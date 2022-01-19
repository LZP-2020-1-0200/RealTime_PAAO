import numpy as np
import pandas as pd

from RealTime_PAOO.common.constants import LAMBDA, REAL_DATA_SKIP_HEADERS
from RealTime_PAOO.data.helpers import interpolate, split_to_arrays


# M. Daimon and A. Masumura. Measurement of the refractive index of distilled water from the near-infrared region
# to the ultraviolet region, Appl. Opt. 46, 3811-3820 (2007)
def get_water_data_from_file(filename, conversion):
    data = np.genfromtxt(filename, delimiter='\t', encoding='utf-8')
    return split_to_arrays(data, conversion)


# A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. Optical properties of metallic films for
# vertical-cavity optoelectronic devices, Appl. Opt. 37, 5271-5283 (1998)
def get_al_data_from_file(filename, conversion):
    data = np.genfromtxt(filename, delimiter=' ', skip_header=9, skip_footer=3, encoding='utf-8')
    return split_to_arrays(data, conversion)


def get_al203_data(length):
    return np.full(length, 1.65)


def get_real_data(current_file, reference_spectrum, R0):
    current_file_spectrum = pd.read_csv(current_file, delimiter='\t', skiprows=REAL_DATA_SKIP_HEADERS,
                                        dtype=np.double, names=["Wavelength", "Intensity"])
    intensity_spectrum = interpolate(current_file_spectrum["Wavelength"], current_file_spectrum["Intensity"],
                                     LAMBDA)

    return (intensity_spectrum / reference_spectrum) * R0


def get_reference_spectrum(path) -> np.ndarray:
    reference_spectrum_from_file = np.genfromtxt(path, delimiter='\t', skip_header=17,
                                                 skip_footer=1, encoding='utf-8')
    reference_spectrum_data = split_to_arrays(reference_spectrum_from_file)
    return interpolate(*reference_spectrum_data, LAMBDA)
