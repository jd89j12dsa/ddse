class Padding(object):
	"""docstring for padding"""
	def __init__(self):

		self.dummy_min = 2**22
		self.dummy_max = 2**30

	def closest_power_of_4(self,num):
	    
	    power = 0
	    while 4 ** power < num:
	        power += 1
	    return 4 ** power
	
	def fill(self,input_list, min_val = 2**22, max_val = 2**30):
	    
	    unique_list = list(set(input_list))
	
	    target_size = self.closest_power_of_4(len(input_list))
	
	    while len(unique_list) < target_size:
	        unique_list.append(min_val)
	        min_val += 1
	        if min_val > max_val:
	            break
	
	    return unique_list[:target_size]

	def eliminate_dummy(self,search_result):
		true_search_result = []
		for x in search_result:
			if not isinstance(x, int):
				true_search_result.append(x)
			else: 
				if int(x) < self.dummy_min:
					true_search_result.append(x)
		return true_search_result
		