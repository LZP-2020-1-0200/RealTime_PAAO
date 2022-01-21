import os
import shutil
import threading
import time
import zipfile
from pathlib import Path

import PySimpleGUI as sg

from RealTime_PAOO.common import paths, shared
from RealTime_PAOO.common.constants import TXT_EXTENSION
from RealTime_PAOO.gui.main_gui.helpers import update_zipping


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


def move_spectrums(anod_start_index, anod_end_index, data_folder, window):
    window['STOP'].update(text="Reorganizing files, Please wait... ")

    # original_folder = make_folder(data_folder, 'Originals')
    # organized_folder = make_folder(data_folder, 'Organized files')
    #
    # pre_anod_folder = make_folder(organized_folder, '1. Pre anodizing spectrum')
    # anod_folder = make_folder(organized_folder, '2. Anodizing spectrum')
    # post_anod_folder = make_folder(organized_folder, '3. Post anodizing spectrum')
    # fitted_plot_folder = make_folder(organized_folder, '4. Anodizing Plots')
    # fitted_data_folder = make_folder(organized_folder, '5. Anodizing Data')

    all_files = data_folder.rglob(TXT_EXTENSION)
    files = [x for x in all_files if x.is_file()]
    ref_spectrum = [x for x in files if x.name == shared.ref_spectrum_name]
    copy_files(ref_spectrum, paths.path_to_anod_folder)
    # move_file([files[-1]], original_folder)
    files.remove(ref_spectrum[0])

    pre_anod_files = files[:anod_start_index]
    anod_files = files[anod_start_index:anod_end_index]
    post_anod_files = files[anod_end_index:]

    copy_files(pre_anod_files, paths.path_to_pre_anod_folder)
    copy_files(anod_files, paths.path_to_anod_folder)
    copy_files(post_anod_files, paths.path_to_post_anod_folder)

    window['STOP'].update(text="Done reorganizing files", disabled=True)
    window['SAVE'].update(disabled=False)


def make_folders_and_move(data_folder,window):
    paths.path_to_data_folder = data_folder
    paths.path_to_organized_folder = make_folder(data_folder, 'Organized files')

    paths.path_to_pre_anod_folder = make_folder(paths.path_to_organized_folder, '1. Pre anodizing spectrum')
    anod_folder = make_folder(paths.path_to_organized_folder, '2. Anodizing spectrum')
    pahs = make_folder(paths.path_to_organized_folder, '3. Post anodizing spectrum')
    paths.path_to_fitted_plot_folder = make_folder(paths.path_to_organized_folder, '4. Anodizing Plots')
    paths.path_to_fitted_data_folder = make_folder(paths.path_to_organized_folder, '5. Anodizing Data')

    all_files = paths.path_to_data_folder.rglob(TXT_EXTENSION)
    files = [x for x in all_files if x.is_file()]
    copy_files(files, paths.path_to_anod_folder)

    window['STOP'].update(text="Done reorganizing files", disabled=True)
    window['SAVE'].update(disabled=False)

def zip_dir(dir, filename, window):
    """Zip the provided directory without navigating to that directory using `pathlib` module"""

    # Convert to Path object
    new_filename = Path(str(filename) + '.zip')
    threading.Thread(target=update_zipping, daemon=True,
                     args=(window,)).start()

    with zipfile.ZipFile(new_filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in dir.rglob("*"):
            zip_file.write(entry, entry.relative_to(dir))
    time.sleep(0.5)

    new_filename = new_filename.rename(dir / new_filename.name)
    shared.zipper_animation = False
    return new_filename


def zip_files(path_to_zip: Path, zip_name: str, what_to_zip, window):
    output_filename = str(path_to_zip) + zip_name
    input_dir = str(what_to_zip)

    threading.Thread(target=update_zipping, daemon=True,
                     args=(window,)).start()
    shutil.make_archive(output_filename, 'zip', input_dir)
    zip_output_filename = Path(path_to_zip / (zip_name + '.zip'))
    zip_output_filename.rename(what_to_zip / zip_output_filename.name)
    shared.zipper_animation = False

    window['START'].update(text='Zipping completed')
    time.sleep(1)
