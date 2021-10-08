import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from randomSorterWebApp.db import get_db
import json
import os
from uuid import uuid4
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from random import shuffle
from datetime import datetime

bp = Blueprint('index', __name__)


@bp.route('/', methods=("GET", "POST"))
def display_index():
    # response json
    response_data = {
        "dataAvailable": False,
        "pathAvailable": False,
        "error": None,
        "sortedList": [],
        "rawData": "",
        "record": False,
        "recordUUID": None
    }

    if request.method == "POST":
        path = None

        # is there a file in the request?
        if bool(request.files):
            f = request.files['file']

            # is it empty?
            if f.filename == '':
                response_data["error"] = "No file provided"

            # if not, saving the file locally and add a cookie to keep the file information
            # TODO: File elimination scheduler
            else:
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(uuid4())))
                f.save(path)
                response_data["pathAvailable"] = True

        if path is not None:

            with open(path, 'r', encoding="UTF-8") as file:
                names = file.readlines()
                shuffle(names)

                # some string formatting
                for name in range(0, len(names)):
                    names[name] = f"{name + 1} - {names[name]}"
                for name in names:
                    response_data["rawData"] = response_data["rawData"] + name + "<br>"

                # response assignments
                response_data["dataAvailable"] = True
                response_data["sortedList"] = names
                response_data["jsParsedSorterList"] = json.dumps(names)
                response_data["listLen"] = len(names)

                # do I have to save the extraction?
                if bool(request.form.getlist("record")):
                    uuid = session["uuid"]
                    response_data["recordUUID"] = uuid

                    # TODO: database folder with all database-related functions
                    db = get_db()
                    db.execute(f"INSERT INTO extractions ('uuid', 'raw', 'timestamp') VALUES(?,?,?)",
                               (str(uuid), response_data['rawData'], str(datetime.now())))
                    db.commit()

    else:
        session["uuid"] = uuid4()
        response_data["recordUUID"] = session["uuid"]

    return render_template("index.html", data=response_data)


@bp.route("/raw-<path>", methods=("GET", "POST"))
def display_raw(path):
    return path


@bp.route("/dbLookup-<uuid>", methods=("GET", "POST"))
def display_db_lookup(uuid):
    data = get_db().execute("SELECT raw, timestamp FROM extractions WHERE uuid=?", (uuid,)).fetchone()
    print(data)
    return "UUID: " + uuid + "<br><br>" + data["raw"] + "<br><br>" + "TIMESTAMP: " + data["timestamp"]
