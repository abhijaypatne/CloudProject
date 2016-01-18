#! /bin/python

import sys
from subprocess import call

class TrafficShaper:
	def create_root(self, interface, major, default):
		init = ['tc', 'qdisc', 'add', 'dev']
		init.append(interface)
		init.append("root")
		init.append("handle")
		init.append(major + ":")
		init.append("htb")
		init.append("default")
		init.append(default)
		#print init
		call(init,shell=False,stdout=False,stderr=False)

	def allocate_egress(self,interface,rate,ceil, major, default):
		param = []
		param.append("tc")
		param.append("class")
		param.append("replace")
		param.append("dev")
		param.append(interface)
		param.append("parent")
		param.append(major + ":")
		param.append("classid")
		param.append(major + ":" + default)
		param.append("htb")
		param.append("rate")
		param.append(rate)
		param.append("ceil")
		param.append(ceil)
		#print param
		try:
			ret = call(param,shell=False,stdout=False,stderr=False)
		except OSError as e:
			print "Error: ",e
		return ret
	
	def allocate_ingress(self):
		pass

#ts1 = TrafficShaper()
#ts2 = TrafficShaper("vif5.0", "1", "12")
#ts1.allocate_egress("ifb0","100kbps","100kbps", "1", "12")
#ts2.allocate_egress("vif5.0","400kbps","400kbps", "1", "12")
#TrafficShaper().allocate_egress("vif3.0","400kbps","400kb", "12")
#TrafficShaper().create_root("ifb0", "1", "12")
TrafficShaper().create_root("eth0", "1", "12")
#TrafficShaper().allocate_egress("ifb0","50kbps","50kbps", "1", "12")
#TrafficShaper().allocate_egress("ifb1","60kbps","60kbps", "1", "12")
#TrafficShaper().create_root("ifb2", "1", "12")
TrafficShaper().allocate_egress("eth0","10mbps","10mbps", "1", "12")
