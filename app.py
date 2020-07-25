import logging
import os

from flask import Flask, request, jsonify
from google.cloud import storage

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Configure this environment variable
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


@app.route('/')
def index():
    return """
<form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file"> <br>
    <input type="submit">
</form>
"""


@app.route('/upload', methods=['POST'])
def upload_file():
    selected_file = request.files.get('file')

    print(selected_file.filename)

    if not selected_file:
        return jsonify(error='No file selected for upload.'), 400

    app.logger.info("File selected for upload {}".format(selected_file.filename))

    try:
        # Initializing GCP storage client
        gcp_storage = storage.Client()

        # Getting the bucket URL where the file needs to be uploaded
        bucket = gcp_storage.get_bucket(CLOUD_STORAGE_BUCKET)

        # Initializing blob object
        blob = bucket.blob(selected_file.filename)

        # Uploading the file
        blob.upload_from_string(
            selected_file.read(),
            content_type=selected_file.content_type
        )

        res = "File: {} has been successfully uploaded to the bucket {}".format(selected_file.filename
                                                                                , CLOUD_STORAGE_BUCKET)
        app.logger.info(res)
        return jsonify(message="File has been successfully uploaded", filename=selected_file.filename), 201
    except Exception as e:
        app.logger.error(e)
        return jsonify(message="An error occurred while uploading the file", error=str(e)), 409


@app.errorhandler(500)
def server_error(e):
    app.logger.error('An error occurred during a request.')
    return jsonify(message="An internal error occurred", error="{} See logs for full stacktrace.".format(e))\
        , 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
