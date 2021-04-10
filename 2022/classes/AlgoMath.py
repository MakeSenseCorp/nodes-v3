#!/usr/bin/python
import os
import sys
import json
import time
import base64
import datetime
from datetime import date
import math

class AlgoMath():
	def __init__(self):
		self.ClassName = "AlgoMath"
	
	def FindBufferMaxMin(self, buffer):
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

	def CreateHistogram(self, buffer, bin_size):
		ret_hist_buffer_y = []
		ret_hist_buffer_x = []
		freq = 1
		try:
			if len(buffer) > 0:
				# Find min and max for this buffer
				pmin, pmax = self.FindBufferMaxMin(buffer)
				# Calculate freq
				freq = (float(pmax) - float(pmin)) / float(bin_size)
				if freq == 0:
					return 0, [pmin], [pmax]
				# Generate x scale
				ret_hist_buffer_x = [(x * freq) + pmin for x in range(0, bin_size)]
				ret_hist_buffer_y = [0] * bin_size
				# Generate y scale
				for sample in buffer:
					index = int((float(sample) - float(pmin)) / freq)
					if index == 25:
						index = 24
					#print(index, sample, freq, pmin, pmax)
					ret_hist_buffer_y[index] += 1
		except Exception as e:
			print("Histograme exception {0}".format(e))
			return 1, [], []
		return 0, ret_hist_buffer_y, ret_hist_buffer_x
	
	def CalculatePercentile(self, low, high, histogram):
		low_perc  			= 0
		low_perc_found  	= False

		mid_perc 			= 0
		mid_perc_found 		= False

		high_perc 			= 0
		high_perc_found 	= False

		pmin 				= 0
		pmin_found 			= False
	
		pmax 				= 0
		pmax_found 			= False

		perc_integral 		= 0.0
		hist_sum 			= 0.0

		hist_len 			= len(histogram)

		for sample in histogram:
			hist_sum += sample

		# TODO - use liniar interpulation
		for idx, sample in enumerate(histogram):
			perc_integral += sample
			if low_perc_found is False:
				if (perc_integral / hist_sum) > low:
					low_perc_found = True
					low_perc = idx
			if high_perc_found is False:
				if (perc_integral / hist_sum) > high:
					high_perc_found = True
					high_perc = idx
			if mid_perc_found is False:
				if (perc_integral / hist_sum) >= 0.5:
					mid_perc_found = True
					mid_perc = idx
			if pmin_found is False:
				if sample > 0:
					pmin_found = True
					pmin = idx
			if pmax_found is False:
				if histogram[(hist_len - 1) - idx] > 0:
					pmax_found = True
					pmax = (hist_len - 1) - idx
		
		return pmin, low_perc, mid_perc, high_perc, pmax
	
	def CalculateRegression(self, coordinates):
		avg_x = 0
		avg_y = 0
		x_dist_2_sum = 0
		y_dist_2_sum = 0
		# Calculate avgs
		for sample in coordinates:
			avg_x += sample["x"]
			avg_y += sample["y"]
			
		avg_x = (avg_x) / (len(coordinates))
		avg_y = (avg_y) / (len(coordinates))

		for sample in coordinates:
			sample["x_dist"] = sample["x"] - avg_x
			sample["y_dist"] = sample["y"] - avg_y

			sample["x_dist_2"] = sample["x_dist"] * sample["x_dist"]
			sample["y_dist_2"] = sample["x_dist"] * sample["y_dist"]

			x_dist_2_sum += sample["x_dist_2"]
			y_dist_2_sum += sample["y_dist_2"]
		
		if x_dist_2_sum <= 0:
			return 0, 0
		
		slope = (y_dist_2_sum) / (x_dist_2_sum)
		b = avg_y - slope * avg_x

		return slope, b
		
	def RValue(self, coordinates, slope, b):
		avg_y = 0
		y_dist_2_sum = 0
		estimated_y_dist_2_sum = 0
		# Calculate avgs
		for sample in coordinates:
			avg_y += sample["y"]
		avg_y = float(avg_y) / float(len(coordinates))

		for sample in coordinates:
			sample["y_dist"] = sample["y"] - avg_y
			sample["y_dist_2"] = sample["y_dist"] * sample["y_dist"]
			sample["estimated_y"] = sample["x"] * slope + b
			sample["estimated_y_dist"] = sample["estimated_y"] - avg_y
			sample["estimated_y_dist_2"] = sample["estimated_y_dist"] * sample["estimated_y_dist"]
			y_dist_2_sum += sample["y_dist_2"]
			estimated_y_dist_2_sum += sample["estimated_y_dist_2"]
		
		if float(y_dist_2_sum) <= 0.0:
			return 0.0
		
		r = float(estimated_y_dist_2_sum) / float(y_dist_2_sum)
		return r
	
	def Variance(self, data, ddof=0):
		n = len(data)
		mean = sum(data) / n
		return sum((x - mean) ** 2 for x in data) / (n - ddof)

	def Stdev(self, data):
		var = self.Variance(data)
		std_dev = math.sqrt(var)
		return std_dev
