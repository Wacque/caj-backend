import os
from os.path import join
from tempfile import NamedTemporaryFile
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file, after_this_request, send_from_directory

from api.cajparser import CAJParser
from api.config import FILE_WRITE_PATH

app = Flask(__name__, static_folder='../front', static_url_path='')
CORS(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'caj'}


def create_temporary_file(file):
    # 创建一个临时文件
    temp = NamedTemporaryFile(delete=False)
    file.save(temp.name)
    return temp.name


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


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
        output_path = FILE_WRITE_PATH + output_name

        # 注册清理函数
        @after_this_request
        def remove_file(response):
            os.remove(output_path)
            return response

        # response file and remove file
        return send_file(output_path, as_attachment=True)
    else:
        return jsonify({'error': 'File type not allowed'}), 400
