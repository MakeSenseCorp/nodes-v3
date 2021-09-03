def IntToBytes(value, length):
	byte_array = []
	while value != 0:
		byte_array = [value % 256] + byte_array
		value = value // 256
	
	# ATMEL will read data from left to right
	byte_array = byte_array + [0]*(length-len(byte_array))
	return byte_array

def DiffArray(old_arr, new_arr):
	added 		= []
	removed 	= []
	for item in old_arr:
		if item not in new_arr:
			removed.append(item)
	for item in new_arr:
		if item not in old_arr:
			added.append(item)
	
	if len(added) == 0:
		added = None
	if len(removed) == 0:
		removed = None
	
	return added, removed