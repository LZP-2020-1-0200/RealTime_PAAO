import numpy as np

from RealTime_PAAO.common.constants import LAMBDA
from RealTime_PAAO.common.paths import path_to_al_refractive_info, path_to_water_refractive_info
from RealTime_PAAO.data.helpers import interpolate
from RealTime_PAAO.data.read import get_al203_data, get_al_data_from_file, get_water_data_from_file


nk_water = interpolate(*get_water_data_from_file(path_to_water_refractive_info, 1e3), LAMBDA)
nk_al2o3 = get_al203_data(len(nk_water))
nk_al = interpolate(*get_al_data_from_file(path_to_al_refractive_info, 1e3), LAMBDA)
nk = np.array([nk_water, nk_al2o3, nk_al])
