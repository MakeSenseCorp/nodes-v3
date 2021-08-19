def IntToBytes(value, length):
	byte_array = []
	while value != 0:
		byte_array = [value % 256] + byte_array
		value = value // 256
	
	# ATMEL will read data from left to right
	byte_array = byte_array + [0]*(length-len(byte_array))
	return byte_array