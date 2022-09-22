# author: Shayan Hemmatiyan
import os
import shutil
from PIL import Image
import sys
sys.path.append("./src")
from src.generate import Generate
from src.annotate import Annotate
import cv2
from flask import (
    Flask,
    flash,
    request,
    render_template,
    redirect,
    url_for,
    session,
    jsonify,
    send_from_directory,
    send_from_directory,
    send_file,
)
import uuid
import logging
import glob
import shutil
from pdf2image import convert_from_path
app = Flask(__name__,static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
import numpy as np
from pathlib import Path
import img2pdf

from werkzeug.exceptions import HTTPException
from collections import OrderedDict
UPLOAD_FOLDER = os.path.basename(".") + "/static/tmp/upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = os.path.basename(".") + "/static/tmp/download"
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
ZIP_FOLDER = os.path.basename(".") + "/static/tmp/zip"

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


        



# Secret key for sessions encryption
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
__author__ = "Shayan Hemmatiyan <shemmatiyan@gmail.com>"
__source__ = ""
# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)
logging.getLogger("werkzeug").setLevel(logging.DEBUG)
LOGGER = logging.getLogger(__name__)




def mk_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def upload_folder(uid):
    return os.path.join(UPLOAD_FOLDER, uid)


def download_folder(uid):
    return os.path.join(DOWNLOAD_FOLDER, uid)


def zip_folder(uid):
    return os.path.join(ZIP_FOLDER, uid)


def remove_tmp():
    try:
       shutil.rmtree(os.path.basename(".") + "/static/tmp")
    except Exception as e:
        LOGGER.info(f"tmp file does not exist {e}")
        

def make_tmp_dirs(uid):
    LOGGER.info("making tmp dirs for uid: " + uid)
    for path in [os.path.basename(".") + "/static/tmp",
        os.path.basename(".")+"/static/tmp/download",
        os.path.basename(".")+"/static/tmp/upload"]:
        mk_dir(path)

    if not os.path.exists(download_folder(uid)):
        mk_dir(download_folder(uid))

    if not os.path.exists(upload_folder(uid)):
        mk_dir(upload_folder(uid))
    return download_folder(uid), upload_folder(uid)



def remove_space(text):
    new_text = "".join([x for x in text.split(" ") if x!=""])
    return new_text

def remove_tmp_dirs(uid):
    try:
        shutil.rmtree(upload_folder(uid))
        shutil.rmtree(download_folder(uid))
    except Exception as e:
        LOGGER.error(f"Error while removing tmp dirs: {e}")

def fileType(fileName):
    fileName = fileName.replace("\\", "/")
    return (str(fileName.split("/")[-1]).split(".")[-1]).lower()


def fileName(filePath):
    filePath = filePath.replace("\\", "/")
    return str(filePath.split("/")[-1]).split(".")[0]



@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return jsonify(error='error', code=500)


@app.route("/")
def home():
    app.config["head"]=0
    app.config["LABELS"] = []
    remove_tmp()
    for path in [os.path.basename(".") + "/static/tmp",
        os.path.basename(".")+"/static/tmp/download",
        os.path.basename(".")+"/static/tmp/upload"]:
        mk_dir(path)
        
    return render_template("index.html", title="LiquidX Document Generator")
    # redirect('/generator', code=302)


@app.route("/health")
def health():
    LOGGER.info("Application is running successfully!")
    return "App is Running!"

@app.route('/generate',methods = ['GET', 'POST'])
def generate():
    LOGGER.info(f"request type: {request.method}")
    if request.method == 'POST':
        LOGGER.info("received post request")
        uid = str(uuid.uuid4())
        LOGGER.info("generated uid: " + uid)
        proc = request.form.get("proc")
        app.config["proc"] = proc
        font_size= request.form.get("font_size")
        bg = request.form.get("bg")
        app.config["font_size"]= font_size
        app.config["bg"]= bg
        app.config["classes"]=OrderedDict()
        app.config["counter"] = 0
        app.config["download_folder"],app.config["upload_folder"] =  make_tmp_dirs(uid)
        file = request.files.get("file")
        # LOGGER.info("file: ", file)
        if not file:
            msg = "file was not uploaded"
            remove_tmp()
            LOGGER.error(msg)
            return jsonify(message=msg), 400
        pdf = os.path.join(upload_folder(uid), file.filename)
        file.save(pdf)
     
        # app.config["download_folder"] = str(download_folder(uid))
        df = app.config["download_folder"]
        # files = request.files.getlist("file")
        LOGGER.info(f"download folder: {df}")
        
        # app.config["upload_folder"]=str(upload_folder(uid))
        img_paths = [str(upload_folder(uid) + "/" + file.filename)]
        for img_path in img_paths:
            pages = convert_from_path(img_path,200)
        # Counter to store images of each page of PDF to image
        image_counter = 1
        # Iterate through all the pages stored above
        doc_names = []
        imgslst = []
        files =[]
        for page in pages:
            image = np.array(pages[image_counter-1])[:, :, ::-1]
            imgslst.append(image)    
            # get pixel at position y=10, x=15
            # where pix is an array of R, G, B.
            # e.g. pix[0] is the red part of the pixel
            #pix = image[10,15]
            
            # Declaring filename for each page of PDF as JPG
            doc_name = os.path.join(
                app.config["download_folder"],
                "page"
                + str(image_counter)
                # + "_"
                # + remove_space(str(fileName(file.filename)))
                + ".png",
            )
            files.append(doc_name)
            # Save the image of the page in system
            page.save(doc_name, "png")
            # Increment the counter to update filename
            image_counter = image_counter + 1
        cv2imgs = np.array(imgslst)
        del imgslst
        app.config["FILES"] = files
        
      
    else:
        files=[]
        app.config["download_folder"] = "./"
        app.config["FILES"] = files
    return redirect('tagger', code=302)
 
 


@app.route('/tagger')
def tagger():
    df =app.config["download_folder"]
    LOGGER.info(f"download_folder: {df}")
    if (app.config["HEAD"] == len(app.config["FILES"])):
        app.config["HEAD"] = 0
        return redirect(url_for('final'))
    try:
        directory = app.config["download_folder"].replace("\\","/")
        print("directory", directory)
        
        # directory = directory.replace("./static/", "/")
        print("Does directory exist? ",os.path.exists(directory))
        if not os.path.exists(directory):
            return jsonify(error="directory does not exist!", code= 305)
        image = app.config["FILES"][app.config["HEAD"]].replace("\\","/")
        
        image = fileName(image) +"."+image.split(".")[-1]
        print("image", image)
        file_ = directory+"/"+image
        file_path = directory.replace("./static/", "/") +"/"+image
        print("Does image exist?", os.path.exists(file_))
        if not os.path.exists(file_):
            return jsonify(error="image does not exist!", code= 305)
        labels = app.config["LABELS"]
        print("labels", labels)
        not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
        print("Is it the last page?",  not not_end)
        print("file_path", file_path)
    except Exception as e:
        remove_tmp()
        app.config["HEAD"] = 0 
        LOGGER.info(f"error with tagger: {e}")
       

    return render_template('tagger.html', not_end=not_end, directory=directory,\
         image_name=image,file_path= file_path,  labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]),code=305)

@app.route('/next')
def next():
    try:
        image = app.config["FILES"][app.config["HEAD"]]
        img = cv2.imread(image)
        hi, wi = img.shape[:2]
        new_img = img.copy()
        download_f = app.config["download_folder"]
        app.config["HEAD"] = app.config["HEAD"] + 1
        if app.config["proc"] =="a":
            annotat_file = str(download_f)+"/"+str(fileName(image)+".txt")
            if not os.path.exists(str(download_f)+"/"+str(fileName(image))+".txt"):
                with open(str(download_f)+"/"+str(fileName(image))+".txt", "w") as f:
                    print(f"file name {annotat_file}") 
        with open(app.config["OUT"],'a') as f:
            for label in app.config["LABELS"]:
                bb = [[round(float(label["xMin"])), round(float(label["yMin"]))],
                    [round(float(label["xMax"])), round(float(label["yMax"]))]]
                print("bb", bb)
                if app.config["proc"] =="g":
                    new_img = Generate(new_img, image, download_f, bb,str(label["name"]), app.config["bg"],app.config["font_size"]).gen()
                    f.write(image + "," +
                    label["id"] + "," +
                    label["name"] + "," +
                    str(round(float(label["xMin"]))) + "," +
                    str(round(float(label["xMax"]))) + "," +
                    str(round(float(label["yMin"]))) + "," +
                    str(round(float(label["yMax"]))) + "\n")
                else:
                    if label["name"] not in [*app.config["classes"]]:
                        app.config["classes"][label["name"]] = str(app.config["counter"])
                        app.config["counter"]+=1
                    line = Annotate(label, app.config["classes"][label["name"]],hi, wi).annot()
                    with open(str(download_f)+"/"+str(fileName(image))+".txt", "a+") as f:
                        f.writelines(f"{line}\n")
        if app.config["proc"] =="g":     
            cv2.imwrite(str(download_f)+"/gen_"+str(fileName(image) +".png"), new_img)
            del new_img
        else:
            with open(str(download_f)+"/classes"+".txt", "w") as f:
                for obj in [*app.config["classes"]]:
                    f.writelines(f"{obj}\n")

    except Exception as e:
        remove_tmp()
        app.config["HEAD"] = 0 
        LOGGER.info(f"error with tagger: {e}")
    #cv2.imwrite("fig.png", new_img)
    app.config["LABELS"] = []
    
    return redirect('tagger')

@app.route("/final")
def final():
    app.config["HEAD"] = 0
    return render_template('final.html')

@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    bb = [[xMin, yMin],[xMax, yMax]]

    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config["download_folder"]
    return send_file(images +'/'+f)

# @app.route('/static/<filename>')
# def display_image(filename):
#     print('display_image filename: ' + filename)
#     return redirect(url_for('static', filename= filename), code=301)


@app.route('/download')
def download():
    mk_dir("images")
    # shutil.copyfile('out.csv', 'images/annotations.csv')
    if app.config["proc"] =="g": 
        for file_ in glob.glob(os.path.join(app.config["download_folder"], "gen*")):
            shutil.copy(file_,"images/"+fileName(file_)+".png" )

        with open("images/gen.pdf", "wb") as f:
            f.write(img2pdf.convert(["images/"+str(i) for i in sorted(os.listdir("images/")) if i.endswith(".png")]))
    else:
        for file_ in glob.glob(os.path.join(app.config["download_folder"], "*.txt")):
            shutil.copy(file_,"images/"+fileName(file_)+".txt" )
        for file_ in glob.glob(os.path.join(app.config["download_folder"], "*.png")):
            shutil.copy(file_,"images/"+fileName(file_)+".png" )

    
        
    try:
        shutil.make_archive('final', 'zip', 'images')
        shutil.rmtree(app.config["download_folder"])
        shutil.rmtree(app.config["upload_folder"])
        shutil.rmtree("images")
    except Exception as e:
        remove_tmp()
        app.config["HEAD"] = 0
        LOGGER.info(f"Error with download: {e}")
        return jsonify(f"error:{e}"), 402
    return send_file('final.zip',
                     mimetype='text/csv',
                     attachment_filename='final.zip',
                     as_attachment=True)

if __name__ == "__main__":
    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["OUT"] = "out.csv"   
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080,  use_reloader=True)
    # app.run(host='0.0.0.0', debug="True",use_reloader=True)
