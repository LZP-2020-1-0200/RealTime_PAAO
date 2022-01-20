from RealTime_PAOO.common.constants import CURRENT_Y_LIM, FITTED_TITLE, FITTED_X_LABEL, FITTED_Y_LABEL, LAMBDA, \
    SPECTRUM_X_TICKS, SPECTRUM_Y_LIM, SPECTRUM_Y_TICKS, THICKNESS_PER_TIME_TITLE, THICKNESS_PER_TIME_X_LABEL, \
    THICKNESS_PER_TIME_Y2_LABEL, THICKNESS_PER_TIME_Y_LABEL


def set_anodization_thickness_per_time_plot_labels(thickness_ax, current_ax):
    thickness_ax.set_xlim(0, 300)
    thickness_ax.set_ylim(0, 300)
    thickness_ax.set_title(THICKNESS_PER_TIME_TITLE, pad=15)
    thickness_ax.grid(True)
    thickness_ax.set_xlabel(THICKNESS_PER_TIME_X_LABEL)
    thickness_ax.set_ylabel(THICKNESS_PER_TIME_Y_LABEL)

    current_ax.set_ylim(CURRENT_Y_LIM)
    current_ax.set_ylabel(THICKNESS_PER_TIME_Y2_LABEL)


def set_fitting_plot_labels(fitting_ax):
    fitting_ax.set_xlim(LAMBDA[0], LAMBDA[-1])
    fitting_ax.set_ylim(SPECTRUM_Y_LIM)
    fitting_ax.set_yticks(SPECTRUM_Y_TICKS)
    fitting_ax.set_xticks(SPECTRUM_X_TICKS)
    fitting_ax.set_xlabel(FITTED_X_LABEL)
    fitting_ax.set_ylabel(FITTED_Y_LABEL)
    fitting_ax.set_title(FITTED_TITLE, pad=15)
    fitting_ax.grid(True)
    fitting_ax.yaxis.tick_right()
    fitting_ax.yaxis.set_label_position("right")


def redraw_plots(fig_agg1, fig_agg2):
    fig_agg1.draw()
    fig_agg2.draw()
    fig_agg1.flush_events()
    fig_agg2.flush_events()
