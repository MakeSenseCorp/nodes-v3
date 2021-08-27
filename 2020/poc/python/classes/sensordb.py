#!/usr/bin/python
import os
import sqlite3

class SensorDB():
	def __init__(self, path):
		path = os.path.join("", path)
		self.ClassName	= "SensorDB"
		self.DB 		= sqlite3.connect(path, check_same_thread=False)
		self.CURS		= self.DB.cursor()

		self.BuildSchema()
	
	def BuildSchema(self):
		'''
			leftovers - How many stock still available for this buy.
		'''
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "sensor_info" (
							"id"			INTEGER PRIMARY KEY AUTOINCREMENT,
							"type"			INTEGER NOT NULL,
							"sensor_id"		INTEGER,
							"name"			TEXT,
							"description"	TEXT,
							"enabled"		INTEGER
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "sensor_value" (
							"id" 			INTEGER NOT NULL,
							"sensor_id"		INTEGER NOT NULL,
							"value"			REAL,
							"timestamp"		REAL
						);''')

		self.Init()

	def Init(self):
		pass

	def SensorExist(self, id):
		try:
			query = "SELECT * FROM sensor_info WHERE id={0}".format(id)
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				return True
		except Exception as e:
			pass
		return False

	def GetSensors(self):
		sensors = []
		query 	= "SELECT * FROM sensor_info"
		try:
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					sensors.append({
						"id": 			row[0],
						"type": 		row[1],
						"sensor_id": 	row[2],
						"name": 		row[3],
						"description": 	row[4],
						"enabled": 		row[5]
					})
		except Exception as e:
			pass
		return sensors
	
	def GetSensorById(self, id):
		try:
			query = "SELECT * FROM sensor_value WHERE id={0}".format(id)
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				return {
					"id": 			rows[0][0],
					"type": 		rows[0][1],
					"sensor_id": 	rows[0][2],
					"name": 		rows[0][3],
					"description": 	rows[0][4],
					"enabled": 		rows[0][5]
				}
		except Exception as e:
			pass
		return None
	
	def GetSensorHistory(self, id):
		history = []
		query 	= "SELECT * FROM sensor_info"
		try:
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					history.append({
						"id": 			row[0],
						"sensor_id": 	row[1],
						"value": 		row[2],
						"timestamp": 	row[3]
					})
		except Exception as e:
			pass
		return history

	def InsertSensor(self, sensor):
		try:
			query = '''
				INSERT INTO stocks_info (id, type, sensor_id, name, description, enabled)
				VALUES (NULL,{0},{1},'{2}','{3}',1)
			'''.format(sensor["type"],sensor["sensor_id"],sensor["name"],sensor["description"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			pass
		return None
	
	def DeleteSensor(self, id):
		try:
			self.CURS.execute('''
				DELETE FROM sensor_info
				WHERE id = {0}
			'''.format(id))
			self.DB.commit()

			self.CURS.execute('''
				DELETE FROM sensor_value
				WHERE id = {0}
			'''.format(id))
			self.DB.commit()
		except Exception as e:
			pass
		return None
	
	def InsertSensorValue(self, sensor):
		try:
			query = '''
				INSERT INTO sensor_value (id, sensor_id, value, timestamp)
				VALUES ({0},{1},{2},{3})
			'''.format(sensor["id"],sensor["sensor_id"],sensor["value"],sensor["timestamp"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			pass
		return None