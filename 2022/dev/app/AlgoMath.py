#!/usr/bin/python
import math
import numpy as np

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
				ret_hist_buffer_x = [(x * freq) + pmin for x in range(0, int(bin_size))]
				ret_hist_buffer_y = [0] * int(bin_size)
				# Generate y scale
				for sample in buffer:
					index = int((float(sample) - float(pmin)) / freq)
					if index == bin_size:
						index = bin_size - 1
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
	
	def MovingAvarage(self, buffer, win):
		window_size = win
		i = 0
		moving_averages = []

		pmin, pmax = self.FindBufferMaxMin(buffer)
		while i < len(buffer):
			if i > window_size - 1:
				this_window = buffer[i - window_size : i]
				window_average = sum(this_window) / window_size
				moving_averages.append(window_average)
			else:
				moving_averages.append(pmin)
			i += 1
		
		x_scale = [x for x in range(0, len(moving_averages))]
		return moving_averages, x_scale
	
	def GetIntersetPoints(self, data):
		data_diff = []
		roi_list  = []

		pmin, pmax = self.FindBufferMaxMin(data)
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
		error, hist_y, hist_x = self.CreateHistogram(data_diff, len(data_diff))

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
