import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt


def interpolate(x_data, y_data, new_x_data):
	return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def split_to_arrays(data, conversion=1):
	if data.shape[1] == 3:
		return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
	return [data[:, 0] * conversion, data[:, 1]]


def get_spectra_filename(i):
	number_file = {10  : "R0000", 100: "R000",
	               1000: "R00", 10000: "R0", 100000: "R"}
	for key, value in number_file.items():
		if i < key:
			return value + str(i) + ".txt"


def save_plots(thickness_history, save_path, time_interval):
	real_data = np.load('real.npy')
	fitted_data = np.load('fitted.npy')

	# print(len(real_data),len(fitted_data))
	time_fro_plot = np.arange(0, time_interval * len(fitted_data), time_interval)
	lambda_range = np.arange(480, 800 + 1)
	for i, (x, y, z) in enumerate(zip(real_data, fitted_data, thickness_history)):
		plt.clf()
		plt.plot(lambda_range, x, lambda_range, y)
		plt.xlim(480, 800)
		plt.ylim(0.75, 0.95)
		plt.yticks(np.arange(0.75, 0.90, 0.05))
		plt.xlabel("Wavelength (nm)")
		plt.ylabel("Reflection (a.u.)")
		plt.title("file={}  d={}  m={}".format(
			get_spectra_filename(i + 1), *z))
		plt.savefig(save_path / (get_spectra_filename(i + 1)[:-4] + '.png'))
		print(save_path / (get_spectra_filename(i + 1)[:-4] + '.png\tsaved'))

	plt.clf()
	plt.plot(time_fro_plot, np.array(thickness_history)[:, 0])
	plt.xlabel("Time (s)")
	plt.ylabel("Thickness (nm)")
	plt.title("PAAO thickness dependence on anodization time")
	plt.savefig(save_path / ('Thickness_per_time.png'))
	print(save_path / 'Thickness_per_time.png \tsaved')
	print('\nDone!')
	input('Press enter to exit\n')
