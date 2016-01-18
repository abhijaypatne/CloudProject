'''
Modified arguments of vif_bw_handler() method.
'''
class Prediction:
	def predict_val(self,data_bytes):
		length = len(data_bytes)
		newval = 0.0
		i = 1
		total = length*(length+1)/2

		while i <= length:
			newval += (data_bytes[i-1]*i)
			i+=1
		newval = newval / total
		return newval
	
	def diff_cal(self,data_bytes):
		length = len(data_bytes)
		#print data_bytes
		diff_values = []
		i = 0
		while i < (length - 1):
			diff_values.append(data_bytes[i+1] - data_bytes[i])
			i+=1
		#print "values = ",diff_values
		return diff_values
		
	def vif_bw_handler(self,stats):
		predicted_list = []
		i = 0
		window_size = len(stats)
		length = len(stats[0].interfaces)
		while i < length:
			j = 0
			temp_list = []
			while j < window_size:
				#print "Packet Size "+str((stats[j].rx_bytes[i])/(stats[j].rx_packets[i]))
				#temp_list.append(((stats[j].dropped[i])*stats[j].rx_bytes[i])/(stats[j].rx_packets[i]*1024))
				temp_list.append((stats[j].dropped[i]))
				#print "interface name : ",stats[0].interfaces[i]," ",stats[j].dropped[i]
				j+=1
			predicted_list.append(self.predict_val(self.diff_cal(temp_list))+stats[-1].dropped[i])
			i+=1
		i=0
		#print "predicted rate : ",predicted_list	
		return predicted_list
			
'''
l1 = [20,30,25,15,36]
l2 = [20,30,25,15,35]
l3 = [20,30,25,15,36]
l4 = [20,30,25,15,35]
vifs = ['v1','v2','v3','v4']
data = [l1,l2,l3,l4]

print Prediction().vif_bw_handler(vifs,data)
'''
