import os

import pdfkit
from flask import current_app
from pyvirtualdisplay.display import Display
from werkzeug.utils import secure_filename


def _generate_pdf_file(data, generated_file_path):
    config = pdfkit.configuration(wkhtmltopdf=current_app.config["PDF_GEN_BIN_PATH"])
    pdfkit.from_string(
        data.get("body"),
        generated_file_path,
        configuration=config,
        options={
            "page-size": "A6",
            "margin-top": "0",
            "margin-right": "0",
            "margin-left": "0",
            "margin-bottom": "0",
            "encoding": "UTF-8",
        },
    )


def generate_pdf_file(data, file_name, folder_path=None):
    if not folder_path:
        folder_path = current_app.config.get("TEMP_GENERATED_FILE_PATH")
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    generated_file_path = os.path.join(folder_path, "{}.pdf".format(file_name))
    if current_app.config.get("USE_VIRTUAL_DISPLAY"):
        with Display():
            _generate_pdf_file(data, generated_file_path)
    else:
        _generate_pdf_file(data, generated_file_path)


def is_valid_filename(filename):
    sec_filename = secure_filename(filename)
    return filename == sec_filename


def validate_file_extensions(filename, valid_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in valid_extensions
