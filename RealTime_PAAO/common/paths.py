from getpass import getuser
from pathlib import Path


def convert_string_to_path_object(path):
    return Path(path)


path_to_realtime_paoo = Path(__file__).parent.parent
path_to_desktop = Path(f'C:\\users\\{getuser()}\\Desktop\\')
# Paths to assets and refractive info
path_to_water_refractive_info = Path(path_to_realtime_paoo / 'resources/refractive_info/Water.txt')
path_to_al_refractive_info = Path(path_to_realtime_paoo / 'resources/refractive_info/Rakic-BB.yml.txt')
path_to_bad_image = str(Path(path_to_realtime_paoo / "resources/gui_assets/bad.png"))
path_to_good_image = str(Path(path_to_realtime_paoo / "resources/gui_assets/good.png"))
path_to_title_icon = str(Path(path_to_realtime_paoo / "resources/gui_assets/title_icon.ico"))

# Organize folder
organized_folder = Path('Organized files')

data_folder = Path()
ref_spectrum_path = Path()
emerg_current = path_to_desktop / 'current.txt'
log_file = path_to_desktop / 'log.txt'

path_to_data_folder = ''
path_to_original_folder = ''
path_to_organized_folder = ''
path_to_pre_anod_folder = ''
path_to_anod_folder = ''
path_to_post_anod_folder = ''
path_to_fitted_plot_folder = ''
path_to_fitted_data_folder = ''

anodization_parameters = ''
