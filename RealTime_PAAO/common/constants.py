import numpy as np

LAMBDA = np.arange(480, 800 + 1)
ZEROS = np.zeros(len(LAMBDA))
# Plot constants
# Labels
THICKNESS_PER_TIME_TITLE = "PAAO thickness and current dependence on anodization time"
THICKNESS_PER_TIME_X_LABEL = "Time $(s)$"
THICKNESS_PER_TIME_Y_LABEL = "Thickness $(nm)$"
THICKNESS_PER_TIME_Y2_LABEL = "Current $(mA)$"

FITTED_X_LABEL = "Wavelength $(nm)$"
FITTED_Y_LABEL = "Reflection $(a.u.)$"
FITTED_TITLE = "Real and fitted spectrum"

# Axis
SPECTRUM_Y_LIM = [0.7, 0.95]
SPECTRUM_Y_TICKS = np.arange(0.7, 0.9, 0.05)
# SPECTRUM_Y_LIM = [1, 3]
# SPECTRUM_Y_TICKS = np.arange(1, 3, 0.2)
SPECTRUM_X_TICKS = np.arange(LAMBDA[0], LAMBDA[-1] + 1, 40)
CURRENT_Y_LIM = [-2, 12]

PLOT_SIZE = (6, 4)

REAL_DATA_SKIP_HEADERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 3665, 3666]
TXT_EXTENSION = "*.txt"
ALLOWED_REF_SPEKTRS_NAME = ["ref_spektrs.txt", "ref spektrs.txt", "rf_spektrs.txt", "r_spektrs.txt", "r spektrs.txt"]

# GUI info elements
INFO_ANOD_TIME = "ANOD-TIME"
INFO_THICKNESS = "ANOD-THICK"
INFO_FILE = "ANOD-FILE"
INFO_CURRENT = "ANOD-CURRENT"

THEORETICAL_TIME = np.arange(0, 700)
THEORETICAL_THICKNESS = THEORETICAL_TIME * 0.811 + 71.5921

INTERCEPT = 71.5921
SLOPE = 0.811
