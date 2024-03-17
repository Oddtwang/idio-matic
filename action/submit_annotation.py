#!/usr/bin/python3

import os
import sys

sys.stdout.buffer.write( b"Content-type: text/html\n\n" )

base_path  = '../'
utils_path = os.path.join( os.path.dirname( os.path.realpath(__file__) ), base_path + "utils")
sys.path.append( utils_path )

from MyMySQL import MyMySQL

mysql_obj = MyMySQL(config_path=utils_path)

from contextlib import redirect_stderr


## This import must be after MySQL
import cgi

debug = True
testdata = False

form     = cgi.FieldStorage()

# Passed in:

## Session ID
## MWE ID
## Sentence ID
## Annot by
## Labels (true, selected) -> for computing correctness
## Explanation  (defaults to empty for human or if not generated)
## Correct (to compute)

sid    = None
mid    = None
sentid = None
annot_by = None
true_label = None
annot_label = None
explanation = None

if debug:

    err_dest = open('../idio-matic.log', 'a')

else:
    err_dest = sys.__stderr__

with err_dest as stderr, redirect_stderr(stderr):

    sys.stderr.write( 'submit_annotation.py called')
    sys.stderr.write('\n')

    if not testdata :

        sys.stderr.write( ' Data (raw):')
        sys.stderr.write('\n')
        sys.stderr.write( str(form))
        sys.stderr.write('\n')
        sys.stderr.write( str(form[ 'sid'].value))
        sys.stderr.write('\n')
        
        try :
            sid             = form[ 'sid' ].value
            mid             = form[ 'mid'  ].value
            sentid          = form[ 'sentid'  ].value
            annot_by        = form[ 'annot_by' ].value
            true_label      = form[ 'true_label'  ].value
            annot_label     = form[ 'annot_label'  ].value
            explanation     = form[ 'explanation' ].value
            
        except KeyError as e:
            print( "Error", e )
            sys.exit()


    if testdata :
        sid             = 1
        mid             = 1
        sentid          = 1
        annot_by        = "Gemini1.0"
        true_label      = "Idiomatic"
        annot_label     = "Idiomatic"
        explanation     = """"Eager beaver" is an idiom used to describe someone who is enthusiastic and hardworking. In the given sentence, it is used to describe someone who worked all night on a report, not a literal beaver."""


    sys.stderr.write( ' Data:' )
    sys.stderr.write('\n')
    sys.stderr.write(' sid ')
    sys.stderr.write(str(sid))
    sys.stderr.write(' | mid ')
    sys.stderr.write(str(mid))
    sys.stderr.write(' | sentid ')
    sys.stderr.write(str(sentid))
    sys.stderr.write(' | annot_by ')
    sys.stderr.write(annot_by)
    sys.stderr.write(' | true_label ')
    sys.stderr.write(true_label)
    sys.stderr.write(' | annot_label ')
    sys.stderr.write(annot_label)
    sys.stderr.write(' | explanation ')
    sys.stderr.write(explanation)
    sys.stderr.write('\n')

    if true_label == annot_label:
        correct = 1

        sys.stderr.write( ' Labels match - correct' )
        sys.stderr.write('\n')
    else:
        correct = 0

        sys.stderr.write( ' Labels do not match - incorrect' )
        sys.stderr.write('\n')


    payload  = ( int( sid ), int( mid ), int( sentid ), annot_by, annot_label, explanation, correct ) 
    query    = 'INSERT INTO annotations( session_id, mwe_id, sent_id, annot_by, label, explanation, correct ) VALUES ( %s, %s, %s, %s, %s, %s, %s )'

    temp_save = os.path.join( utils_path, 'Cache' )
    temp_save = os.path.join( temp_save , str(sid) + "_" + str( mid ) + "_" + str( sid ) + ".pk" )

    try : 
        sys.stderr.write( " ".join( [str( query ),str( sid ),str( mid ),str( sentid ),annot_by, annot_label, explanation, str( correct ) ] ) )
        sys.stderr.write('\n')

        with open( temp_save, 'w' ) as fh:
            #pickle.dump( data, fh )
            fh.write(annot_by)
            fh.write('\n')
            fh.write(annot_label)
            fh.write('\n')
            fh.write(explanation)
            fh.write('\n')
    except :
        sys.stderr.write( ' Temp save error' )
        sys.stderr.write('\n')

        pass

    try : 
        sys.stderr.write( ' Running SQL insert' )
        sys.stderr.write('\n')

        cursor = mysql_obj.mysql_connection.cursor()
        cursor.execute(query, payload )
        cursor.close()
        mysql_obj.mysql_connection.commit()
    except : 
        sys.stdout.buffer.write( " ".join( [str( query ),str( sid ),str( mid ),str( sentid ),annot_by, annot_label, explanation, str( correct ) ] ).encode( 'utf-8' ) )
        sys.exit()

    # time.sleep( 3 );
    sys.stdout.buffer.write( str( "Success" ).encode( 'utf-8' ) ) 

    sys.exit()