from pathlib import Path

correct_ref_file = False
correct_thickness = False
list_of_files = []
ref_spectrum_name = ''
reference_spectrum = []
fitting = False
spektri = []
current_real_data = []
real_data_history = []
fitted_parameters = [0, 1]
thickness_history = []
current_fitted_data = []
fitted_data_history = []

# real time
desired_thickness = 0
anod_ending_index = 0
anod_starting_index = 0
i = 0
current_file = Path()
emergency_stop = False

zipper_animation = True
filename = ''

integration_time = 0
integration_time_units = ''
spectra_average = 0
anodization_time = 0
last_thickness = 0
uploader_animation = True