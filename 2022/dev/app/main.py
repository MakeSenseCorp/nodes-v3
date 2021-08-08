#!/usr/bin/python
import signal
import argparse
import time
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import _thread
import json
import subprocess

import MkSLogger
import StockMarketAPI
import NasdaqApi
import AlgoMath
import MkSLocalWebServer

class Task():
	def __init__(self, name):
		self.TaskEnabled 	= False
		self.Running 		= False
		self.Paused 		= False
		self.Logger 		= MkSLogger.Logger(name)

		self.Logger.EnablePrint()
		self.Logger.SetLogLevel(1)
		self.Logger.EnableLogger()

	def Start(self):
		if self.TaskEnabled is False:
			self.TaskEnabled = True
			_thread.start_new_thread(self.WorkerThread, ())
		
		self.Paused  = False

	def Stop(self):
		if self.Running is True:
			self.Logger.Log("Thread STOP", 1)
			self.Running = False
	
	def Pause(self):
		self.Logger.Log("Thread PAUSE", 1)
		self.Paused = True
	
	def Resume(self):
		self.Logger.Log("Thread RESUME", 1)
		self.Paused = False
	
	def WorkerThread(self):
		self.Logger.Log("Thread START", 1)
		self.Running = True
		while self.Running is True:
			if self.Paused is False:
				self.Handler()
		self.TaskEnabled = False
		self.Logger.Log("Thread EXIT", 1)

	def Handler(self):
		pass

class BounderiesTask(Task):
	def __init__(self):
		Task.__init__(self, "BounderiesTask")
		self.Name 					= "BounderiesTask"
		self.Limits 				= StockBounderies()
		self.MainLoopInterval		= 10
		self.StockUpdateInterval	= 60 * 5
		self.StockInterval 			= 1
		self.Tickers 				= [
			{
				"ticker": "aapl",
				"timestamp": 0.0
			},
			{
				"ticker": "tsla",
				"timestamp": 0.0
			},
			{
				"ticker": "intc",
				"timestamp": 0.0
			},
			{
				"ticker": "fb",
				"timestamp": 0.0
			},
			{
				"ticker": "t",
				"timestamp": 0.0
			}
		]
	
	def Handler(self):
		for ticker in self.Tickers:
			if time.time() - ticker["timestamp"] > self.StockUpdateInterval:
				self.Logger.Log("Query {0} stock".format(ticker["ticker"]), 1)
				data = self.Limits.Calculate(ticker["ticker"])
				self.Limits.Print(self.Logger, data)

				time.sleep(self.StockInterval)
				ticker["timestamp"] = time.time()
		time.sleep(self.MainLoopInterval)

class StockBounderies():
	def __init__(self):
		self.StockApi		= StockMarketAPI.API()
		self.Math			= AlgoMath.AlgoMath()
		self.Yesturday 		= None
		self.Week 			= None
		self.Month 			= None
		self.ThreeMonths	= None
		self.SixMonths		= None
		self.Year 			= None
		self.Price 			= 0.0

	def GetYesturday(self, ticker):
		yesturday 	= []
		week 		= []
		status, hist = self.StockApi.GetStockHistory(ticker, "5d", "1h")
		if status is True:
			print("Failed with 5days history data request.")
		else:
			# Each 7 row represent day
			current_date = dt.datetime.now().date()
			prev_date = current_date
			slots_count = 0
			
			for item in hist[::-1]:
				date = dt.datetime.strptime(item["date"].split(" ")[0], '%Y-%m-%d').date()
				if (prev_date != date):
					if slots_count == 0:
						# first time, means yesturday
						pass
					slots_count += 1
					# print("CHANGE")
				prev_date = date
				if slots_count == 1:
					yesturday.append(item)
					week.append(item)
					#print("D: {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
				elif slots_count >= 1:
					week.append(item)
					#print("W: {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
		
		self.Yesturday 	= yesturday
		self.Week 		= week
		return yesturday
	
	def GetMonth(self, ticker):
		month 		= []
		three_monts = []
		six_months 	= []
		year 		= []
		status, hist = self.StockApi.GetStockHistory(ticker, "1y", "1d")
		if status is True:
			print("Failed with 5days history data request.")
		else:
			today_date = dt.datetime.now().date()
			date_count = 0
			for item in hist[::-1]:
				date = dt.datetime.strptime(item["date"].split(" ")[0], '%Y-%m-%d').date()
				if (today_date == date):
					continue
				
				if date_count < 22:
					month.append(item)
					three_monts.append(item)
					six_months.append(item)
					#print("D: {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
				elif date_count < 66:
					three_monts.append(item)
					six_months.append(item)
					#print("W: {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
				elif date_count < 132:
					six_months.append(item)
					#print("W: {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
				else:
					pass
				year.append(item)
				date_count += 1

		self.Month 			= month
		self.ThreeMonths	= three_monts
		self.SixMonths		= six_months
		self.Year			= year
		return month
	
	def ConvertToCoordinates(self, hist):
		x = []
		y = []
		for idx, item in enumerate(hist):
			x.append(idx)
			y.append(item["close"])
		return x, y
	
	def CalculateYesturday(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			hist = self.GetYesturday(ticker)
			x, y = self.ConvertToCoordinates(hist)

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "Day",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": hist[0]["close"],
					"low": hist[0]["close"] - stop_loss,
					"high": hist[0]["close"] + stop_loss
				}
			}
		return None
	
	def CalculateWeek(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			if self.Week is None:
				self.CalculateYesturday(ticker)
			
			x, y = self.ConvertToCoordinates(self.Week)
			#for item in self.Week:
			#	print("   {0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "Week",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": self.Week[0]["close"],
					"low": self.Week[0]["close"] - stop_loss,
					"high": self.Week[0]["close"] + stop_loss
				},
				"x": x,
				"y": y
			}
		return None
	
	def CalculateMonth(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			hist = self.GetMonth(ticker)
			x, y = self.ConvertToCoordinates(hist)

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "Month",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": hist[0]["close"],
					"low": hist[0]["close"] - stop_loss,
					"high": hist[0]["close"] + stop_loss
				},
				"x": x,
				"y": y
			}
		return None

	def Calculate3Month(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			if self.ThreeMonths is None:
				self.GetMonth(ticker)
			x, y = self.ConvertToCoordinates(self.ThreeMonths)

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "3 Months",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": self.ThreeMonths[0]["close"],
					"low": self.ThreeMonths[0]["close"] - stop_loss,
					"high": self.ThreeMonths[0]["close"] + stop_loss
				},
				"x": x,
				"y": y
			}
		return None

	def Calculate6Month(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			if self.SixMonths is None:
				self.GetMonth(ticker)
			x, y = self.ConvertToCoordinates(self.SixMonths)

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "6 Months",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": self.SixMonths[0]["close"],
					"low": self.SixMonths[0]["close"] - stop_loss,
					"high": self.SixMonths[0]["close"] + stop_loss
				},
				"x": x,
				"y": y
			}
		return None

	def CalculateYear(self, ticker):
		status, price = self.StockApi.GetStockCurrentPrice(ticker)
		if status is False:
			if self.Year is None:
				self.GetMonth(ticker)
			x, y = self.ConvertToCoordinates(self.Year)

			std = self.Math.Stdev(y)
			p_min, p_max = self.Math.FindBufferMaxMin(y)
			stop_loss = ((p_max - p_min) / 2) * 0.8

			return {
				"ticker": ticker,
				"name": "Year",
				"price": price,
				"min": p_min,
				"max": p_max,
				"std": std,
				"amp": stop_loss,
				"limit": {
					"price": self.Year[0]["close"],
					"low": self.Year[0]["close"] - stop_loss,
					"high": self.Year[0]["close"] + stop_loss
				},
				"x": x,
				"y": y
			}
		return None

	def Calculate(self, ticker):
		yesturday 		= self.CalculateYesturday(ticker)
		week 			= self.CalculateWeek(ticker)
		month 			= self.CalculateMonth(ticker)
		three_months 	= self.Calculate3Month(ticker)
		six_months 		= self.Calculate6Month(ticker)
		year 			= self.CalculateYear(ticker)
		
		return yesturday, week, month, three_months, six_months, year
	
	def Print(self, logger, data):

		logger.Log("Type\t\tPrice\tMIN\tMAX\tSTD\tAMP\tPrice\tLow\tHigh", 1)
		logger.Log("----\t\t-----\t---\t---\t---\t---\t-----\t---\t----", 1)
		for idx, item in enumerate(data):
			if item is not None:
				if item["name"] not in ["3 Months", "6 Months"]:
					logger.Log("{0}\t\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}\t{7:.2f}\t{8:.2f}".format(item["name"], item["price"], item["min"], item["max"], item["std"], item["amp"], item["limit"]["price"], item["limit"]["low"], item["limit"]["high"]), 1)
				else:
					logger.Log("{0}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}\t{7:.2f}\t{8:.2f}".format(item["name"], item["price"], item["min"], item["max"], item["std"], item["amp"], item["limit"]["price"], item["limit"]["low"], item["limit"]["high"]), 1)

class Terminal():
	def __init__(self):
		self.ProcessRunning = True
		self.StockApi 	= StockMarketAPI.API()
		self.NasdaqApi 	= NasdaqApi.Nasdaq()
		self.Math 		= AlgoMath.AlgoMath()
		self.Limits 	= StockBounderies()
		self.Handlers = {
			"help": 					self.HelpHandler,
			"list": 					self.ListHandler,
			"price":					self.PriceHandler,
			"history": 					self.HistoryHandler,
			"nasdaq": 					self.NasdaqHandler,
			"graph": 					self.GraphHandler,
			"mavg_buy":					self.MovingAvarageBuyHandler,
			"bounderies": 				self.BounderiesHandler,
			"task":						self.TasksHandler,
			"app":						self.AppHandler,
			"exit": 					self.ExitHandler
		}
		self.LastHistoryBuffer = None
		self.Tasks = {
			"bounderies": BounderiesTask()
		}
	
	def IsMarketOpen(self):
		currTime = dt.datetime.now().time()
		return (currTime > dt.time(16,25) and currTime < dt.time(23,5))

	def CalculateStopLoss(self, ticker):
		colors = ["green", "orange", "navy", "purple", "steelblue", "tomato"]
		x_axis = []
		y_axis = []
		status, hist = self.StockApi.GetStockHistory(ticker, "1d", "30m")
		if status is False:
			fig, (ax) = plt.subplots(1, 1)
			fig.subplots_adjust(hspace=0.5)

			for idx, item in enumerate(hist):
				x_axis.append(idx)
				y_axis.append(item["close"])
				ax.plot(x_axis, y_axis, color="blue")

			data = self.Limits.Calculate(ticker)
			print("Type\t\tPrice\tMIN\tMAX\tSTD\tAMP\tPrice\tLow\tHigh")
			print("----\t\t-----\t---\t---\t---\t---\t-----\t---\t----")
			for idx, item in enumerate(data):
				if item is not None:
					if item["name"] not in ["3 Months", "6 Months"]:
						print("{0}\t\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}\t{7:.2f}\t{8:.2f}".format(item["name"], item["price"], item["min"], item["max"], item["std"], item["amp"], item["limit"]["price"], item["limit"]["low"], item["limit"]["high"]))
					else:
						print("{0}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}\t{7:.2f}\t{8:.2f}".format(item["name"], item["price"], item["min"], item["max"], item["std"], item["amp"], item["limit"]["price"], item["limit"]["low"], item["limit"]["high"]))
					if item["name"] not in ["Year", "6 Months", "3 Months"]:
						ax.plot(x_axis, [item["limit"]["high"]]*len(x_axis), color=colors[idx], label=item["name"], linestyle='dashed')
						ax.plot(x_axis, [item["limit"]["low"]]*len(x_axis), color=colors[idx])

			plt.legend()
			plt.show()

	def Close(self):
		pass
	
	def UndefinedHandler(self, data):
		pass

	def ExitHandler(self, data):
		self.ProcessRunning = False

	def TasksHandler(self, data):
		if len(data) > 1:
			name 		= data[0]
			action 		= data[1]

			if name in self.Tasks:
				task = self.Tasks[name]
				if action == "start":
					task.Start()
				elif action == "stop":
					task.Stop()
				elif action == "pause":
					task.Pause()
				elif action == "resume":
					task.Resume()
				else:
					pass
		else:
			print("Wrong parameter")
	
	def BounderiesHandler(self, data):
		if len(data) > 0:
			ticker = data[0]
			self.CalculateStopLoss(ticker)
		else:
			print("Wrong parameter")
	
	def MovingAvarageBuyHandler(self, data):
		if len(data) > 2:
			ticker 		= data[0]
			period 		= data[1]
			interval 	= data[2]
			status, price = self.StockApi.GetStockCurrentPrice(ticker)
			if status is False:
				'''
					Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
					Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
				'''
				status, hist = self.StockApi.GetStockHistory(ticker, period, interval)
				if status is True:
					print("Request FAILED.")
				else:
					x_axis = []
					y_axis = []
					for idx, item in enumerate(hist):
						x_axis.append(idx)
						y_axis.append(item["close"])
					window = 8
					y_buff, x_buff = self.Math.MovingAvarage(y_axis, window)

					# True  - Original > Average
					# False - Original < Average
					
					action 		= "NONE"
					last_price	= 0.0
					overall 	= 0.0
					avg 		= y_buff[window:]
					state 		= y_axis[window] > avg[0]
					for idx, item in enumerate(y_axis[window:]):
						new_state = item > avg[idx]
						if state != new_state:
							if new_state == False:
								if action == "BUY":
									action = "SELL"
									overall += item
								else:
									pass
							else:
								action = "BUY"
								overall -= item
							
							print(str(idx + window), action, item)
							last_price = item
							state = new_state
					
					if action == "BUY":
						overall += last_price

					print("Overall", overall)
					fig, (ax) = plt.subplots(1, 1)
					fig.subplots_adjust(hspace=0.5)

					ax.plot(x_axis, y_axis, color='blue')
					ax.plot(x_axis, y_buff, color='orange')
					plt.show()
		else:
			print("Wrong parameter")
	
	def NasdaqHandler(self, data):
		if len(data) > 0:
			action = data[0]
			if action == "articles":
				articles = self.NasdaqApi.RecentArticles(10)
				for item in articles:
					print("{0} {1}".format(item["ago"], item["title"]))
		else:
			print("Wrong parameter")
	
	def PriceHandler(self, data):
		if len(data) > 0:
			ticker = data[0]
			status, price = self.StockApi.GetStockCurrentPrice(ticker)
			if status is True:
				print("Request FAILED.")
			else:
				print(price)
		else:
			print("Wrong parameter")

	def GraphHandler(self, data):
		if len(data) > 2:
			ticker 		= data[0]
			period 		= data[1]
			interval 	= data[2]
			status, price = self.StockApi.GetStockCurrentPrice(ticker)
			if status is False:
				'''
					Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
					Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
				'''
				status, hist = self.StockApi.GetStockHistory(ticker, period, interval)
				if status is True:
					print("Request FAILED.")
				else:
					x_axis = []
					y_axis = []
					for idx, item in enumerate(hist):
						# x_axis.append(time.mktime(datetime.strptime(item["date"], '%Y-%m-%d %H:%M:%S').timetuple()))
						x_axis.append(idx)
						y_axis.append(item["close"])
					
					std = self.Math.Stdev(y_axis)
					p_min, p_max = self.Math.FindBufferMaxMin(y_axis)
					stop_loss = ((p_max - p_min) / 2) * 0.8

					print("Price CUR: {2:.1f}\nPrice MIN: {0:.1f}\nPrice MAX: {1:.1f}\nStop Loss: {3:.1f} ({4:.1f})".format(p_min, p_max, price, stop_loss, price - stop_loss))
					print("STD: {0:.1f} ({1:.1f} - {2:.1f})".format(std, price - std, price + std))

					price_axis = [price]*len(hist)
					stop_loss_axis = [price - stop_loss]*len(hist)

					y_buff, x_buff = self.Math.MovingAvarage(y_axis, 5)

					# dt_left  = dt.datetime.strptime(x_axis[0], '%Y-%m-%d %H:%M:%S')
					# dt_right = dt.datetime.strptime(x_axis[-1], '%Y-%m-%d %H:%M:%S')

					fig, (ax) = plt.subplots(1, 1)
					fig.subplots_adjust(hspace=0.5)

					# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
					# plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
					# plt.gca().set_xbound(dt_left, dt_right)

					ax.plot(x_axis, y_axis, color='blue')
					ax.plot(x_axis, price_axis, color='green')
					ax.plot(x_axis, stop_loss_axis, color='red', linestyle='dashed')
					ax.plot(x_axis, y_buff, color='orange')

					# plt.gcf().autofmt_xdate()
					plt.show()
		else:
			print("Wrong parameter")

	def HistoryHandler(self, data):
		if len(data) > 2:
			ticker 		= data[0]
			period 		= data[1]
			interval 	= data[2]
			'''
				Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
				Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
			'''
			status, hist = self.StockApi.GetStockHistory(ticker, period, interval)
			if status is True:
				print("Request FAILED.")
			else:
				self.LastHistoryBuffer = hist
				for item in hist:
					print("{0} {1:.1f} {2:.1f} {3}".format(item["date"], item["open"], item["close"], item["vol"]))
		else:
			print("Wrong parameter")

	def ListHandler(self, data):
		pass

	def AppHandler(self, data):
		subprocess.call(["ui.cmd"])
	
	def HelpHandler(self, data):
		print('''
	Periods:\t1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
	Intervals:\t1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo\n
	list\t\tList all monitored stockes.\n
	price\t\tPrint price of a ticker.\n
	history\t\tPrint history of a ticker.\n
	nasdaq\t\tNasdaq.\n
	graph\t\tShow graph of a stock.\n
	mavg_buy\tCalculate earning for basic moving avarage change.\n
	bounderies\tShow limit bounderies [day, week, month, 3months, 6months, year]\n
	task\t\tTerminal can execute predefined tasks. (Type 'task list' for available tasks)\n
	exit\t\tExit application.\n
		''')
	
	def IntToBytes(self, value, length):
		byte_array = []
		while value != 0:
			byte_array = [value % 256] + byte_array
			value = value // 256
		
		# ATMEL will read data from left to right
		byte_array = byte_array + [0]*(length-len(byte_array))
		return byte_array

def signal_handler(signal, frame):
	pass
	
def main():
	signal.signal(signal.SIGINT, signal_handler)

	parser = argparse.ArgumentParser(description='Execution module called Node \n Example: python.exe main.py')
	parser.add_argument('-v', '--version', action='store_true',
			help='Version')
	parser.add_argument('-verb', '--verbose', action='store_true',
			help='Print messages')
	
	args = parser.parse_args()
	terminal = Terminal()

	# Data for the pages.
	web_data 	= {
		'ip': str("localhost"),
		'port': str(1981)
	}
	data = json.dumps(web_data)
	web	= MkSLocalWebServer.WebInterface("Context", 8181)
	web.AddEndpoint("/", "index", None, data)
	web.Run()

	try:
		while(terminal.ProcessRunning is True):
			raw  	= input('> ')
			data 	= raw.split(" ")
			cmd  	= data[0]
			params 	= data[1:]

			if cmd in terminal.Handlers:
				terminal.Handlers[cmd](params)
			else:
				if cmd not in [""]:
					print("unknown command")
	except Exception as e:
		print("{0}".format(e))

	terminal.Close()
	print("Bye.")

if __name__ == "__main__":
    main()
