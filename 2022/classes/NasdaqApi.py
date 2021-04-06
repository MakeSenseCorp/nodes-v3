#!/usr/bin/python
import os
import sys
import signal
import json
import time
import urllib.request

class Nasdaq():
    __init__(self):
        self.ClassName = "Nasdaq"
    
    def UpcommingEvents(self):
        json = urllib.request.urlopen("https://api.nasdaq.com/api/calendar/upcoming")
        return ""