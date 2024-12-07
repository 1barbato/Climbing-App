import flask
from flask import request, jsonify, send_from_directory, url_for
from flask_restful import Api, Resource
import config
from pymongo import MongoClient, errors
import os
import logging
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)
api = Api(app)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
boulders = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads') #temp dir to hold uploaded files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET"])
@app.route("/index", methods=['GET'])
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('index.html')

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
    media_file = request.files.get('boulder_media')
    if not media_file:
        print('no media file found in request')

    if not name or not grade:
        return jsonify({"error": "Missing required fields"}), 400

    media_url = None

    filename = secure_filename(media_file.filename)

    if media_file:
        #media_filename = os.path.join(UPLOAD_FOLDER, media_file.filename)
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"saving file to {media_path}")

        try:
            media_file.save(media_path)
            print(f'file saved successfully: {media_path}')
        except Exception as e:
            print(f'error saving file: {e}')
            return 'file save failed', 500
    
    media_url = url_for('uploaded_file', filename=filename)

    response_data = {
        'id': len(boulders) + 1,
        'name': name,
        'grade': grade,
        'media_url': media_url
        }
    boulders.append(response_data)
    
    #return jsonify(response_data), 200
    return flask.redirect(url_for('index'))
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/boulders', methods=['GET'])
def show_boulders():
    return flask.render_template('boulders.html', boulders=boulders)

app.debug = True
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=5000, host="0.0.0.0")