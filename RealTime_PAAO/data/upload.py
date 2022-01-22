import threading
import time

import requests

from RealTime_PAAO.common import shared
from RealTime_PAAO.gui.main_gui.helpers import update_uploading

# CHANGEEEEE!!!
ACCESS_TOKEN = 'FwTvXGqMz20WprHPvzOOQw6N9PMK2nrJ0gQfG3AyIMeNuPVG4WmuZydIZhSc'
bucket_url = 'https://sandbox.zenodo.org/api/files/c5edac05-aca7-4a59-8c8b-1040fba40de5'


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
