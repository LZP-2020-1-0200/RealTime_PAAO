import numpy as np

from functions import split_to_arrays


# M. Daimon and A. Masumura. Measurement of the refractive index of distilled water from the near-infrared region
# to the ultraviolet region, Appl. Opt. 46, 3811-3820 (2007)
def get_water_data_from_file(filename, conversion):
    data = np.genfromtxt(filename / "Water.txt", delimiter='\t', encoding='utf-8')
    return split_to_arrays(data, conversion)


def get_al203_data(length):
    return np.full(length, 1.65)


# A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. Optical properties of metallic films for
# vertical-cavity optoelectronic devices, Appl. Opt. 37, 5271-5283 (1998)
def get_al_data_from_file(filename, conversion):
    data = np.genfromtxt(filename / "Rakic-BB.yml.txt", delimiter=' ', skip_header=9, skip_footer=3, encoding='utf-8')
    return split_to_arrays(data, conversion)


def create_ntilde(water, al203, al):
    return np.array([water, al203, al])
