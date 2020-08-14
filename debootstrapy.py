# -*- coding: utf-8 -*-
################################################################################
##            debootstrapy - a linux tool for using debootstrap               ##
################################################################################
# Copyright (c) 2020 Adam Galindo                                             ##
#                                                                             ##
# Permission is hereby granted, free of charge, to any person obtaining a copy##
# of this software and associated documentation files (the "Software"),to deal##
# in the Software without restriction, including without limitation the rights##
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell   ##
# copies of the Software, and to permit persons to whom the Software is       ##
# furnished to do so, subject to the following conditions:                    ##
#                                                                             ##
# Licenced under GPLv3                                                        ##
# https://www.gnu.org/licenses/gpl-3.0.en.html                                ##
#                                                                             ##
# The above copyright notice and this permission notice shall be included in  ##
# all copies or substantial portions of the Software.                         ##
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
####
################################################################################
"""
debootstrapy - a linux tool for using debootstrap to make 
	a networked, debian based, sandbox.
	OR, a live image with persistance

	currently, only a single os on live usb is supproted
"""
import subprocess
import os
import sys
from io import BytesIO,StringIO
import argparse

__author__ = 'Adam Galindo'
__email__ = 'null@null.com'
__version__ = '1'
__license__ = 'GPLv3'

###################################################################################
# Color Print Functions
###################################################################################
import colorama
from colorama import init
init()
from colorama import Fore, Back, Style
blueprint = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (TESTING == True) else None
greenprint = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (TESTING == True) else None
redprint = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (TESTING == True) else None
# inline colorization for lambdas in a lambda
makered    = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL
makegreen  = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL
makeblue   = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL
makeyellow = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (TESTING == True) else None

###################################################################################
# Commandline Arguments
###################################################################################

parser = argparse.ArgumentParser(description='python/bash based, distro repacker')

parser.add_argument('--user',
                                 dest    = 'user',
                                 action  = "store" ,
                                 default = "derp" ,
                                 help    = "The username to be created" )
parser.add_argument('--password',
                                 dest    = 'password',
                                 action  = "store" ,
                                 default = 'password' ,
                                 help    = "The password to said username" )
parser.add_argument('--extra-packages',
                                 dest    = 'extra_extra',
                                 action  = "store" ,
                                 default = 'micro' ,
                                 help    = "comma seperated list of extra packages to install" )
parser.add_argument('--sandbox-mac',
                                 dest    = 'sand_mac',
                                 action  = "store" ,
                                 default = 'de:ad:be:ef:ca:fe' ,
                                 help    = "MAC Address of the Sandbox" )
parser.add_argument('--sandbox-ip',
                                 dest    = 'sand_ip',
                                 action  = "store" ,
                                 default = '192.168.0.3' ,
                                 help    = "IP Address of the Sandbox" )							
parser.add_argument('--sandbox-iface',
                                 dest    = 'sand_iface',
                                 action  = "store" ,
                                 default = 'hakc1' ,
                                 help    = "Interface name for the Sandbox" )
parser.add_argument('--sandbox-path',
                                 dest    = 'sandy_path',
                                 action  = "store" ,
                                 default = '/home/moop/Desktop/sandbox' ,
                                 help    = "Full Path of the Sandbox" )
parser.add_argument('--arch',
                                 dest    = 'arch',
                                 action  = "store" ,
                                 default = 'amd64' ,
                                 help    = "AMD64, X86, ARM, what-have-you" )
parser.add_argument('--components',
                                 dest    = 'components',
                                 action  = "store" ,
                                 default = 'main,contrib,universe,multiverse' ,
                                 help    = "Which repository components are included" )
parser.add_argument('--repository',
                                 dest    = 'repository',
                                 action  = "store" ,
                                 default = "http://archive.ubuntu.com/ubuntu/" ,
                                 help    = 'The Debian-based repository. E.g. "Ubuntu"' )		
parser.add_argument('--logfile',
                                 dest    = 'log_file',
                                 action  = "store" ,
                                 default = "'./debootstrap_log.txt'" ,
                                 help    = 'logfile name' )
parser.add_argument('--host_iface',
                                 dest    = 'host_iface',
                                 action  = "store" ,
                                 default = "eth0" ,
                                 help    = 'Host network interface to use' )
parser.add_argument('--internal-ip',
                                 dest    = 'internal_ip',
                                 action  = "store" ,
                                 default = "192.168.0.1" ,
                                 help    = 'Host IP address on the chosen interface' )
parser.add_argument('--network_gateway',
                                 dest    = 'gateway',
                                 action  = "store" ,
                                 default = "192.168.0.1" ,
                                 help    = 'Network Gateway IP' )
arguments = parser.parse_args()


class CommandRunner():
	def __init__(self):
		self.error_code_from_current_command = ""
		self.current_command = subprocess
		self.user            = arguments.user
		self.password        = arguments.password
		self.extra           = arguments.extra_extra
		self.sand_mac        = arguments.sand_mac
		self.sand_ip		 = arguments.sand_ip
		self.sand_iface		 = arguments.sand_iface
		self.sandy_path		 = arguments.sandy_path
		self.arch			 = arguments.arch
		self.repository	 	 = arguments.repository
		self.log_file		 = arguments.log_file
		self.host_iface		 = arguments.host_iface
		self.internal_ip	 = arguments.internal_ip
		self.gateway		 = arguments.gateway
		self.extras          = "wget debconf nano curl"
	def error_exit(self):
		print("$1")

	def exec_command(self, command, blocking = bool, shell_env = True):
		if shell_env == True:
			self.current_command = subprocess.run(command , shell=True)
		else:
			self.current_command = subprocess.run(command , shell=False)
		if blocking == True:
			self.current_command.

	def debootstrap_stage1(self):
		# Sequential commands
		print("[+] Beginning Debootstrap")
		thing_to_run = ["sudo", "debootstrap --components {} --arch {} , bionic {} {} >> {} ".format(COMPONENTS,ARCH,SANDBOX,REPOSITORY,LOGFILE)]
		step = self.exec_command(thing_to_run)
		if step.returncode == 1:
		    print("[+] Debootstrap Finished Successfully!")
		else:
			error_exit("[-]Debootstrap Failed! Check the logfile!")
		#resolv.conf copy
		print("[+] Copying Resolv.conf")
		step = ["sudo cp /etc/resolv.conf {}/etc/resolv.conf".format(SANDBOX)]
		if step.returncode == 0:
		    print("[+] Resolv.conf copied!") 
		else:
			error_exit("[-]Copy Failed! Check the logle!")

		# sources.list copy
		print("[+] Copying Sources.list")
		step = ["sudo cp /etc/apt/sources.list {} $SANDBOX/etc/apt/".format()]
		if step.returncode == 0:
	    	print("[+] Sources.list copied!") 
		else:
			error_exit("[-]Copy Failed! Check the logle!")
		#mount and bind the proper volumes
		# /dev
		print("[+] Mounting /dev" )
		step = ["sudo mount -o bind /dev {} $SANDBOX/dev".format()]
		if step.returncode == 0:
	    	print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")
		# /proc
		print("[+] Mounting /proc")
		step = ["sudo mount -o bind -t proc /proc {} $SANDBOX/proc".format()]
		if step.returncode == 0:
	    	print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")
		# /sys
		print("[+] Mounting /sys")
		step = ["sudo mount -o bind -t sys /sys {} $SANDBOX/sys".format()]
		if step.returncode == 0:
	    	print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")

		#finish setting up the basic system
	def deboot_second_stage():
		steps = [["sudo chroot {} $SANDBOX".format(self.sandy_path)]						,\
				 ["useradd {}".format(self.user)]											,\
				 ["passwd  {}".format(self.user)]											,\
				 ["login {}".format(self.user)]												,\
				 ["sudo -S apt-get update"]													,\
				 ["sudo -S apt-get --no-install-recommends install {}".format(self.extras)]	,\
				#clean the gpg error messag
				 ["sudo -S apt-get update"]													,\  
				 #If you don't talk en_US
				 ["sudo -S apt-get install locales dialog"]									,\
		#sudo -S locale-gen en_US.UTF-8  # or your preferred locale
		#tzselect; TZ='Continent/Country'; export TZ  #Congure and use our local time instead of UTC; save in .prole

	#begin setting up services
	def deboot_third_stage():

		step = ["sudo -S apt install $EXTRA_PACKAGES".format()]

	#Makes an interface with iproute1
	def create_iface_ipr1():
		step = ["sudo -S modprobe dummy".format()]
		step = ["sudo -S ip link set name {} $SANDBOX_{} IFACE_NAME dev dummy0".format()]
		step = ["sudo -S ifcong {} $SANDBOX_{} IFACE_NAME hw ether {} $SANDBOX_MAC_ADDRESS".format()]

	#Makes an interface with iproute2
	def create_iface_ipr2():
		step = ["ip link add {} $SANDBOX_{} IFACE_NAME type veth".format()]

	def del_iface1():
		steps = [["sudo -S ip addr del {} $SANDBOX_IP_ADDRESS/24 brd + dev {} $SANDBOX_{} IFACE_NAME".format()],\
			 	 ["sudo -S ip link delete {} $SANDBOX_{} IFACE_NAME type dummy".format()],\
				 ["sudo -S rmmod dummy".format()]]

	#Deletes the SANDBOX Interface
	def del_iface2():
		step = ["ip link del {} $SANDBOX_{} IFACE_NAME".format()]

	#run this from the HOST
	def setup_host_networking():
		#Allow forwarding on HOST IFACE
		steps = [["sysctl -w net.ipv4.conf.$HOST_IF_NAME.forwarding=1".format()],\
		#Allow from sandbox to outside
				 ["iptables -A FORWARD -i {} $SANDBOX_{} IFACE_NAME -o $HOST_{} IFACE_NAME -j ACCEPT".format()],\
		#Allow from outside to sandbox
				 ["iptables -A FORWARD -i $HOST_{} IFACE_NAME -o {} $SANDBOX_{} IFACE_NAME -j ACCEPT".format()]]

	#this is a seperate "computer", The following is in case you want to setup another
	#virtual computer inside this one and allow to the outside
	def sandbox_forwarding():
		#Allow forwarding on Sandbox IFACE
		steps = [["sysctl -w net.ipv4.conf.{} $SANDBOX_{} IFACE_NAME.forwarding=1".format()],\
		#Allow forwarding on Host IFACE
		#Allow from sandbox to outside
				["iptables -A FORWARD -i {} $SANDBOX_{} IFACE_NAME -o $HOST_{} IFACE_NAME -j ACCEPT".format()],\
		#Allow from outside to sandbox
				["iptables -A FORWARD -i $HOST_{} IFACE_NAME -o {} $SANDBOX_{} IFACE_NAME -j ACCEPT".format()]]

	#run this from the Host
	def establish_network():
		# 1. Delete all existing rules
		steps = [["iptables -F"] ,\
		 # 2. Set default chain policies
		 		 ["iptables -P INPUT DROP"],\
		 		 ["iptables -P FORWARD DROP"],\
		 		 ["iptables -P OUTPUT DROP"],\
		# 4. Allow ALL incoming SSH
		         ["iptables -A INPUT -i eth0 -p tcp --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT".format()],\
		         ["iptables -A OUTPUT -o eth0 -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT".format()],\
		# Allow incoming HTTPS
		         ["iptables -A INPUT -i eth0 -p tcp --dport 443 -m state --state NEW,ESTABLISHED -j ACCEPT".format()],\
				 ["iptables -A OUTPUT -o eth0 -p tcp --sport 443 -m state --state ESTABLISHED -j ACCEPT".format()],\
		# 19. Allow MySQL connection only from a specic network
			     #iptables -A INPUT -i eth0 -p tcp -s 192.168.200.0/24 --dport 3306 -m state --state NEW,ESTABLISHED -j ACCEPT
		         #iptables -A OUTPUT -o eth0 -p tcp --sport 3306 -m state --state ESTABLISHED -j ACCEPT
		# 23. Prevent DoS attack
			     ["iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT".format()]]


if __name__ == "__main__":
   "wat"
