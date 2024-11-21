import flask
from flask import request, jsonify, send_from_directory
from flask_restful import Api, Resource
import config
from pymongo import MongoClient, errors
import os
import logging

app = flask.Flask(__name__)
api = Api(app)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

UPLOAD_FOLDER = 'static/uploads' #temp dir to hold uploaded files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET"])
@app.route("/index", methods=['GET'])
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('main.html')

@app.route("/my_boulders", methods=["GET"])
def my_boulders():
    app.logger.debug("My Boulders Page Entry")
    return flask.render_template("my_boulders.html")

@app.route("/submit", methods=['GET', 'POST'])
def submit():
    print("form data received:", request.form)
    print("files received:", request.files)
    name = request.form.get('boulder_name')
    grade = request.form.get('boulder_grade')
    media_file = request.files.get('boulder-media')

    if not name or not grade:
        return jsonify({"error": "Missing required fields"}), 400

    media_url = None

    if media_file:
        media_filename = os.path.join(UPLOAD_FOLDER, media_file.filename)
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_filename)
        print(f"saving file to {media_path}")
        media_file.save(media_path)

        if os.path.exists(media_path):
            print(f"File saved successfully: {media_path}")
        else:
            print(f"File save failed: {media_path}")
        media_url = f'/uploads/{media_filename}'
        print(f"generated media url: {media_url}")

    response_data = {
        'name': name,
        'grade': grade,
        'mediaUrl': media_url
        }
    
    return jsonify(response_data), 200
    #return flask.redirect(flask.url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

app.debug = True
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=5000, host="0.0.0.0")