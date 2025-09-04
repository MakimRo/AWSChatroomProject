from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import datetime
import pymysql
from werkzeug.utils import secure_filename

# Initialize flask app
app = Flask(__name__)
app.config["FILE_FOLDER"] = "./images"
os.makedirs("/images", exist_ok=True)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowedfile(filename):
    print(filename.rsplit(".", 1)[1].lower(), file = sys.stderr)
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    
@app.route("/upload", methods = ["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"Error":"No File"}), 400
    
    file = request.files["file"]
    print(file, file = sys.stderr)
    if file.filename == "":
        return jsonify({"Error":"No Selected File"}), 400
    
    
    if file and allowedfile(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["FILE_FOLDER"], filename)   
        print(file.filename, file = sys.stderr)
        print(file_path, file = sys.stderr)
        file.save(file_path)
        return jsonify({"Message":"File uploaded successfully", "filename": file.filename}), 200
    else:
        return jsonify({"Error": "Invalid File Type"}), 400
    

@app.route("/upload/<filename>", methods = ['GET'])
def get_image(filename):
    try:
        return send_from_directory(app.config["FILE_FOLDER"], filename)
    except:
        return 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
