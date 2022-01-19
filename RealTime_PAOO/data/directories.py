import shutil
import threading
import time
from pathlib import Path

import PySimpleGUI as sg

from RealTime_PAOO.common import shared
from RealTime_PAOO.common.constants import TXT_EXTENSION
from RealTime_PAOO.gui.helpers import update_zipping


def get_data_directory():
    return Path(sg.popup_get_folder('', no_window=True))


def make_folder(path, folder_name):
    full_path = path / folder_name
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def copy_files(list_of_files: list, new_dir: Path):
    for file in list_of_files:
        shutil.copy2(file, new_dir)


def move_file(list_of_files: list, new_dir: Path):
    for file in list_of_files:
        file.rename(new_dir / file.name)


def make_folders_and_move_files(anod_start_index, anod_end_index, data_folder, window):
    window['STOP'].update(text="Reorganizing files, Please wait... ")
    original_folder = make_folder(data_folder, 'Originals')
    organized_folder = make_folder(data_folder, 'Organized files')

    pre_anod_folder = make_folder(organized_folder, '1. Pre anodizing spectrum')
    anod_folder = make_folder(organized_folder, '2. Anodizing spectrum')
    post_anod_folder = make_folder(organized_folder, '3. Post anodizing spectrum')
    fitted_plot_folder = make_folder(organized_folder, '4. Anodizing Plots')
    fitted_data_folder = make_folder(organized_folder, '5. Anodizing Data')

    all_files = data_folder.rglob(TXT_EXTENSION)
    files = [x for x in all_files if x.is_file()]
    copy_files([files[-1]], anod_folder)
    move_file([files[-1]], original_folder)
    files.pop()
    pre_anod_files = files[:anod_start_index]
    anod_files = files[anod_start_index:anod_end_index]
    post_anod_files = files[anod_end_index:]

    copy_files(pre_anod_files, pre_anod_folder)
    copy_files(anod_files, anod_folder)
    copy_files(post_anod_files, post_anod_folder)

    move_file(pre_anod_files, original_folder)
    move_file(anod_files, original_folder)
    move_file(post_anod_files, original_folder)
    window['STOP'].update(text="Done reorganizing files", disabled=True)
    window['SAVE'].update(disabled=False)


def zip_files(path_to_zip: Path, zip_name: Path, window):
    output_filename = str(path_to_zip / zip_name)
    input_dir = str(path_to_zip)
    threading.Thread(target=update_zipping, daemon=True,
                     args=(window,)).start()
    shutil.make_archive(output_filename, 'zip', input_dir)
    shared.zipper_animation = False
    window['START'].update(text='Zipping completed')
    time.sleep(1.5)
    window['START'].update(text='Window can be closed now')
