import os
from tempfile import NamedTemporaryFile

from flask import Flask, request, flash, jsonify

from api.cajparser import CAJParser

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, World!'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'caj'}


def create_temporary_file(file):
    # 创建一个临时文件
    temp = NamedTemporaryFile(delete=False)
    file.save(temp.name)
    return temp.name


@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    # 如果用户没有选择文件，浏览器可能会提交一个没有文件名的空部分

    filename = file.filename
    output_name = ""

    if filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        temp_file_path = create_temporary_file(file)
        caj = CAJParser(temp_file_path)

        if filename.endswith(".caj"):
            output_name = file.filename.replace(".caj", ".pdf")
        elif (len(output_name) > 4 and (filename[-4] == '.' or filename[-3] == '.') and not filename.endswith(
                ".pdf")):
            output_name = os.path.splitext(filename)[0] + ".pdf"
        else:
            output_name = filename + ".pdf"

        caj.convert(output_name)
        print("done")
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400
