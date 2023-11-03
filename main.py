import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import json
import jsonify
import os
import time
import malaya_speech

from flask import *
from werkzeug.utils import secure_filename

app = Flask(__name__)

stt = malaya_speech.stt.deep_transducer()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'm4a'}

UPLOAD_FOLDER = r'C:\Users\Harold Harrison\Downloads\vr_speech_learning'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home_page():
    data_set = {'Page': 'Home', 'Message': 'Successfully loaded the home page', 'Timestamp': time.time()}
    json_dump = json.dumps(data_set)
    return json_dump


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')
    errors = {}
    success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500

    if success:
        resp = transcribe_audio(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    else:
        resp = jsonify(errors)
        resp.status_code = 500

    # print(resp[0])
    return resp[0]


def transcribe_audio(path):
    extension = os.path.splitext(path)[1]
    if extension != '.wav':
        path = convert_file(path)

    y, sr = malaya_speech.load(path)
    text = stt.greedy_decoder([y])
    os.remove(path)
    return text


def convert_file(file):
    filename_no_ex = os.path.splitext(file)[0]
    new_filename = filename_no_ex + ".wav"
    sound = AudioSegment.from_file(file, format='m4a')
    sound.export(new_filename, format='wav')
    os.remove(file)
    return new_filename


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
