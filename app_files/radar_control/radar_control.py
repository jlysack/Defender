#!/usr/bin/python3

import sys, os
sys.path.append("../")
import Class.TinyRad as TinyRad
import time as time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import signal
import constants as const

def signal_handler(sig, frame):    
	print('\nCtrl-C entered. Killing processes.')
    sys.exit(0)

def configure_plots(display_cfg):
    if display_cfg['time_signals'] is True:
        WinTim = pg.GraphicsLayoutWidget(show=False, title="Time signals")
        WinTim.setBackground((255, 255, 255)) 
        WinTim.resize(1000,600)

        PltTim = WinTim.addPlot(title="TimSig", col=0, row=0)
        PltTim.showGrid(x=True, y=True)

    if display_cfg['range_profile'] is True:
        WinRP = pg.GraphicsLayoutWidget(show=False, title="Range Profile")
        WinRP.setBackground((255, 255, 255))
        WinRP.resize(1000,600) 

        PltRP = WinRP.addPlot(title="Range", col=0, row=0)
        PltRP.showGrid(x=True, y=True) 

    if display_cfg['sum_data'] is True:
        WinSum = pg.GraphicsLayoutWidget(show=False, title="Sum Channel Data")
        WinSum.setBackground((255, 255, 255)) 
        WinSum.resize(1000,600)

        PltSum = WinSum.addPlot(title="Sum Channel", col=0, row=0)
        PltSum.showGrid(x=True, y=True)

	if display_cfg['dbf_cost_function'] is True:
		View = pg.PlotItem(title='Cross Range Plot')
		View.setLabel('left', 'R', units='m')
		View.setLabel('bottom', 'u')
															 
		Img = pg.ImageView(view=View)
		Img.show() 
		Img.ui.roiBtn.hide() 
		Img.ui.menuBtn.hide()
		#Img.ui.histogram.hide()
		Img.getHistogramWidget().gradient.loadPreset('flame')

	# TODO: Create plot list to return to main function
	# return plot_list

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # Configure plots
    display_cfg['frame_numbers']     = False # display frame numbers
    display_cfg['time_signals']      = False # display time signals
    display_cfg['range_profile']     = True  # display range profiles
    display_cfg['sum_data']          = True  # display sum of all (7) range profile channels
    display_cfg['dbf_cost_function'] = False # display "cost function for dbf"

    c0 = const.c0

    configure_plots(display_cfg)

	# TODO: Implement section for configuration of hardware
	# TODO: Implement section for configuration of signal processor constants
		# TODO: Make both of the above configurable on-the-fly
	# TODO: Implement board control function (reset, get data, etc.) with return
			# value checking
	# TODO: Implement signal processor functions (built-in) and add comments
	# TODO: Implement detection list functionality (1 target, or multiple targets?)
