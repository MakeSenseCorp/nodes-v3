#!/usr/bin/python
import signal
import argparse

from classes import terminal
from classes import application
from classes import nrf

def signal_handler(signal, frame):
	pass

class Node():
	def __init__(self):
		pass
	
def main():
	signal.signal(signal.SIGINT, signal_handler)

	parser = argparse.ArgumentParser(description='Execution module called Node \n Example: python.exe main.py --serial COM31')
	parser.add_argument('-v', '--version', action='store_true',
			help='Version')
	parser.add_argument('-cn', '--serial', action='store',
			dest='serial', help='Serial COM to connect')
	parser.add_argument('-verb', '--verbose', action='store_true',
			help='Print messages')
	
	args = parser.parse_args()

	cli 		= terminal.Terminal()
	app 		= application.Application()
	gateway 	= nrf.NRF()

	app.RegisterHardware(gateway)
	cli.RegisterHardware(gateway)
	cli.RegisterApplication(app)

	# gateway.RegisterListener(cli.AsyncDataArrived)
	gateway.RegisterListener(app.AsyncDataArrived)

	app.Run()
	cli.Run() # Blocking
	
	cli.Close()
	print("Bye.")

if __name__ == "__main__":
    main()
