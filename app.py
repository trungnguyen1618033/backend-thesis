import flask
from flask import Flask, request, render_template, jsonify, redirect, url_for
from util import base64_to_pil, np_to_base64
import uuid
import numpy as np
import os
import json
from face_recognition import *
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
import shutil

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


UPLOAD_FOLDER_SEARCH = os.path.join("./search")
UPLOAD_FOLDER_NEW = os.path.join("./new")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def fitler_name(name):
    with open("listCeleb.json") as jsondata:
        data = json.load(jsondata)
    if list(filter(lambda x: x["ten"].lower() == name.lower(), data["celeb"])):
        return True
    return False


def write_json(data, filename="listCeleb.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def new_celeb(name):
    with open("listCeleb.json") as json_file:
        data = json.load(json_file)

        temp = data["celeb"]
        print(len(data["celeb"]))
        # python object to be appended
        y = {
            "stt": str(len(data["celeb"])),
            "ten": name,
            "link": "",
        }

        # appending data to emp_details
        temp.append(y)

    write_json(data)


def mapping_index(name):
    filename = "mapping.txt"
    with open(filename, encoding="utf8") as fh:
        for line in fh:
            (key, val) = line.strip().split(None, 1)
            if val == name:
                # print(val)
                # print(key)
                return key
    return None


def mapping_name(labels):
    filename = "mapping.txt"
    names = []
    links = []
    with open(filename, encoding="utf8") as fh:
        d = {}
        for line in fh:
            (key, val) = line.strip().split(None, 1)
            d[int(key)] = val
    for i, label in enumerate(labels):
        if label == "unknown":
            names.append(label)
        elif int(label) < 731 and int(label) >= 0:
            t = int(label)
            names.append(d[t])
    for i, name in enumerate(names):
        if name == "unknown":
            links.append("")
        else:
            url = (
                "https://www.google.com/search?q="
                + name.replace(" ", "+")
                + "&client=ubuntu&hl=en&source=lnms&tbm=isch&sa=X"
            )
            links.append(url)

    return names, links


def convert_to_json(labels, bboxes, base64):
    dict_json = []
    if labels is None:
        num_face = -1
        dict_json = {
            "num_face": num_face,
            "labels": "",
            "bboxes": "",
            "base64": "",
            "links": "",
        }
        jsonobj = json.dumps(dict_json)
        return jsonobj
    else:
        faces = bboxes.tolist()
        num_face = len(labels)
        names, links = mapping_name(labels)
        # dict_json = {"num_face": num_face}
        for i in range(num_face):
            data = {
                "num_face": i,
                "labels": names[i],
                "bboxes": faces[i],
                "base64": base64[i],
                "link": links[i],
            }
            # print('data', type(data))
            dict_json.append(data)
            # print(dict_json, type(dict_json))
        # print(labels, type(labels))
        # print(names, type(names))
        # print(dict_json, type(dict_json))
        jsonobj = json.dumps(dict_json)
        # print(jsonobj)
        return jsonobj


recognition = FaceRecognition()
app = Flask(__name__)
CORS(app)
# app.secret_key = "secret key"
app.config["UPLOAD_FOLDER_SEARCH"] = UPLOAD_FOLDER_SEARCH
app.config["UPLOAD_FOLDER_NEW"] = UPLOAD_FOLDER_NEW
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        data = {}
        with open("listCeleb.json", encoding="utf-8") as f:
            data = json.load(f)
        f.close
        return data
    #     return render_template("home.html")

    # if request.method == "POST":


@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        if "files[]" not in request.files:
            resp = jsonify({"message": "No file part in the request"})
            resp.status_code = 400
            return resp

        files = request.files.getlist("files[]")

        errors = {}
        success = False

        path = os.listdir(app.config["UPLOAD_FOLDER_SEARCH"])
        name = "search_" + str(len(path))
        path_folder = os.path.join(app.config["UPLOAD_FOLDER_SEARCH"], name)
        try:
            os.mkdir(path_folder)
        except OSError:
            print("Creation of the directory %s failed" % path_folder)
        else:
            print("Successfully created the directory %s " % path_folder)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(path_folder, filename))
                success = True
            else:
                errors[file.filename] = "File type is not allowed"

        if success and errors:
            errors["message"] = "File(s) successfully uploaded"
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            index = request.form["name"]
            name = mapping_index(index)
            # print("name: ", name)
            my_image, base64 = recognition.SearchCeleb(path_folder, name)
            # print(my_image)
            dict_json = []
            for i in range(len(my_image)):
                data = {"image": my_image[i], "base64": base64[i]}
                dict_json.append(data)
            jsonobj = json.dumps(dict_json)
            return jsonobj
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        return None


@app.route("/checkname", methods=["POST"])
def checkname():
    if request.method == "POST":
        print(request.json["name"])
        name = request.json["name"]
        success = fitler_name(name)
        if success:
            resp = jsonify({"message": "Failed"})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({"message": "Success"})
            resp.status_code = 201
            return resp
        return None


@app.route("/new", methods=["POST"])
def new():
    if request.method == "POST":
        if "files[]" not in request.files:
            resp = jsonify({"message": "No file part in the request"})
            resp.status_code = 400
            return resp

        files = request.files.getlist("files[]")

        errors = {}
        success = False

        if len(files) < 5:
            errors["message"] = "File(s) upload less < 5"
            resp = jsonify(errors)
            resp.status_code = 200
            return resp
            return None

        path = os.listdir(app.config["UPLOAD_FOLDER_NEW"])
        name = request.form["name"]

        path_folder = os.path.join(app.config["UPLOAD_FOLDER_NEW"], name)

        if os.path.isdir(path_folder):
            shutil.rmtree(path_folder)
        try:
            os.mkdir(path_folder)
        except OSError:
            print("Creation of the directory %s failed" % path_folder)
        else:
            print("Successfully created the directory %s " % path_folder)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(path_folder, filename))
                success = True
            else:
                errors[file.filename] = "File type is not allowed"

        if success and errors:
            errors["message"] = "File(s) successfully uploaded"
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            result = recognition.DetectFace(path_folder, name)
            if result != True:
                resp = jsonify({"message": result["message"]})
            else:
                new_celeb(name)
                resp = jsonify({"message": "Success"})

            resp.status_code = 201
            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        return None


@app.route("/predict", methods=["GET", "POST"])
def predict():
    # if request.method == "GET":
    #     return render_template("predict.html")

    if request.method == "POST":
        # Get the image from post request
        link_path = "./uploads"
        path = os.listdir(link_path)
        # img = base64_to_pil(request.json["base64"])
        name = "image_" + str(len(path)) + ".jpg"
        file_path = os.path.join(link_path, name)
        # img.save(file_path)
        # print(request.json['base64'],len(request.json["base64"]), type(request.json['base64']))
        if len(request.json["base64"]) > 0:
            print("base65")
            img = base64_to_pil(request.json["base64"])
            img.save(file_path)
        else:
            url = request.json["link"]
            print(url)
            r = requests.get(url)
            with open(file_path, "wb") as f:
                f.write(r.content)
            # urllib.request.urlretrieve(url, file_path)
        labels, bboxes, base64 = recognition.GetLabel(file_path, name)
        jsonobj = convert_to_json(labels, bboxes, base64)

        return jsonobj


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
