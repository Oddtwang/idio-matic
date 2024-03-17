#!/usr/bin/python3

print( "Content-type: text/html\n\n" )

## This import must be after MySQL
import sys
import cgi

form     = cgi.FieldStorage()

try :
    sessionType = form[ 'sessionType' ].value.strip().replace( ' ', '' )
except KeyError:
    print( "False" )
    sys.exit()

if sessionType == "Live":
    stype = "live"

elif sessionType == "Pre-run":
    stype = "static"

else:
    stype = "False"

print( stype )