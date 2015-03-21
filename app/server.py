



import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

import traceback

UPLOAD_FOLDER = r'E:\mabodev\upload\app\files'

ALLOWED_EXTENSIONS = set(['json', 'xls', 'xlsx', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def notify(filename):
    
    print("nofity:%s" % (filename))
    
    
def allowed_file(filename):
    
    val = '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    print("val:%s" %(val) )       
    return val

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            
            #print filename
            
            try:
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                notify(filename)
                
            except Exception as ex:
                
                pass
            
            
            return redirect(url_for('upload_file'))
            #print traceback.format_exc()
        else:
            print("wrong file type")
            
    return '''
    <!doctype html>
    <html>
    <head>
    <title></title>
    </head>
    <body>
    <h1>Upload new File</h1>
    <form action="/upload" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value="Upload">
    </form>
    </body>
    </html>
    '''
    
    
if __name__ == '__main__':
    
    app.run(port=6680)

