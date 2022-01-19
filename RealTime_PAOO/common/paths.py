from getpass import getuser
from pathlib import Path


def convert_string_to_path_object(path):
    return Path(path)


path_to_desktop = Path(f'C:\\users\\{getuser()}\\Desktop\\')
# Paths to assets and refractive info
path_to_water_refractive_info = Path('RealTime_PAOO/resources/refractive_info/Water.txt')
path_to_al_refractive_info = Path('RealTime_PAOO/resources/refractive_info/Rakic-BB.yml.txt')
path_to_bad_image = str(Path("RealTime_PAOO/resources/gui_assets/bad.png"))
path_to_good_image = str(Path("RealTime_PAOO/resources/gui_assets/good.png"))
path_to_title_icon = str(Path("RealTime_PAOO/resources/gui_assets/title_icon.ico"))

# Organize folder
organized_folder = Path('Organized files')
pre_anod_folder_name = Path(organized_folder / '1. Pre anodizing spectrum')
anod_folder_name = Path(organized_folder / '2. Anodizing spectrum')
post_anod_folder_name = Path(organized_folder / '3. Post anodizing spectrum')
fitted_plot_folder_name = Path(organized_folder / '4. Anodizing Plots')
fitted_data_folder_name = Path(organized_folder / '5. Anodizing Data')

data_folder = Path()
ref_spectrum_path = Path()
emerg_current = path_to_desktop / 'current.txt'
log_file = path_to_desktop /  'log.txt'