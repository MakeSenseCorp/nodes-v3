#!/usr/bin/python
import os
import sys
import json
import time
import base64
import datetime
from datetime import date
import math

from classes import AlgoMath

class BasicPrediction():
	def __init__(self):
		self.ClassName 				= "BasicPrediction"
		self.Math 					= AlgoMath.AlgoMath()
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