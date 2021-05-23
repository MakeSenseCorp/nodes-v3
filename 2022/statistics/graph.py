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

def GetMAX(ticker):
	hist = []
	objtk = yf.Ticker(ticker)
	data = objtk.history(period="max")
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

def Get5D(ticker):
	'''
		Open,High,Low,Close,Volume,Dividends,Stock Splits
	'''
	hist = []
	objtk = yf.Ticker(ticker)
	data = objtk.history(period="3mo", interval="60m")
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

def Get1MO(ticker):
	'''
		Open,High,Low,Close,Volume,Dividends,Stock Splits
	'''
	hist = []
	objtk = yf.Ticker(ticker)
	data = objtk.history(period="1mo")
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

def GetStockInfo(ticker):
	objtk = yf.Ticker(ticker)

	ask  = 0
	bid  = 0
	high = 0
	low  = 0

	if type(objtk.info["ask"]) == dict:
		ask = objtk.info["ask"]["raw"]
	else:
		ask = objtk.info["ask"]
	
	if type(objtk.info["bid"]) == dict:
		bid = objtk.info["bid"]["raw"]
	else:
		bid = objtk.info["bid"]
	
	if type(objtk.info["dayHigh"]) == dict:
		high = objtk.info["dayHigh"]["raw"]
	else:
		high = objtk.info["dayHigh"]
	
	if type(objtk.info["dayLow"]) == dict:
		low = objtk.info["dayLow"]["raw"]
	else:
		low = objtk.info["dayLow"]

	return {
		"ask": ask,
		"bid": bid,
		"high": high,
		"low": low
	}

def CalculateMinMax(data):
	pmax = 0
	pmin = 0
	if len(data) > 0:
		pmin = data[0]["close"]
		for item in data:
			if pmax < item["close"]:
				pmax = item["close"]
			if pmin > item["close"]:
				pmin = item["close"]
	return pmin, pmax

def CalculateRegression(coordinates):
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
		
	slope = (y_dist_2_sum) / (x_dist_2_sum)
	b = avg_y - slope * avg_x

	return slope, b
	
def RValue(coordinates, slope, b):
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
	
	r = float(estimated_y_dist_2_sum) / float(y_dist_2_sum)
	return r

def Variance(data, ddof=0):
	n = len(data)
	mean = sum(data) / n
	return sum((x - mean) ** 2 for x in data) / (n - ddof)

def Stdev(data):
	var = Variance(data)
	std_dev = math.sqrt(var)
	return std_dev

def LoadLocalStockJsonDB(path):
	global g_StocksDB
	str_data = Load(path)
	json_data = json.loads(str_data)
	g_StocksDB = json_data["stocks"]

def GetRegressionLineStatistics(data):
	line = []
	for idx, item in enumerate(data):
		line.append({
			"y": item["close"],
			"x": idx
		})
	slope, b = CalculateRegression(line)
	r2 = RValue(line, slope, b)
	return slope, b, r2

def GetBasicStatistics(data):
	line = []
	for item in data:
		line.append(item["close"])
	var = Variance(line)
	std = Stdev(line)
	return var, std

def OutBasicStatistics(m_std,m_var,w_std,w_var,ticker,w_slope,w_b,w_r2,m_slope,m_b,m_r2,wmax,wmin,mmin,mmax,dhigh,dlow,ask,bid):
	output = '''
***********************************************************************
Ticker: {ticker}
Price: 
	Daily:		Max	Min	ASK	BID
			---	---	---	---
			{dhigh:.2f}	{dlow:.2f}	{ask:.2f}	{bid:.2f}

	Weekly:		Max	Min	Slope	B	Correlation 	VAR	STD
			---	---	-----	------	-----------	------	------
			{wmax:.2f}	{wmin:.2f}	{w_slope:.2f}	{w_b:.2f}	{w_r2:.2f}		{w_var:.2f}	{w_std:.2f}
			
	Monthly:	Max	Min	Slope	B	Correlation 	VAR	STD
			---	---	-----	------	-----------	------	------
			{mmax:.2f}	{mmin:.2f}	{m_slope:.2f}	{m_b:.2f}	{m_r2:.2f}		{m_var:.2f}	{m_std:.2f}
***********************************************************************\n
	'''.format(m_std=m_std,m_var=m_var,w_std=w_std,w_var=w_var,ticker=ticker,w_slope=w_slope,w_b=w_b,w_r2=w_r2,m_slope=m_slope,m_b=m_b,m_r2=m_r2,wmax=wmax,wmin=wmin,mmin=mmin,mmax=mmax,dhigh=dhigh,dlow=dlow,ask=ask,bid=bid)
	print(output)

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

def main():
	parser = argparse.ArgumentParser(description='Stock DB Creator')
	parser.add_argument('--update', action='store_true', help='Update DB')
	parser.add_argument('--ticker', action='store', dest='ticker', help='Calculate single ticker')
	parser.add_argument('--plot', action='store_true', help='Update DB')
	args = parser.parse_args()

	if args.ticker is not None:
		x1 = []
		y1 = []
		x2 = []
		y2 = []
		x3 = []
		y3 = []
		x4 = []
		y4 = []
		x5 = []
		y5 = []
		x6 = []
		y6 = []
		x7 = []
		y7 = []

		#fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
		fig, (ax1) = plt.subplots(1, 1)
		fig.subplots_adjust(hspace=0.5)

		ticker = args.ticker
		data = Get5D(ticker)

		# Build y scale (close data)
		for idx, item in enumerate(data):
			y1.append(item["close"])
		
		y1, x1 = MAVG(y1, 10)
		y4, x4 = MAVG(y1, 50)
		y5, x5 = MAVG(y1, 20)
		pmin, pmax = FindBufferMaxMin(y1)
		avg = (pmax + pmin) / 2

		# Build x scale
		#for idx, item in enumerate(y1):
		#	x.append(idx)
		
		diff_arr = np.array(y1, dtype=np.double)
		y2 = np.diff(diff_arr, n=1).tolist()

		# ------------------------------------------------------------------ DIFF REMOVE POSITIVE SLOPE START
		for idx, item in enumerate(y2):
			if item > 0:
				y2[idx] = 0
		# ------------------------------------------------------------------ DIFF REMOVE POSITIVE SLOPE END

		# ------------------------------------------------------------------ HISTOGRAM START
		error, Y, X = CreateHistogram(y2, len(y2))

		hist_sum = 0.0
		for sample in Y:
			hist_sum += sample

		filter_thershold = 0.0
		perc_integral = 0.0
		for idx, sample in enumerate(Y):
			perc_integral += sample
			if (perc_integral / hist_sum) > 0.3:
				filter_thershold = X[idx]
				break
		# ------------------------------------------------------------------ HISTOGRAM END

		# ------------------------------------------------------------------ DIFF REMOVE NOISE START
		for idx, item in enumerate(y2):
			if item > filter_thershold:
				y2[idx] = 0
		# ------------------------------------------------------------------ DIFF REMOVE NOISE END

		#ax2.plot(x1[:-1], y2)

		# ------------------------------------------------------------------ FIND GROUPS START
		roi_list = []
		start_of_peak 	= 0
		item_counter 	= 0
		prev_item 		= 0
		scale_const = (pmax - pmin) / 8
		for idx, item in enumerate(y2):
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
				else:
					roi_list.append({
						"start": start_of_peak,
						"end": idx
					})
				# Start items counter
				item_counter = 0
			else:
				# ANY OTHER CASE
				pass

			prev_item = item
		
		y6 = [pmin] * len(y2)
		for item in roi_list:
			for idx in range(item["start"], item["end"]):
				y6[idx] = pmin + scale_const
		# ------------------------------------------------------------------ FIND GROUPS END
		
		# ------------------------------------------------------------------ DIFF SCALE TO GRAPH START
		scale_const = (pmax - pmin) / 2
		#y7 = [((scale_const * ((0 - x) / scale_const) * 4) + avg) for x in y2]
		#y2 = [((scale_const * (x / scale_const) * 4) + avg) for x in y2]
		y7 = [((scale_const * ((0 - x) / scale_const) * 4) + pmin) for x in y2]
		y2 = [((scale_const * (x / scale_const) * 4) + pmax) for x in y2]
		# ------------------------------------------------------------------ DIFF SCALE TO GRAPH END

		ax1.plot(x1, y1)
		ax1.plot(x1[:-1], y2, color='orange')
		ax1.plot(x1[:-1], y7, color='orange')
		ax1.plot(x1[:-1], y6, color='red')
		ax1.plot(x4, y4, color='red', linestyle='dashed')
		ax1.plot(x5, y5, color='green', linestyle='dashed')

		#ax3.plot(X, Y)
		#ax4.plot(x4, y4, color='red')
		#ax4.plot(x5, y5, color='green')
	
		plt.show()
	
	return

	if args.ticker is not None:
		fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
		fig.subplots_adjust(hspace=0.5)

		ticker = args.ticker
		stock_info 	= GetStockInfo(ticker) # Get stock info
		
		data = Get5D(ticker) # 5 Day history price
		wmin, wmax = CalculateMinMax(data)
		w_slope, w_b, w_r2 = GetRegressionLineStatistics(data)
		w_var, w_std = GetBasicStatistics(data)

		x  = []
		y1 = []
		y2 = []
		y3 = []
		for idx, item in enumerate(data):
			x.append(idx)
			y1.append(item["high"])
			y2.append(item["low"])
			y3.append(item["close"])
		ax1.plot(x, y1, x, y2, x, y3)

		data = Get1MO(ticker) # One month history price
		mmin, mmax = CalculateMinMax(data)
		m_slope, m_b, m_r2 = GetRegressionLineStatistics(data)
		m_var, m_std = GetBasicStatistics(data)

		x  = []
		y1 = []
		y2 = []
		y3 = []
		for idx, item in enumerate(data):
			x.append(idx)
			y1.append(item["high"])
			y2.append(item["low"])
			y3.append(item["close"])
		ax2.plot(x, y1, x, y2, x, y3)

		y = []
		x = []
		data = GetMAX(ticker) # Max days history price
		for idx, item in enumerate(data):
			x.append(idx)
			if idx == 0:
				y.append(0)
			else:
				y.append(data[idx-1]["close"]/item["close"]-1)
		ax3.plot(x, y)

		OutBasicStatistics(m_std,m_var,w_std,w_var,ticker,w_slope,w_b,w_r2,m_slope,m_b,m_r2,wmax,wmin,mmin,mmax,stock_info["high"],stock_info["low"],stock_info["ask"],stock_info["bid"])
		plt.show()
		return
	
	path_csv = os.path.join("output","csv")
	for stock in g_StocksDB:
		ticker 		= stock["ticker"]
		stock_info 	= GetStockInfo(ticker) # Get stock info
		
		data = Get5D(ticker) # 5 Day history price
		wmin, wmax = CalculateMinMax(data)
		w_slope, w_b, w_r2 = GetRegressionLineStatistics(data)
		w_var, w_std = GetBasicStatistics(data)

		data = Get1MO(ticker) # One month history price
		mmin, mmax = CalculateMinMax(data)
		m_slope, m_b, m_r2 = GetRegressionLineStatistics(data)
		m_var, m_std = GetBasicStatistics(data)
		OutBasicStatistics(m_std,m_var,w_std,w_var,ticker,w_slope,w_b,w_r2,m_slope,m_b,m_r2,wmax,wmin,mmin,mmax,stock_info["high"],stock_info["low"],stock_info["ask"],stock_info["bid"])

		now = datetime.now()
		date_str = now.strftime("%m-%d-%Y 00:00:00")
		if args.update is True:
			ticker_path = os.path.join(path_csv,"{0}.csv".format(ticker))
			if os.path.isfile(ticker_path) is False:
				Append(ticker_path,"date,Daily Max,Daily Min,ASK,BID,,Weekly Max,Weekly Min,Weekly Slope,Weekly B,Weekly Correlation,Weekly VAR,Weekly STD,,Monthly Max,Monthly Min,Monthly Slope,Monthly B,Monthly Correlation,Monthly VAR,Monthly STD\n")
			row = "{date_str},{dhigh:.2f},{dlow:.2f},{ask:.2f},{bid:.2f},,{wmax:.2f},{wmin:.2f},{w_slope:.2f},{w_b:.2f},{w_r2:.2f},{w_var:.2f},{w_std:.2f},,{mmax:.2f},{mmin:.2f},{m_slope:.2f},{m_b:.2f},{m_r2:.2f},{m_var:.2f},{m_std:.2f}\n".format(date_str=date_str,m_std=m_std,m_var=m_var,w_std=w_std,w_var=w_var,ticker=ticker,w_slope=w_slope,w_b=w_b,w_r2=w_r2,m_slope=m_slope,m_b=m_b,m_r2=m_r2,wmax=wmax,wmin=wmin,mmin=mmin,mmax=mmax,dhigh=stock_info["high"],dlow=stock_info["low"],ask=stock_info["ask"],bid=stock_info["bid"])
			Append(ticker_path,row)

if __name__ == "__main__":
	main()

'''
Get DataFrame from Yahoo:
	objtk = yf.Ticker(ticker)
	data  = objtk.history(period="5d")
DataFrame information:
	data.info()
Last and First five rows of DataFrame:
	data.head() or data.head(20) [20 rows]
	data.tail() or data.tail(20) [20 rows]
Create DataFrame and append columns:
	frame = pd.DataFrame()
	for ticker in ["GE","AAPL","TSLA"]:
		frame[ticker] = range(20)
Read row - 1 from DataFrame
	df.shift(1)

Math operations:
	def.mean()



PANDAS DATAREADER
-----------------
	from pandas_datareader import data as wb
	dbDataFrame = wb.DataReader('TSLA', datasource='iex', start='1995-11-30')

PANDAS CSV/EXCEL
----------
	data = pd.read_csv('PATH') # data = pd.read_csv('PATH', index_col='COL_NAME')
	data.head()
	data.tail()
	data.to_csv('PATH')
	data = pd.read_excel('PATH')
	data.to_excel('PATH')

QUANDL
------
	import quandl
	data = quandl.get('FRED/GDP')
'''