#!/usr/bin/python
import os
import sys
import signal
import json
import yfinance as yf
import pandas as pd
import math
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

g_StocksDB = None

def Load(filename):
	if os.path.isfile(filename) is True:
		file = open(filename, "r")
		data = file.read()
		file.close()
		return data
	return ""

def Save (filename, data):
	file = open(filename, "w")
	file.write(data)
	file.close()

def Append (filename, data):
	file = open(filename, "a")
	file.write(data)
	file.close()

def Get5D(ticker):
	'''
		Open,High,Low,Close,Volume,Dividends,Stock Splits
	'''
	hist = []
	objtk = yf.Ticker(ticker)
	data = objtk.history(period="1mo", interval="5m")
	for idx, row in data.iterrows():
		hist.append({
			"date": "{0}".format(idx),
			"open": row['Open'],
			"close": row['Close'],
			"high": row['High'],
			"low": row['Low'],
			"vol": row['Volume']
		})
	return hist

g_exit = False
def signal_handler(signal, frame):
	global g_exit
	print("Accepted signal from other app")
	g_exit = True

def FindBufferMaxMin(buffer):
		pmax = 0		
		pmin = 0
		if len(buffer) > 0:
			pmin = buffer[0]
			for item in buffer:
				if pmax < item:
					pmax = item
				if pmin > item:
					pmin = item
		return pmin, pmax

def CreateHistogram(buffer, bin_size):
	ret_hist_buffer_y = []
	ret_hist_buffer_x = []
	freq = 1
	try:
		if len(buffer) > 0:
			# Find min and max for this buffer
			pmin, pmax = FindBufferMaxMin(buffer)
			# print("pmax:{0}, pmin:{1}, bin_size:{2}".format(pmax,pmin,bin_size))
			# Calculate freq
			freq = (float(pmax) - float(pmin)) / float(bin_size)
			if freq == 0:
				return 0, [pmin], [pmax]
			# Generate x scale
			ret_hist_buffer_x = [(x * freq) + pmin for x in range(0, int(bin_size))]
			ret_hist_buffer_y = [0] * int(bin_size)
			# Generate y scale
			for sample in buffer:
				index = int((float(sample) - float(pmin)) / freq)
				if index == bin_size:
					index = bin_size - 1
				#print(index, sample, freq, pmin, pmax)
				ret_hist_buffer_y[index] += 1
	except Exception as e:
		print("Histograme exception {0}".format(e))
		return 1, [], []
	return 0, ret_hist_buffer_y, ret_hist_buffer_x

def MAVG(buffer, win):
	window_size = win
	i = 0

	moving_averages = []
	while i < len(buffer) - window_size + 1:
		this_window = buffer[i : i + window_size]
		window_average = sum(this_window) / window_size
		moving_averages.append(window_average)
		i += 1
	
	x_scale = [x for x in range(0, len(moving_averages))]
	
	return moving_averages, x_scale

def GetIntersetPoints(data):
	data_diff = []
	roi_list  = []

	pmin, pmax = FindBufferMaxMin(data)
	avg = (pmax + pmin) / 2
	
	diff_arr = np.array(data, dtype=np.double)
	data_diff = np.diff(diff_arr, n=1).tolist()

	# ------------------------------------------------------------------ DIFF REMOVE POSITIVE SLOPE START
	for idx, item in enumerate(data_diff):
		if item < 0:
			if idx < len(data_diff) - 2:
				if data_diff[idx + 1] > 0:
					pass
				else:
					data_diff[idx] = 0
		if item > 0:
			data_diff[idx] = 0
	# ------------------------------------------------------------------ DIFF REMOVE POSITIVE SLOPE END

	# ------------------------------------------------------------------ HISTOGRAM START
	error, hist_y, hist_x = CreateHistogram(data_diff, len(data_diff))

	hist_sum = 0.0
	for sample in hist_y:
		hist_sum += sample
	
	if hist_sum == 0:
		return []

	filter_thershold = 0.0
	perc_integral 	 = 0.0
	for idx, sample in enumerate(hist_y):
		perc_integral += sample
		if (perc_integral / hist_sum) > 0.1:
			filter_thershold = hist_x[idx]
			break
	# ------------------------------------------------------------------ HISTOGRAM END

	# ------------------------------------------------------------------ DIFF REMOVE NOISE START
	for idx, item in enumerate(data_diff):
		if item > filter_thershold:
			data_diff[idx] = 0
	# ------------------------------------------------------------------ DIFF REMOVE NOISE END
	
	# ------------------------------------------------------------------ FIND GROUPS START
	start_of_peak 	= 0
	item_counter 	= 0
	prev_item 		= 0
	for idx, item in enumerate(data_diff):
		if prev_item == 0 and item < 0: # START OF PEAK
			start_of_peak = idx
		elif prev_item < 0 and item < 0: # MIDDLE OF PEAK
			pass
		elif prev_item == 0 and item == 0: # NO PEAK
			# Count items
			item_counter += 1
		elif prev_item < 0 and item == 0: # END OF PEAK
			# Check length of items between previouse peak
			if item_counter < 10 and len(roi_list) > 0:
				roi_list[-1]["end"] = idx
				roi_list[-1]["data"] = data_diff[roi_list[-1]["start"]:idx]
			else:
				roi_list.append({
					"start": start_of_peak,
					"end": idx,
					"data": data_diff[start_of_peak:idx]
				})
			# Start items counter
			item_counter = 0
		else:
			# ANY OTHER CASE
			pass

		prev_item = item
	
	return roi_list
	
	if history == None:
		return roi_list[-1]

	if history["start"] != roi_list[-1]["start"] and history["end"] != roi_list[-1]["end"]:
		return roi_list[-1]
	else:
		return None
			
	# ------------------------------------------------------------------ FIND GROUPS END

def CompareRoi(a, b):
	pass

def main():
	parser = argparse.ArgumentParser(description='Stock DB Creator')
	parser.add_argument('--update', action='store_true', help='Update DB')
	parser.add_argument('--ticker', action='store', dest='ticker', help='Calculate single ticker')
	parser.add_argument('--plot', action='store_true', help='Update DB')
	args = parser.parse_args()

	if args.ticker is not None:
		x_buff = []
		y_buff = []

		ticker = args.ticker
		data = Get5D(ticker)

		# Build y scale (close data)
		for idx, item in enumerate(data):
			y_buff.append(item["close"])
		
		y_buff, x_buff = MAVG(y_buff, 10)

		rois  		= None
		rois_map 	= {}
		window_size = 96 # hours
		w_start 	= 0
		w_end 		= window_size
		# print(len(y_buff), y_buff)
		while len(y_buff) - 1 != w_end:
			# print(w_start, w_end, len(y_buff))
			rois = GetIntersetPoints(y_buff[w_start:w_end])
			if len(rois) > 0:
				key = w_start+rois[-1]["end"]
				rois_map[key] = 1
			w_start += 1
			w_end   += 1
		
		pmin, pmax = FindBufferMaxMin(y_buff)
		avg = (pmax + pmin) / 2
		scale_const = (pmax - pmin) / 12
	
		y1 = [pmin] * len(x_buff)
		for idx in rois_map:
			y1[idx] = pmin + scale_const
		
		print(y1)

		fig, (ax1) = plt.subplots(1, 1)
		fig.subplots_adjust(hspace=0.5)

		ax1.plot(x_buff, y_buff, color='green')
		ax1.plot(x_buff, y1, color='red')
	
		plt.show()

if __name__ == "__main__":
	main()
