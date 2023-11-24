import os
import requests
import logging
from flask import Flask, request
from google.cloud import storage
import pandas as pd

import simulation as simulation

app = Flask(__name__)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ["CLOUD_STORAGE_BUCKET"]

@app.route("/")
def index() -> str:

    example_html = pd.read_excel(f"https://storage.googleapis.com/{CLOUD_STORAGE_BUCKET}/sample/character_info.xlsx", sheet_name="Heroes").to_html()

    html_file = f"""
    <html>
    <head>
        <title>DnD Combat Simulator</title>
    </head>
    <body>
        <h1>DnD Combat Simulator</h1>
        <p>Upload a .xlsx file with two Sheets titled Heroes and Monsters, listing information about each character</p>
        <p>Download the sample file <a href="https://storage.googleapis.com/{CLOUD_STORAGE_BUCKET}/sample/character_info.xlsx">here</a></p>
        <p>Sample file contains explanations on how to input your character's information.</p>
        <p>With any recommendations, please reach out to me on <a href="https://github.com/andrei-gorbatch/monte_carlo">github</a></p>
    </body>
    <body>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit">
        </form>
    </body>
    </html>
    """
    return html_file


@app.route("/upload", methods=["POST"])
def upload() -> str:
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get("file")

    if not uploaded_file:
        return "No file uploaded.", 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(), content_type=uploaded_file.content_type
    )

    # Make the blob public.
    blob.make_public()

    # The public URL can be used to directly access the uploaded file via HTTP.
    uploaded_file_url = blob.public_url

    # Run the simulation
    text = simulation.main(uploaded_file_url)

    return text


@app.errorhandler(500)
def server_error(e: Exception | int) -> str:
    logging.exception("An error occurred during a request.")
    return (
        """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(
            e
        ),
        500,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)