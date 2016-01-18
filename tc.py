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
		param.append(major + ":1")
		param.append("classid")
		param.append(major + ":" + default)
		param.append("htb")
		param.append("rate")
		param.append(rate)
		param.append("ceil")
		param.append(ceil)
		#print param
		call(param,shell=False,stdout=False,stderr=False)

	def allocate_ingress(self):
		pass

'''
TrafficShaper.create_root("ifb0", "1", "12")
TrafficShaper.create_root("ifb1", "1", "12")
TrafficShaper.allocate_egress("ifb0","50kbps","50kbps", "1", "12")
TrafficShaper.allocate_egress("ifb1","40kbps","40kbps", "1", "12")
TrafficShaper.create_root("ifb2", "1", "12")
TrafficShaper.allocate_egress("ifb2","50kbps","50kbps", "1", "12")
'''
#TrafficShaper().allocate_egress("ifb0","100kbps","120kbps","1","10")
#ts3 = TrafficShaper("ifb2", "1", "12")
#ts3.allocate_egress("ifb2","40kbps","40kbps", "1", "12")

