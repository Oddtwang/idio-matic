#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from random import shuffle
from contextlib import redirect_stderr

lib_dir = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "lib")
sys.path.append( lib_dir )

from config        import config
from header_footer import header, footer

utils_path = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "utils")
sys.path.append( utils_path )

from MyMySQL import MyMySQL

mysql_obj = MyMySQL(config_path=utils_path)

## This import must be after MySQL
import cgi

######

def _generate_session_id():

    # Insert session datetime into sessions table; auto-incremented ID generated
    query = """INSERT INTO sessions (session_id, timestamp)
               VALUES ( NULL, NOW() )
               ;
            """
    
    mysql_obj.mysql_do( query )
    
    # Retrieve inserted ID

    retrieve = """SELECT LAST_INSERT_ID();"""

    return mysql_obj.mysql_get( retrieve )[0][0]


def _get_possible_mwes( sid ):

    # Pull MWEs
     # Exclude any annotated this session

    query = """SELECT mwe_id, mwe
                FROM mwes
                WHERE mwe_id NOT IN ( SELECT DISTINCT mwe_id
                                      FROM annotations
                                      WHERE session_id = """ + str(sid) + """
                                      )
                ;
            """
    
    results = list( reversed( mysql_obj.mysql_get( query ) ) )
    results = [ [ i[0], i[1].encode("utf-8").decode() ] for i in results ]

    return results


def _get_model_annotations( mid , sentid = None):

    # Pull all non-human annotations for this MWE

    query = """SELECT sent_id, label, correct, explanation
                FROM annotations
                WHERE mwe_id = """ + str(mid) 
    
    if sentid:
        query += """
                AND sent_id = """ + str( sentid )
                
    query += """
                AND annot_by <> "Human"
                ;
            """
    
    results = list( reversed( mysql_obj.mysql_get( query ) ) )
    results = [ [ i[0], i[1].encode("utf-8").decode(), i[2], i[3].encode("utf-8").decode() ] for i in results ]

    return results



def _get_all_sentences( mid ):

    # Pull all sentences for this MWE

    query = """SELECT sent_id, sentence, label
                FROM sentences
                WHERE mwe_id = """ + str(mid) + """
                ;
            """
    
    results = list( reversed( mysql_obj.mysql_get( query ) ) )
    results = [ [ i[0], i[1].encode("utf-8").decode(), i[2].encode("utf-8").decode() ] for i in results ]

    return results


def _get_sentence( sentid ):

    # Pull a specific sentence

    query = """SELECT sentence, label
                FROM sentences
                WHERE sent_id = """ + str(sentid) + """
                ;
            """
    
    results = list( reversed( mysql_obj.mysql_get( query ) ) )
    results = [ [ i[0].encode("utf-8").decode(), i[1].encode("utf-8").decode() ] for i in results ]

    return results


def _get_mwe( mid ):

    # Pull a specific sentence

    query = """SELECT mwe
                FROM mwes
                WHERE mwe_id = """ + str(mid) + """
                ;
            """
    
    results = list( reversed( mysql_obj.mysql_get( query ) ) )
    results = [ [ i[0].encode("utf-8").decode() ] for i in results ]

    return results[0]


######



rel_path = ''

debug = False

if debug:

    err_dest = open('idio-matic.log', 'a')

else:
    err_dest = sys.__stderr__


with err_dest as stderr, redirect_stderr(stderr):


    # Check for session type
    stype = None

    try : 
        form = cgi.FieldStorage()
        stype  = form[ 'stype' ].value
        if debug:
            sys.stderr.write( 'Session type found: ' + stype )
            sys.stderr.write('\n')

    except :
        sys.stderr.write( 'Session type NOT found' )
        sys.stderr.write('\n')

        meta = '<meta http-equiv="refresh" content="0;url=./" />'
        header( rel_path, config()[ 'cache_css' ], '', None )
        print ( """
            <div class="login-errors" style="display:block; margin:auto;margin-top:10px">
                Something went wrong. Please <a href="./">start a new session</a>.
            </div>
            """ )
        footer( rel_path ) 

        sys.exit()



    # Generate a session ID if not already set
    if not 'sid' in list( form.keys() ) :
        if debug:
            sys.stderr.write( 'No session ID - generating ') 
            sys.stderr.write('\n')

        sid = _generate_session_id()
        if debug:
            sys.stderr.write( 'Generated session ID: ' + str(sid))
            sys.stderr.write('\n')
        # Don't think we need to refresh, as no display change or user input

    else:
        sid  = form[ 'sid' ].value
        if debug:
            sys.stderr.write( 'Session ID passed: ' + str(sid))
            sys.stderr.write('\n')


    # If MWE ID and sentence ID passed, don't want to choose new ones - just fetch existing data  
    if ('mid' in list( form.keys() )) and ('sentid' in list( form.keys() )):
        form = cgi.FieldStorage()
        sentid = form[ 'sentid' ].value
        mid    = form[ 'mid' ].value

        if debug:
            sys.stderr.write( 'MWE ID and sentence ID passed: ' + str(mid) +', ' + str(sentid) )
            sys.stderr.write('\n')

        # Pull corresponding sentence, label, MWE
        if debug:
            sys.stderr.write( 'Fetching MWE, sentence')
            sys.stderr.write('\n')

        sentence, true_label = _get_sentence( sentid )[0]
        mwe = _get_mwe( mid )[0]
        


    else:
        # Pull MWEs
            # Excludes any annotated this session
        if debug:
            sys.stderr.write( 'Getting possible MWEs for annotation ')
            sys.stderr.write('\n')

        possible_mwes = _get_possible_mwes( sid )

        if len(possible_mwes) == 0:
            if debug:
                sys.stderr.write( 'No MWEs available to annotate')
                sys.stderr.write('\n')
            # If none left, want to invite to go back to the start
            meta = '<meta http-equiv="refresh" content="0;url=./" />'
            header( rel_path, config()[ 'cache_css' ], '', None  )
            print ( """
                <div class="ann-sentence-samples" style="display:block; margin:auto;margin-top:10px">
                    All available expressions annotated. Please <a href="./">return to the landing page</a> to start a new session.
                </div>
                """ )
            footer( rel_path )

            sys.exit()

        else:
            # Pick a random MWE
            shuffle(possible_mwes)
            mid, mwe = possible_mwes[0]

            if debug:
                sys.stderr.write( 'Random MWE selected: ' + str(mwe)  + ', ' + str(mid) )
                sys.stderr.write('\n')



        # If session type is STATIC:
        if stype == "static":

            if debug:
                sys.stderr.write( 'Session type STATIC')
                sys.stderr.write('\n')

            # Pull all non-human annotations for this MWE
            all_annotations = _get_model_annotations( mid )
        
            # If none, all sentences available - set model info to a default
            if len(all_annotations) == 0:
                if debug:
                    sys.stderr.write( 'No LLM annotations fetched - picking a random sentence ')
                    sys.stderr.write('\n')

                model_label = -1
                model_correct = -1
                model_explanation = ""

                # Choose any sentence for this MWE
                all_sentences = _get_all_sentences( mid )

                shuffle(all_sentences)
                sentid, sentence, true_label = all_sentences[0]
                if debug:
                    sys.stderr.write( 'Random sentence selected: ' + str(sentid) + ' | '+ sentence + ' | ' + str(true_label))
                    sys.stderr.write('\n')
            

            else:
                # Pick a random annotation from among them
                if debug:
                    sys.stderr.write( 'LLM annotations found')
                    sys.stderr.write('\n')
                shuffle(all_annotations)
                sentid, model_label, model_correct, model_explanation = all_annotations[0]
        
                # Pull corresponding sentence
                sentence, true_label = _get_sentence( sentid )[0]
                if debug:
                    sys.stderr.write( 'Sentence ID selected with label: ' +str(sentid) + ' | '+ sentence + ' | ' + str(true_label))
                    sys.stderr.write('\n')



        elif stype == "live":
            if debug:
                sys.stderr.write( 'Session type LIVE')
                sys.stderr.write('\n')
        # If LIVE:
            # Construct prompt
            # Submit to Gemini API
            #  Possibly retry?
            # Capture response
            # If valid, write to annotations table

            pass

        

        else:
            # Shouldn't hit this!
            sys.stderr.write( 'Session type INVALID! ')
            sys.stderr.write('\n')

            meta = '<meta http-equiv="refresh" content="0;url=./" />'
            header( rel_path, config()[ 'cache_css' ], '', None, meta )
            print ( """
                <div class="login-errors" style="display:block; margin:auto;margin-top:10px">
                    Something went wrong. Please <a href="./">start a new session</a>.
                </div>
                """ )
            footer( rel_path ) 

            sys.exit()



    #####
        
    # Check if item has just been annotated
    if 'annot' in list( form.keys() ) :
        annot  = form[ 'annot' ].value
        if debug:
            sys.stderr.write( 'Annotation value passed: ' + annot)
            sys.stderr.write('\n')
        
    else:
        annot = 'x'


    if annot == 'x':
        if debug:
            sys.stderr.write( 'No annotation value set. ')
            sys.stderr.write('\n')

        scripts = """

        $( document ).ready(function() {
        
            $( ".annot_button" ).click(function( event ) {
                event.preventDefault();

                $("#submit_results").html('<div style="margin: 30px; text-align: center; font-size: 24px; color: #eb5600; ">Saving ...</div>');

                var annot_label = $(this).attr('annot_label');
                var annot = $(this).attr('annot');

                $.ajax({
                    type: 'post',
                    url: '""" + rel_path + """/action/submit_annotation.py',
                    data: { 
                            'sid'  : """ + str( sid ) + """,
                            'mid'  : """ + str( mid ) + """,
                            'sentid'  : """ + str( sentid ) + """,
                            'annot_by': 'Human',
                            'true_label' : '""" + str( true_label ) + """',
                            'annot_label': annot_label,
                            'explanation': ' '
                        }, 
                    success: function ( response ) {
                        if( response == 'Success' ) { 
                        window.location.href='idio-matic.py?sid=""" + str( sid ) + """&mid=""" + str( mid ) + """&sentid=""" + str( sentid ) + """&stype=""" + str( stype ) + """&annot=' + annot ;
                        } else {
                        $( '#tmpTest' ).html( "ERROR SAVING DATA!<br>" + response );
                        }
                    }
                });

            });

        });

        """


        home  = './idio-matic.py' + '?sid=' + str( sid ) + '&mid=' + str( mid ) + '&sentid=' + str( sentid ) + "&stype=" + str( stype )
        header( rel_path, config()[ 'cache_css' ], scripts, home )
    
        # Display sentence, MWE to user

        out_str = '<div class="ann-sentence-samples">'
        out_str += """<p style="font-size:20pt;">In the following sentence, how is the expression '<b>""" + mwe + """</b>' used?</p>"""
        out_str += "<br>"
        out_str += sentence
        out_str += '</div>'

        # 3 buttons (idiomatic, literal, other/don't know)
        # Button click: record response, write to annotations table.  Call page again, passing sid, mid, sentid, stype, annot

        out_str += """
            <div id="submit_results">
                <form id="submitAnnotation">
                    <button class="ui-button ui-widget ui-corner-all annot_button" id=submit_idiomatic annot_label="Idiomatic" annot="i">Idiomatically</button> 
                    <button class="ui-button ui-widget ui-corner-all annot_button" id=submit_literal annot_label="Literal" annot="l">Literally</button> 
                    <button class="ui-button ui-widget ui-corner-all annot_button" id=submit_other annot_label="Other" annot="o">Other / Unclear</button> 
                </form>

                <div id="tmpTest"></div>
            </div>
        
        """

        sys.stdout.buffer.write( out_str.encode( 'utf-8' ) )

        footer( rel_path )

    # User has submitted an annotation
    else:
        if debug:
            sys.stderr.write( ' Annotation done - compare with model response ')
            sys.stderr.write('\n')

        # Annotation has been done - want to compare with model response

        # "Continue" button - effectively reload page, with same session ID + type
        # "End session" button - return to index
        scripts = """

            $( document ).ready(function() {
            
                $( ".continue-button" ).click(function( event ) {
                    event.preventDefault();

                    window.location.href='idio-matic.py?sid=""" + str( sid ) + """&stype=""" + str( stype ) +"""';
                    
                });

                $( ".end-button" ).click(function( event ) {
                    event.preventDefault();

                    window.location.replace('index.py');

                });

            });

            """

        home  = './idio-matic.py' + '?sid=' + str( sid ) + '&mid=' + str( mid ) + '&sentid=' + str( sentid ) + "&stype=" + stype + "&annot=" + annot
        header( rel_path, config()[ 'cache_css' ], scripts, home )

        # Present model response & explanation, correct label, compare notes

        #  Fetch model annotation (pick any for this sentence, mwe)

        model_annotations = _get_model_annotations( mid , sentid = sentid)
        shuffle(model_annotations)

        _, model_label, model_correct, model_explanation = model_annotations[0]


        # Display sentence, MWE to user

        out_str = '<div class="ann-sentence-compare">'
        out_str += """<p style="font-size:18pt;">Let's compare annotations for the expression '<b>""" + mwe + """</b>' in this sentence:"""
        out_str += "<br><br>"
        out_str += sentence
        out_str += "</p>"

        if annot == 'o':
            out_str += "You gave a label of <b>Other / Unclear</b>.<br>"

        elif annot == 'i':
            out_str += "You labelled the expression as <b>Idiomatic</b>.<br>"

        elif annot == 'l':
            out_str += "You labelled the expression as <b>Literal</b>.<br>"


        out_str += "The 'true' label we have recorded is: <b>" + true_label + "</b>.<br>"

        out_str += """<p style="color: #eb5600; font-size:18pt;">The Idio-Matic (a Large Language Model trained using large volumes of text from the internet) thought the answer was '<b>""" + model_label + """</b>', and generated the following explanation:</p>"""
        out_str += """<p style="color: #eb5600;">\"""" + model_explanation + """"</p>"""

        if (((true_label == 'Idiomatic') and (annot == 'i')) or ((true_label == 'Literal') and (annot == 'l'))):
            if model_correct:
                out_str += "Looks like you and the Idio-Matic agreed about this one."

            else:
                out_str += "Congratulations! You understood the (possibly) figurative language better than the Idio-Matic!"

        elif annot != 'o':
            if model_correct:
                out_str += "Is there anything about the sentence which is unclear? Or maybe you made different assumptions based on your experience of people using potentially ambiguous language."

            else:
                out_str += "Is there something about the sentence which is potentially misleading?"

        out_str += "<br>Is the model's 'explanation' plausible?<br>"
        out_str += '</div>'
        


        #out_str += '<div class="ann-sentence-compare">'
        out_str += "<br>Thank you for pitting your wits against the <b>Idio-Matic</b>!<br>"
        out_str += "If you'd like to try another, press 'Continue'. Otherwise, please press 'End Session' to return to the homepage.<br><br>"

        # "Continue" button - effectively reload page, with same session ID etc.
        # "End session" button - return to index
        out_str += """
                <form id="endItem">
                    <button class="ui-button ui-widget ui-corner-all continue-button" id=continue>Continue</button> 
                    <button class="ui-button ui-widget ui-corner-all end-button" id=end_session>End Session</button>
                </form>
                """
        #out_str += '</div>'

        sys.stdout.buffer.write( out_str.encode( 'utf-8' ) )

        footer( rel_path )