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

            else:
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(uuid4())))
                f.save(path)
                session["file"] = path
                response_data["pathAvailable"] = True
        else:
            response_data["pathAvailable"] = True
            path = session["file"]

        if path is not None:
            with open(path, 'r', encoding="UTF-8") as file:
                names = file.readlines()
                shuffle(names)
                for name in range(0, len(names)):
                    names[name] = f"{name + 1} - {names[name]}"
                response_data["dataAvailable"] = True
                response_data["sortedList"] = names
                response_data["jsParsedSorterList"] = json.dumps(names)
                response_data["listLen"] = len(names)
                for name in names:
                    response_data["rawData"] = response_data["rawData"] + name + "<br>"
                if bool(request.form.getlist("record")):
                    uuid = session["uuid"]
                    response_data["recordUUID"] = uuid
                    db = get_db()
                    db.execute(f"INSERT INTO extractions ('uuid', 'raw', 'timestamp') VALUES(?,?,?)",
                               (str(uuid), response_data['rawData'], str(datetime.now())))
                    db.commit()
                    session["uuid"] = uuid4()
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
