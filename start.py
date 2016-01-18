#!/usr/bin/python

'''
Deleted Method getVirtualInterfaces.
'''

from mon import *
from prediction import *
import sys
from allocator import *

class vmInfo:
    def __init__(self):
        self.domid = 0
        self.domname = "null"
        #self.interfaces = []
        self.minbw = 1024
        self.maxbw = 10240
        #self.type
	self.allocatedbw = self.minbw
    
class ODBA:
    def __init__(self):
        self.vmlist = []
        #list to store VifStats Objects
        self.stats = [] 
	self.bwManager = 0
	
    def getDomainsList(self):
        domains = [1,2,3]
        return domains

    def getvmInfo(self,domains):
        for s in domains:
            vminfo = vmInfo()
            vminfo.domid = s
            self.vmlist.append(vminfo)

    def monitor(self,time_window,packet_size):
        #starting phase wait 5 times 
        #collect six data sets to predict 7th
	self.getvmInfo(self.getDomainsList())
	self.bwManager = BandwidthManager(self.vmlist)
	self.bwManager.init_allocator()
	
        parser = ProcDevNetParser()
        predictor = Prediction()
        domains = self.getDomainsList()
        #self.stats.append(parser.calculate_bytes(domains))
        #print self.stats[0]
        #time.sleep(5)
        parser.calculate_bytes(domains,time_window,packet_size)
        time.sleep(time_window)
        i = 0
        while i<5:
            self.stats.append(parser.calculate_bytes(domains,time_window,packet_size))
            print self.stats[i]
            time.sleep(time_window)
            i+=1

        #call predictor
        newval = predictor.vif_bw_handler(self.stats)
        #print "Predicted Values : ",newval   
        #call tc
        self.bwManager.calculator(newval,self.stats)
            
        while True:
            #call parser
            del self.stats[0]
            self.stats.append(parser.calculate_bytes(domains,time_window,packet_size))
            print self.stats[-1]
            
            #predictor
            newval = predictor.vif_bw_handler(self.stats)
            #print "Predicted Values : ",newval

            #tc
            self.bwManager.calculator(newval,self.stats)
            time.sleep(time_window)
        
def main():
    if len(sys.argv) != 3:
	print "Usage : ./start.py Time_window Packetsize_in_bytes"
	sys.exit(1)
    ODBA().monitor(float(sys.argv[1]),float(sys.argv[2]))

main()
