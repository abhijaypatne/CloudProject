
from tc import *

class PriorityClass:
    def __init__(self):
        self.classno=0
        self.totbw=0.0
        self.vms = []
       	 
    def add_vm(self,vminfo):
        self.vms.append(vminfo)

    def remove_vm(self,vminfo):
        pass

    def setval(self,num):
        self.classno = num

#done

class BandwidthManager:
    def __init__(self,vms):
        self.Bphy = 10240
        self.Bcurr_tot = 0
        self.Bpool = 0
        self.vms = vms #list of objects of vmInfo class
        self.pclass = [] #list of objects of Priority Class
	self.tc_handler = TrafficShaper()

    def init_allocator(self):
        i = 1.0
	j = 0
	l = [1,2,3]
        for s in self.vms:   
	    self.tc_handler.create_root('ifb'+str(j),"1","10")
            self.allocator('ifb'+str(j),s.minbw)
            self.Bcurr_tot+=s.minbw
            self.pclass.append(PriorityClass())
            self.pclass[-1].setval(i)
            self.pclass[-1].add_vm(s)
            i+=1
	    j+=1
            
        self.Bpool = self.Bphy - self.Bcurr_tot
        #print "Bpool : ",self.Bpool
       
    #distributor method to be called by calculator
    def distributor(self,predicted_list,stats_list):
        breq = 0
        temp_pool = 0
        round2_pool = 0
        
        for s in predicted_list:
            if s < 0:
                temp_pool-=s
            breq+=s

        temp_pool+=self.Bpool			
	#print "Bpool = ",self.Bpool,"    breq = ",breq,"    temp_pool = ",temp_pool
        if breq <= temp_pool:
            #possible case
	    #print "In if case"
            i=0
            for s in predicted_list:
                #print "Max for the vm : ",self.vms[i].maxbw
                if (s + self.vms[i].allocatedbw) > self.vms[i].maxbw:
                    predicted_list[i] = self.vms[i].maxbw - self.vms[i].allocatedbw
                    #readjust the breq[i] so its usage doesn't exceed Bmax
		i+=1

            breq = 0        
            for s in predicted_list:			
                breq+=s

            i=0
            for s in self.pclass:
                self.pclass[i].totbw = predicted_list[i]
                i+=1
            
        else:
	   #print "In else case"
           i = 0
	   if self.Bpool == 0.0:
               #print "Exhausted Bpool !!!"
               for s in predicted_list:
                   predicted_list[i] = predicted_list[i] + self.vms[i].allocatedbw
                   self.vms[i].allocatedbw = 0
                   self.Bpool = 10240
                   temp_pool = 10240
                   i+=1
               #print "Predicted list : ",predicted_list
           length = 0
           for s in predicted_list:
           	if s > 0:
                    length+=1
           #print "Length = ",length         
           tot_weight = (length*(length+1))/2
           i=0
           for s in self.pclass:
               if predicted_list[i] > 0:
                   temp = (length*temp_pool)/tot_weight
               	   
                   if predicted_list[i] < temp:
		       if (self.vms[i].allocatedbw+predicted_list[i]) > self.vms[i].maxbw:
                           #print "in predicted_list maxbw comparison"
                           self.pclass[i].totbw = self.vms[i].maxbw - self.vms[i].allocatedbw 
                           round2_pool += (self.vms[i].allocatedbw+predicted_list[i]) - self.vms[i].maxbw
		       else:
                           self.pclass[i].totbw = predicted_list[i]
                           round2_pool += (temp - predicted_list[i])
                   else:
                       if (self.vms[i].allocatedbw+temp) > self.vms[i].maxbw:
                           #print "in temp maxbw comparison"
                           self.pclass[i].totbw = self.vms[i].maxbw - self.vms[i].allocatedbw
                           round2_pool += (self.vms[i].allocatedbw+temp) - self.vms[i].maxbw
                       else:
                           self.pclass[i].totbw = temp
                   length-=1
               else:
                   self.pclass[i].totbw = predicted_list[i] 
               i+=1
           #print "Assigned bw to classes : ",self.pclass[0].totbw,self.pclass[1].totbw,self.pclass[2].totbw
           #round2
           
           if round2_pool > 0:
	       #print "Round 2"
               i=0
               for s in self.pclass:
                   if round2_pool > 0:
                       diff = predicted_list[i] - s.totbw
                       if diff > 0:
                           if round2_pool >= diff:
                               round2_pool -= diff
                               self.pclass[i].totbw = predicted_list[i]
                           else:
                               self.pclass[i].totbw+=round2_pool
                               round2_pool = 0
                   i+=1
           
        temp_tot = 0
        i=0
       
        
        for s in stats_list[0].interfaces:
	    if (self.pclass[i].totbw + self.vms[i].allocatedbw) < self.vms[i].minbw:
		self.allocator(s,self.vms[i].minbw)
		temp_tot+=self.vms[i].minbw
		self.vms[i].allocatedbw = self.vms[i].minbw
	    else:
            	self.allocator(s,self.pclass[i].totbw + self.vms[i].allocatedbw)
            	temp_tot+=(self.pclass[i].totbw + self.vms[i].allocatedbw)
		self.vms[i].allocatedbw = self.pclass[i].totbw + self.vms[i].allocatedbw
            i+=1
        self.Bpool = self.Bphy - temp_tot
        #print "Pool : ",self.Bpool
      	#print
	#print  
        
    def allocator(self,vif,bwcap):
        #print "Allocator : ",vif,"   ",bwcap
	self.tc_handler.allocate_egress(vif,str(bwcap)+"kbps",str(bwcap)+"kbps","1","10")
        
    def calculator(self,predicted_list,stats_list):
        i=0
        temp_pool = 0
        for val in predicted_list:
            if val == 0:
                #stage 1 and 2
                if (self.vms[i].allocatedbw == self.vms[i].minbw):
                    #print "In stage 0"
		    pass
                else:
                    if stats_list[-1].rx_bytes[i] == self.vms[i].allocatedbw:
                        #stage 1...do nothing
			#print "In stage 1"
                        pass
                    else:
                        #stage 2
			#print "In stage 2"
                        if stats_list[-1].rx_bytes[i] < self.vms[i].minbw:
                            #do nothing
                            pass
                        else:
                            self.pclass[i].totbw = stats_list[-1].rx_bytes[i] - self.vms[i].allocatedbw 
                            temp_pool += self.vms[i].allocatedbw - stats_list[-1].rx_bytes[i]
                            #self.pclass[i].totbw = stats_list[-1].rx_bytes[i]
            i+=1
            
        self.Bpool+=temp_pool
        self.distributor(predicted_list,stats_list)
