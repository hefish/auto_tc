#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time


white_ip_list = ["10.23.52.148",   \
                 "10.23.52.213", "10.23.52.214", \
                 "10.23.52.203", "10.23.52.204"
                 ];


class TrafficControl:
    '''
    '''

    def __init__(self):
        self.q_class_id = 1
        pass

    def get_arp_list(self, dev):
        p = subprocess.Popen(["arp",  "-an", "-i", dev], stdout=subprocess.PIPE)
        arp_output = p.stdout.read()
        arp_list = {}
        for l in arp_output.split("\n"):
            if l.strip() == "":
                continue
            items = l.split(" ")
            if items[3] == "<incomplete>":
                continue

            ip = items[1][1:-1]
            mac = items[3]

            arp_list[ip] = mac

        return arp_list

    def clear_root_qdisc(self, dev):
        cmd = "tc qdisc del dev %s root" % (dev)
        self.run_cmd(cmd)

    def set_root_qdisc(self, dev):
        self.q_class_id = 1
        cmd = "tc qdisc add dev %s root handle 1: htb r2q 1" % (dev)
        self.run_cmd(cmd)

    def set_qdisc(self, dev, arp_list, rate="1Mbit"):
        for (ip,mac) in arp_list.items():
            self.set_ip_rate(dev, ip, rate)



    def set_ip_rate(self, dev, ip, rate="1Mbit"):
        if ip in white_ip_list:
            return
        self.q_class_id += 1
        cmd = "tc class add dev %s parent 1: classid 1:%d htb rate %s ceil %s" % \
              ( dev, self.q_class_id, rate, rate)
        self.run_cmd(cmd)

#        cmd = "tc qdisc add dev %s parent 1:%s handle %d: sfq perturb 10" % \
#              ( dev, self.q_class_id, self.q_class_id )
#        self.run_cmd(cmd)

        cmd = "tc filter add dev %s parent 1: protocol ip prio 16 u32 match ip dst %s flowid 1:%s " % \
              ( dev, ip, self.q_class_id )
        self.run_cmd(cmd)

    def run_cmd(self, cmd, verbose=False):
        if verbose:
            print cmd
        os.system(cmd)


class TCDaemon:

    def __init__(self):
        pass

    def go_loop(self):
        tc = TrafficControl()

        while True:
            print "set ip rates ... "

            tc.clear_root_qdisc("eth0.26")
            tc.set_root_qdisc("eth0.26")
            _8l_ips = tc.get_arp_list("eth0.26")
            tc.set_qdisc("eth0.26", _8l_ips, "3Mbit")

            tc.clear_root_qdisc("eth0.27")
            tc.set_root_qdisc("eth0.27")
            _9l_ips = tc.get_arp_list("eth0.27")
            tc.set_qdisc("eth0.27", _9l_ips, "3Mbit")

            tc.clear_root_qdisc("eth0.52")
            tc.set_root_qdisc("eth0.52")
            _tech_ips = tc.get_arp_list("eth0.52")
            tc.set_qdisc("eth0.52", _tech_ips, "3Mbit")

            time.sleep(300)

        pass


o = TCDaemon()
o.go_loop()




