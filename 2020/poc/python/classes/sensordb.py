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
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "sensor_info" (
							"id"			INTEGER PRIMARY KEY AUTOINCREMENT,
							"sensor_index"  INTEGER,
							"type"			INTEGER,
							"device_id"		INTEGER,
							"device_type"	INTEGER,
							"name"			TEXT,
							"description"	TEXT,
							"enabled"		INTEGER
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "sensor_value" (
							"id" 			INTEGER NOT NULL,
							"device_id"		INTEGER NOT NULL,
							"value"			REAL,
							"timestamp"		REAL
						);''')

		self.Init()

	def Init(self):
		pass

	def SensorExist(self, id):
		try:
			query = "SELECT * FROM sensor_info WHERE device_id={0}".format(id)
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
						"index":		row[1],
						"type": 		row[2],
						"device_id": 	row[3],
						"device_type": 	row[4],
						"name": 		row[5],
						"description": 	row[6],
						"enabled": 		row[7]
					})
		except Exception as e:
			pass
		return sensors
	
	def GetSensorByDeviceId(self, id):
		sensors = []
		try:
			query = "SELECT * FROM sensor_info WHERE device_id={0}".format(id)
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					sensors.append({
						"id": 			row[0],
						"index":		row[1],
						"type": 		row[2],
						"device_id": 	row[3],
						"device_type": 	row[4],
						"name": 		row[5],
						"description": 	row[6],
						"enabled": 		row[7]
					})
				return sensors
		except Exception as e:
			pass
		return sensors
	
	def GetSensorHistory(self, id):
		history = []
		query 	= "SELECT * FROM sensor_value WHERE id={0}".format(id)
		try:
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					history.append({
						"value": 		row[2],
						"timestamp": 	row[3]
					})
		except Exception as e:
			pass
		return history

	def InsertSensor(self, sensor):
		try:
			query = '''
				INSERT INTO sensor_info (id, sensor_index, type, device_id, device_type, name, description, enabled)
				VALUES (NULL,{0},{1},{2},{3},'{4}','{5}',1)
			'''.format(sensor["index"],sensor["type"],sensor["device_id"],sensor["device_type"],sensor["name"],sensor["description"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			print(str(e))
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
	
	def DeleteDevice(self, device_id):
		try:
			self.CURS.execute('''
				DELETE FROM sensor_info
				WHERE device_id = {0}
			'''.format(device_id))
			self.DB.commit()
			self.CURS.execute('''
				DELETE FROM sensor_value
				WHERE device_id = {0}
			'''.format(device_id))
			self.DB.commit()
		except Exception as e:
			pass
		return None
	
	def InsertSensorValue(self, sensor):
		try:
			query = '''
				INSERT INTO sensor_value (id, device_id, value, timestamp)
				VALUES ({0},{1},{2},{3})
			'''.format(sensor["id"],sensor["device_id"],sensor["value"],sensor["timestamp"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			pass
		return None
	
	def GetDeviceList(self):
		devices = []
		try:
			query = '''
				SELECt device_id, device_type, COUNT(device_id) as sensors_count FROM `sensor_info`
				GROUP BY device_id
			'''
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					devices.append({
						"device_id": 		row[0],
						"device_type": 		row[1],
						"sensors_count": 	row[2],
					})
				return devices
		except Exception as e:
			pass
		return devices
	
	def UpdateSensorInfo(self, sensor_id, name, description):
		query = '''
			UPDATE sensor_info
			SET name = '{0}', description = '{1}'
			WHERE id = {2}
		'''.format(name,description,sensor_id)

		try:
			self.CURS.execute(query)
			self.DB.commit()
			return True
		except Exception as e:
			return False
	