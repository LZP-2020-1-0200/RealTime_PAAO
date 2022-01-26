import threading
import time

import requests

from RealTime_PAAO.common import shared
from RealTime_PAAO.gui.main_gui.helpers import update_uploading

# CHANGEEEEE!!!
ACCESS_TOKEN = 'XvK0RJGyF26GVWTL7hKdfGUUUD0fUbR8KIgn0avGFoVXPxxhlSKQ2LTCnUva'
bucket_url = 'https://zenodo.org/api/files/49a14c4c-319a-4398-8b52-493ebf543e61'


# my test
# ACCESS_TOKEN = 'EaaBGopxSv3jGRx9AJO04r0nPKqButErGOu5ygBfvbXp3vB54uhhGDAU0Ta1'
# bucket_url = 'https://zenodo.org/api/files/462fe752-8075-40c3-a9fa-8ce43598eb3d'

def upload_to_zenodo(filename, path, window):
    window['START'].update(text='Uploading')
    params = {'access_token': ACCESS_TOKEN}

    threading.Thread(target=update_uploading, daemon=True,
                     args=(window,)).start()
    with open(path, "rb") as fp:
        r = requests.put(
            "%s/%s" % (bucket_url, filename),
            data=fp,
            params=params,
        )
    shared.uploader_animation = False
    if r.status_code == 200:
        window['START'].update(text='Uploaded successfully')
    else:
        window['START'].update(text='Upload failed')
    time.sleep(2)
    window['START'].update(text='Window now can be closed')
