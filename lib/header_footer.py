import sys
import time

def header( rel_path, cache_css, scripts, home=None, other='' ) :

    add_string = ''
    if not cache_css:
        add_string = '?' + str( time.time() )
    
    out_string =  "Content-type: text/html; charset=utf-8\n\n" 
    out_string += """
        <!DOCTYPE html>
        <head>
        <title>The Idio-Matic</title>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        <link href="https://fonts.googleapis.com/css2?family=Ewert&family=Poppins" rel="stylesheet">
        <link rel="stylesheet" type="text/css" """ + 'href="' + rel_path + 'css/style.css' + add_string + '">' + """
        <link rel="icon" type="image/x-icon" href="favicon.svg">
        <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
        <script type='text/javascript'> """ + scripts + """ </script>
        """ + other + """            
        </head>

        <body>

        <div class="content">
        <div class="header"> """ 

    if home is None : 
        out_string += '<a href="./"> The Idio-Matic</a>'
    else :
        out_string += '<a href="' + home + '">The Idio-Matic</a>' 

    out_string += """
        </div> <!--header  -->
        <!-- End of header section -->
        """
    
    sys.stdout.buffer.write( out_string.encode( 'utf-8' ) )



def footer( rel_path ) : 
    sys.stdout.buffer.write( b"""
        <!-- Footer -->
        </div> <!--content -->

        </body>
        </html>
    """)

    
