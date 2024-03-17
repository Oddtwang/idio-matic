#!/usr/bin/python3

import os
import sys
import time

lib_dir = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "lib")
sys.path.append( lib_dir )

from config        import config
from header_footer import header, footer

rel_path = ''

scripts = """

    $( document ).ready(function() {
    
        $(".stype-button").click( function( event ) {
            event.preventDefault();
            var stype = $(this).attr('sessionType');
            window.location.href = 'idio-matic.py?stype=' + stype ;
            return false;
        });

    });
        
    """


header( rel_path, config()[ 'cache_css' ], scripts )

# LIVE BUTTON HIDDEN AS NOT IMPLEMENTED

out_string = """
    <div class="index-login" > 
        <div id="show-error" class="login-errors">
            Session ID error. Please refresh and try again.
        </div>
        
    Select session type:<br><br>

    <form id="typeSelection">
        <button class="ui-button ui-widget ui-corner-all stype-button" id=button_static sessionType="static" >Static</button> 
        <button hidden /*class="ui-button ui-widget ui-corner-all stype-button"*/ id=button_live   sessionType="live" >Live</button>
    </form>

    <div id="tmpTest"></div>

    </div> <!--index-login-->

    """


sys.stdout.buffer.write( out_string.encode( 'utf-8' ) )

footer( rel_path ) 

