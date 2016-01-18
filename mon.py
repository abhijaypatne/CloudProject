#!/usr/bin/python

'''
Added method filter.Filter method removes vif for whom tap interface is available.
'''

import time
import sys
import subprocess

class VifStats:
	def __init__(self):
		self.interfaces = []
		self.rx_bytes = []
		self.tx_bytes = []
		self.type = []
		self.dropped = []
		self.rx_packets = []
				
	def __sub__(self,stats1):
		i=0
		for s in self.interfaces:
			self.rx_bytes[i] = self.rx_bytes[i] - stats1.rx_bytes[i]
			self.tx_bytes[i] = self.tx_bytes[i] - stats1.tx_bytes[i]
			i+=1
		return self
	
        def filter(self):
		'''
		i=0
		for s in self.interfaces:
			if self.type[i] == 'tap':
				index = 0
				for m in self.interfaces:
					if m == self.interfaces[i] and self.type[index] == 'vif':
						del self.interfaces[index]
						del self.rx_bytes[index]
						del self.tx_bytes[index]
						del self.type[index]
					index+=1
			i+=1
		'''
		i = 0
		for s in self.interfaces:
			self.interfaces[i] = self.type[i]+s
			i+=1
		return self
	
	def __str__(self):
		string = ""
		i = 0
		for s in self.interfaces:
			string+= s +" \t" + str(self.rx_bytes[i])+"\tdr:\t"+str(self.dropped[i]) + "\t"
			i+=1
		return string
		
class ProcDevNetParser: 
	def __init__(self):
		self.file = open('/proc/net/dev',"r")
		self.old_stats = {}
	
	def __del__(self):
		self.file.close()
		
	def calculate_bytes(self,domains,time_window,packet_size):
		self.file.seek(0,0)
		text = self.file.read()
		lines = text.split('\n')
		parts = lines[1].split('|')

		del lines[0]  #remove entry Inter, Receive and Transmit for lines
		del lines[0]  #remove face,bytes,etc headers
		del lines[-1] #remove blank entry created by split

		length = len(lines)
		stats = VifStats()

		for s in lines:
			subparts = s.split()
			firstentry = subparts.pop(0).split(':')
			subparts.insert(0,firstentry[1])
			subparts.insert(0,firstentry[0])
#			print subparts[0] 

			if 'ifb' in subparts[0]:
				drp = (self.calculate_dropped(subparts[0])*packet_size)/1024.0
				stats.interfaces.append(subparts[0][3:])
				if (self.old_stats.has_key(subparts[0])):
					stats.rx_bytes.append((float(subparts[1]) - self.old_stats[subparts[0]][0]) / (time_window*1024))
					stats.tx_bytes.append((float(subparts[9]) - self.old_stats[subparts[0]][1]) / (time_window*1024))
					stats.rx_packets.append(float(subparts[2]) - self.old_stats[subparts[0]][2])
					stats.dropped.append((drp - self.old_stats[subparts[0]][3])/time_window)
				else:
#					print subparts[1]
					stats.rx_bytes.append(float(subparts[1]) / 1024)
					stats.tx_bytes.append(float(subparts[9]) / 1024)
					stats.rx_packets.append(float(subparts[2]))
					stats.dropped.append(drp)
				stats.type.append('ifb')
				self.old_stats[subparts[0]] = [ float(subparts[1]) , float(subparts[9]) , float(subparts[2]),drp ]
				#print "dropped : " + str(drp) + " interface : " + self.map_ifb(subparts[0])
		return stats.filter()

	def calculate_dropped(self, interface):
		tc = ['tc', '-s' ,'qdisc' ,'show', 'dev' , interface ]
		#val = float(subprocess.check_output(tc, shell=True).rstrip('\n').split(' ')[7].rstrip(','))
		#val = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE).communicate()[0]
		val = float((subprocess.Popen(tc, stdout=subprocess.PIPE).communicate()[0].split('\n')[-3]).split(' ')[7].rstrip(','))
		return val
	
	def map_ifb(self,interface):
		if interface == 'ifb0':
			return 'vnet0'
		elif interface == 'ifb1':
			return 'vnet1'
		else:
			return 'vnet2'

'''
parser = ProcDevNetParser()
domains = [2,3]
stats = []
i = 0
while i<5:
    stats.append(parser.calculate_bytes(domains,1))
    print stats[i]
    time.sleep(3)
    i+=1

while True:
    #call parser
    del stats[0]
    stats.append(parser.calculate_bytes(domains,1))
    print stats[-1]
    time.sleep(3)
'''	
