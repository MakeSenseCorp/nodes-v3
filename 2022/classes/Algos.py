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

class AlgoBasicPrediction():
	def __init__(self):
		self.ClassName 				= "AlgoBasicPrediction"
		self.Math 					= AlgoMath()
		self.HistogramWindowSize 	= 25
		self.PercentileLow 			= 0.15
		self.PercentileHigh 		= 0.85
		self.Buffer 				= None
	
	def SetBuffer(self, buffer):
		self.Buffer = buffer
	
	def Execute(self):
		error, Y, X = self.Math.CreateHistogram(self.Buffer, self.HistogramWindowSize)
		if error != 0 or len(X) == 0:
			return -1, {
				"output": {
					"x"				: [],
					"y"				: [],
					"index_min"		: 0,
					"index_low"		: 0,
					"index_middle"	: 0,
					"index_high"	: 0,
					"index_max"		: 0
				}
			}
		
		idxMIN, idxLOW, idxMID, idxHIGH, idxMAX = self.Math.CalculatePercentile(self.PercentileLow, self.PercentileHigh, Y)

		return 0, {
			"output": {
				"x"				: X,
				"y"				: Y,
				"index_min"		: idxMIN,
				"index_low"		: idxLOW,
				"index_middle"	: idxMID,
				"index_high"	: idxHIGH,
				"index_max"		: idxMAX
			}
		}