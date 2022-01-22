from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from RealTime_PAAO.common.constants import FITTED_X_LABEL, FITTED_Y_LABEL, LAMBDA, SPECTRUM_Y_LIM, SPECTRUM_Y_TICKS, \
    THICKNESS_PER_TIME_TITLE, THICKNESS_PER_TIME_X_LABEL, THICKNESS_PER_TIME_Y_LABEL


def save_fitting_data(list_of_spectrum_files: list, all_real_data: list[list], all_fitted_data: list[list],
        plot_folder, calculated_data_folder, window):
    fig, ax = plt.subplots()
    ax.set_xlim(LAMBDA[0], LAMBDA[-1])
    ax.set_ylim(SPECTRUM_Y_LIM)
    ax.set_yticks(SPECTRUM_Y_TICKS)
    ax.set_xlabel(FITTED_X_LABEL)
    ax.set_ylabel(FITTED_Y_LABEL)
    fitted_line = ax.plot(LAMBDA, np.zeros(len(LAMBDA)), color='orange', label='Fitted data', linewidth=2)[0]
    real_line = ax.plot(LAMBDA, np.zeros(len(LAMBDA)), color='tab:blue', label='Experimental data', alpha=0.8)[0]
    ax.legend()
    for i, (spectr, real_data, fitted_data) in enumerate(zip(list_of_spectrum_files, all_real_data, all_fitted_data)):
        percentage = int((i + 1) / (len(list_of_spectrum_files) + 1) * 100)
        window['START'].update(text=f'Saving plots: {percentage}%')
        df = pd.DataFrame({'Wavelength (nm)'  : LAMBDA,
                           'Experimental data': real_data,
                           'Fitted data'      : fitted_data})
        fitted_line.set_ydata(df['Fitted data'])
        real_line.set_ydata(df['Experimental data'])
        ax.set_title(spectr)
        plt.draw()
        fig.savefig(plot_folder / (spectr[:-4] + '.png'))
        df.to_csv(calculated_data_folder / (spectr[:-4] + '.dat'), sep='\t', index=False, header=False)
    window['START'].update(text=f'Completed saving plots')


def save_thickness_per_time_data(thickness_hist, thickness_time, path_to_save):
    fig, ax1 = plt.subplots()
    ax1.plot(thickness_time, thickness_hist, label='Thickness per time')
    ax1.set_xlabel(THICKNESS_PER_TIME_X_LABEL)
    ax1.set_ylabel(THICKNESS_PER_TIME_Y_LABEL)
    ax1.set_title(THICKNESS_PER_TIME_TITLE)
    ax1.legend()
    ax1.grid()

    fig.savefig(path_to_save / 'Thickness_per_time.png')
    thick_per_time = pd.DataFrame({'Time(s)'      : thickness_time,
                                   'Thickness(nm)': thickness_hist})
    thick_per_time.to_csv(path_to_save / 'Thickness_per_time.dat', sep='\t', index=False, header=False)


def save_current_per_time_data(current_dict: dict, path_to_save: Path):
    curr_per_time = pd.DataFrame({'Anod Time (s)': current_dict.keys(),
                                  'Current (nm)' : current_dict.values()})
    curr_per_time.to_csv(path_to_save / 'Current_per_time.dat', sep='\t', index=False, header=False)
