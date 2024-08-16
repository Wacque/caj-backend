import os
from tempfile import NamedTemporaryFile

from flask import Flask, request, flash, jsonify, send_file, after_this_request

from api.cajparser import CAJParser
from api.config import FILE_WRITE_PATH

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
    filename = file.filename
    output_name = ""

    if filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        temp_file_path = create_temporary_file(file)
        caj = CAJParser(temp_file_path)

        if filename.endswith(".caj"):
            output_name = filename.replace(".caj", ".pdf")
        elif len(output_name) > 4 and (filename[-4] == '.' or filename[-3] == '.') and not filename.endswith(".pdf"):
            output_name = os.path.splitext(filename)[0] + ".pdf"
        else:
            output_name = filename + ".pdf"

        output_path = caj.convert(output_name)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(temp_file_path)
                os.remove(output_path)
            except Exception as e:
                print(f'Error removing or closing downloaded file handle: {e}')
            return response

        # 返回文件并确保在响应后删除文件
        return send_file(output_path, as_attachment=True)
    else:
        return jsonify({'error': 'File type not allowed'}), 400
