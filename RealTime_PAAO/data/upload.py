import json
import threading
import time
from pathlib import Path

import PySimpleGUI as sg
import requests
from RealTime_PAAO.common import shared
from RealTime_PAAO.gui.main_gui.helpers import update_uploading

with open("config.json") as file:
    data = json.load(file)
    access_token = data["Access Token"]
    bucket_url = data["Bucket URL"]


def check_access_token():
    response = requests.get("https://zenodo.org/api/deposit/depositions", params={"access_token": access_token})
    response_json = response.json()

    if "message" in response_json:
        message = response_json["message"]
    else:
        message = "Something is wrong with Access token"

    if response.status_code != 200:
        sg.popup_error(message, "Automatic file upload to Zenodo is not possible!")
        return False
    return True


def check_bucket_url():
    filename = Path("text.txt")
    params = {"access_token": access_token}
    with open(filename, "w") as file:
        file.write("test bucket link")

    with open(filename, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, str(filename)),
            data=fp,
            params=params,
        )

    filename.unlink()
    response_json = r.json()

    if r.status_code != 200:
        sg.popup_error(response_json["message"], "Automatic file upload to Zenodo is not possible!")
        return False
    return True


def upload_to_zenodo(filename, path, window):
    window["START"].update(text="Uploading")
    params = {"access_token": access_token}

    threading.Thread(target=update_uploading, daemon=True, args=(window,)).start()
    with open(path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, filename),
            data=fp,
            params=params,
        )
    shared.uploader_animation = False
    if r.status_code == 200:
        window["START"].update(text="Uploaded successfully")
    else:
        window["START"].update(text="Upload failed")
    time.sleep(2)
    window["START"].update(text="Window can be closed now")
