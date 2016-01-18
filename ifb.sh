#!/bin/bash
if [ $# -eq 3 ]
then
	modprobe ifb numifbs=3
	ip link set dev ifb0 up
	ip link set dev ifb1 up
	ip link set dev ifb2 up

	tc qdisc add dev $1 handle ffff: ingress
	tc filter add dev $1 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
	
	tc qdisc add dev $2 handle ffff: ingress
	tc filter add dev $2 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb1

	tc qdisc add dev $3 handle ffff: ingress
	tc filter add dev $3 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb2
else
	echo "Usage : ./ifb.sh interface1 interface2 interface3"
fi
