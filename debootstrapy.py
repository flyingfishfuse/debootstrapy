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
debootstrapy - a python based linux tool for using debootstrap to make 
	a networked, debian based, sandbox OR a live image with persistance

	Using only basic debian/linux/gnu tools

	currently, only a single os on live usb is supported
	
	config file must be named "debootstrapy-config" and be in the same directory
"""
import os
import sys
import pathlib
import argparse
import subprocess
import configparser
from io import BytesIO,StringIO

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
# I guess we start at the top!
###################################################################################
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='python/bash based, distro repacker')
	parser.add_argument('--use-config',
                                 dest    = 'config_file',
                                 action  = "bool" ,
                                 default = "False" ,
                                 help    = 'Use config file, if set to "True" will ignore other options' )
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
	parser.add_argument('--sandbox-hostname',
                                 dest    = 'sand_hostname',
                                 action  = "store" ,
                                 default = 'sandbox' ,
                                 help    = "Hostname of the Sandbox" )
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
	parser.add_argument('--sandbox-interface',
                                 dest    = 'sand_iface',
                                 action  = "store" ,
                                 default = 'hack1' ,
                                 help    = "Interface name for the Sandbox" )
	parser.add_argument('--sandbox-netmask',
                                 dest    = 'sandy_netmask',
                                 action  = "store" ,
                                 default = '/24' ,
                                 help    = 'Netmask for the sandbox in slash notation, e.g. "/24"' )
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
                                 default = './debootstrap_log.txt' ,
                                 help    = 'logfile name' )
	parser.add_argument('--host-interface',
                                 dest    = 'host_iface',
                                 action  = "store" ,
                                 default = "eth0" ,
                                 help    = 'Host network interface to use' )
	parser.add_argument('--internal-ip',
                                 dest    = 'internal_ip',
                                 action  = "store" ,
                                 default = "192.168.0.1" ,
                                 help    = 'Host IP address on the chosen interface' )
	parser.add_argument('--network-gateway',
                                 dest    = 'gateway',
                                 action  = "store" ,
                                 default = "192.168.0.1" ,
                                 help    = 'Network Gateway IP' )
	# dont use this here, not time for it to be parsed yet
	#arguments = parser.parse_args()

#Set some variables

class OSStuff:
	def __init__(self):
		self.script_cwd         = pathlib.Path().absolute()
		self.script_osdir       = pathlib.Path(__file__).parent.absolute() 

if __name__ == "__main__":
	OSVars = OSStuff()


class CommandRunner:
	def __init__(self, sand_hostname, user, password ,\
				 extra, sand_mac, sand_ip,sand_iface ,\
				 sandy_netmask, sandy_path, arch     ,\
				 repository, components, log_file    ,\
				 host_iface, internal_ip, gateway    ):
		self.current_command  = subprocess
		self.sandbox_hostname = sand_hostname 
		self.user             = user
		self.password         = password
		self.extra_packages   = extra_extra
		self.sand_mac         = sand_mac
		self.sand_ip		  = sand_ip
		self.sand_iface		  = sand_iface
		self.sandy_netmask    = sandy_netmask
		self.sandy_path		  = sandy_path
		self.arch			  = arch
		self.repository	 	  = repository
		self.components       = components
		self.log_file		  = log_file
		self.host_iface		  = host_iface
		self.internal_ip	  = internal_ip
		self.gateway		  = gateway
		self.extras           = "debconf nano curl"
		self.error_code_from_current_command = ""

	def error_exit(self, message : str, exception : Exception):
		redprint(message)
		print(Exception.with_traceback)

	def exec_command(self, command, blocking = True, shell_env = True):
		'''
	returns a subprocess.CompletedProcess object
	TODO: add logging
		'''
		#pass strings 
		try:
		#if we want it to wait, halting program execution
			if blocking == True:
				step = subprocess.Popen(command , shell=shell_env , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				# print the response
				output, error = step.communicate()
				herp = output.decode()
				derp = error.decode()
				for output_line in herp[0].decode(encoding='utf-8').split('\n'):
				  greenprint(output_line)
				for error_lines in herp[0].decode(encoding='utf-8').split('\n'):
					greenprint(error_lines)

				return step.returncode
				
			elif blocking == False:
				# TODO: not implemented yet
				pass	
	
		except Exception as derp:
			self.error_exit("[-] Shell Command failed! ", derp)

	def stage1(self):
		'''
	Stage 1 :
		- sets up base files/directory's
			* debootstrap
			* copy resolv.conf
		- mounts for chroot
			* /dev, /proc, /sys
		'''
		# Sequential commands
		greenprint("[+] Beginning Debootstrap")
		self.current_command = ["sudo debootstrap --components {} --arch {} , bionic {} {}".format( \
											     self.components,self.arch,self.sandy_path,self.repository)]
		stepper = self.exec_command(self.current_command)
		if stepper.returncode == 1:
		    greenprint("[+] Debootstrap Finished Successfully!")
		elif stepper.returncode == 1:
			error_exit("[-]Debootstrap Failed! Check the logfile!")

############################################
		#resolv.conf copy
		greenprint("[+] Copying Resolv.conf")
		self.current_command = ["sudo cp /etc/resolv.conf {}/etc/resolv.conf".format(self.sandy_path)]
		stepper = self.exec_command(self.current_command)

		if stepper.returncode == 1:
		    greenprint("[+] Resolv.conf copied!") 
		else:
			error_exit("[-]Copy Failed! Check the logle!")

##########################################
		# sources.list copy
		print("[+] Copying Sources.list")
		self.current_command = ["sudo cp /etc/apt/sources.list {}/etc/apt/".format(self.sandy_path)]
		stepper = self.exec_command(self.current_command)
		if stepper.returncode == 1:
			print("[+] Sources.list copied!") 
		else:
			error_exit("[-]Copy Failed! Check the logfile!")

##########################################
		#mount and bind the proper volumes
		# /dev
		print("[+] Mounting /dev" )
		self.current_command = ["sudo mount -o bind /dev {}/dev".format(self.sandy_path)]
		stepper = self.exec_command(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")
		# /proc
		print("[+] Mounting /proc")

########################################
		self.current_command = ["sudo mount -o bind -t proc /proc {}/proc".format(self.sandy_path)]
		stepper = self.exec_command(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")

#######################################
		# /sys
		print("[+] Mounting /sys")
		self.current_command = ["sudo mount -o bind -t sys /sys {}/sys".format(self.sandy_path)]
		stepper = self.exec_command(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mount Failed! Check the logle!")

###############################################################################
		#finish setting up the basic system
	def stage2(self):
		'''
	Establishes Chroot
		- sets username / password

        - LOG'S IN, DONT LEAVE THE COMPUTER
            -for security purposes

		- updates packages
		- installs debconf, nano, curl
		- installs extras

		'''
		steps = [["sudo chroot {} ".format(self.sandy_path)]						,\
				 ["useradd {}".format(self.user)]											,\
				 ["passwd  {}".format(self.password)]											,\
				 ["login {}".format(self.user)]												,\
				 ["sudo -S apt-get update"]													,\
				 ["sudo -S apt-get --no-install-recommends install {}".format(self.extras)]	,\
				#TODO: clean the gpg error message
				 ["sudo -S apt-get update"]													]#,\  
				 #If you don't talk en_US
				 #["sudo -S apt-get install locales dialog"]									,\
		#sudo -S locale-gen en_US.UTF-8  # or your preferred locale
		#tzselect; TZ='Continent/Country'; export TZ  #Congure and use our local time instead of UTC; save in .prole

	#begin setting up services
	def deboot_third_stage(self):
		'''
	Installs extra user packages
		'''
		self.current_command = ["sudo -S apt install {}".format(self.extra_packages)]

	#Makes an interface with iproute1
	def create_iface_ipr1(self, internal_interface, external_interface):
		steps = [["sudo -S modprobe dummy"] ,\
				 ["sudo -S ip link set {} dev dummy0".format(self.sand_iface)] ,\
				 ["sudo -S ifcong {} hw ether {}".format(\
					self.sand_iface, self.sand_mac)]]

	#Makes an interface with iproute2
	def create_iface_ipr2(self):
		steps = ["ip link add {} type veth".format(self.sand_iface)]

	def del_iface1(self):
		steps = [["sudo -S ip addr del {}{} brd + dev {}".format(self.sand_ip,self.sandy_netmask,self.sand_iface)],\
			 	 ["sudo -S ip link delete {} $SANDBOX_{} IFACE_NAME type dummy".format()],\
				 ["sudo -S rmmod dummy".format()]]

	#Deletes the SANDBOX Interface
	def del_iface2(self):
		ssteps = ["ip link del {} $SANDBOX_{} IFACE_NAME".format()]

	#run this from the HOST
	def setup_host_networking(self):
		#Allow forwarding on HOST IFACE
		steps = [["sysctl -w net.ipv4.conf.$HOST_IF_NAME.forwarding=1".format()],\
		#Allow from sandbox to outside
				 ["iptables -A FORWARD -i {} $SANDBOX_{} IFACE_NAME -o $HOST_{} IFACE_NAME -j ACCEPT".format()],\
		#Allow from outside to sandbox
				 ["iptables -A FORWARD -i $HOST_{} IFACE_NAME -o {} $SANDBOX_{} IFACE_NAME -j ACCEPT".format()]]

	#this is a seperate "computer", The following is in case you want to setup another
	#virtual computer inside this one and allow to the outside
	def sandbox_forwarding(self):
		#Allow forwarding on Sandbox IFACE
		steps = [["sysctl -w net.ipv4.conf.{} $SANDBOX_{} IFACE_NAME.forwarding=1".format()],\
		#Allow forwarding on Host IFACE
		#Allow from sandbox to outside
				["iptables -A FORWARD -i {} $SANDBOX_{} IFACE_NAME -o $HOST_{} IFACE_NAME -j ACCEPT".format()],\
		#Allow from outside to sandbox
				["iptables -A FORWARD -i $HOST_{} IFACE_NAME -o {} $SANDBOX_{} IFACE_NAME -j ACCEPT".format()]]

	#run this from the Host
	def establish_network(self):
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
	arguments = parser.parse_args()
	if arguments.config_file == True:
		config = configparser.ConfigParser()
		config.read('debootstrapy.config')
		user_choice = config['Thing To Do']
		for option in config.sections():
			if option == "Debian Buster":
				kwargs = config[option]
				CommandRunner(**kwargs)
			elif option == 'Ubuntu 18.04':
				pass
			elif option == 'Ubuntu 20.04':
				pass
			elif option == 'Linux Mint'
				pass
			else:
				redprint("[-] Option not in config file")
	elif arguments.config_file == False:
		thing_to_do = CommandRunner(arguments.sand_hostname ,arguments.user       ,\
					  arguments.password,	arguments.extra_extra     ,\
					  arguments.sand_mac,	arguments.sand_ip         ,\
					  arguments.sand_iface, arguments.sandy_netmask ,\
					  arguments.sandy_path, arguments.arch          ,\
					  arguments.repository, arguments.components    ,\
					  arguments.log_file,	arguments.host_iface      ,\
					  arguments.internal_ip, arguments.gateway      ,\
					  "debconf nano curl")
