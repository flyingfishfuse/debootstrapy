# -*- coding: utf-8 -*-
################################################################################
##			debootstrapy - a linux tool for using debootstrap			      ##
################################################################################
# Copyright (c) 2020 Adam Galindo											  ##
#																			  ##
# Permission is hereby granted, free of charge, to any person obtaining a copy##
# of this software and associated documentation files (the "Software"),to deal##
# in the Software without restriction, including without limitation the rights##
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell   ##
# copies of the Software, and to permit persons to whom the Software is	      ##
# furnished to do so, subject to the following conditions:					  ##
#																			  ##
# Licenced under GPLv3														  ##
# https://www.gnu.org/licenses/gpl-3.0.en.html								  ##
#																			  ##
# The above copyright notice and this permission notice shall be included in  ##
# all copies or substantial portions of the Software.						  ##
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
debootstrapy:
	- infrastructure that allows for running bash scripts with python
 
	- python based linux tool for using debootstrap to make a networked
		debian based, sandbox OR a live-usb image with persistance
		Using only basic debian/linux/gnu tools

	currently, only a single os live-usb is supported
	
	config file must be named "debootstrapy.config" and be in the same directory

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
try:
	import colorama
	from colorama import init
	init()
	from colorama import Fore, Back, Style
	COLORMEQUALIFIED = True
except ImportError as derp:
	print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE")
	COLORMEQUALIFIED = False

blueprint = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
redprint = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
# inline colorization for lambdas in a lambda
makered	= lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen  = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue   = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeyellow = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
###################################################################################
# Commandline Arguments
###################################################################################
# If the user is running the program as a script we parse the arguments or use the 
# config file. 
# If the user is importing this as a module for usage as a command framework we do
# not activate the argument or configuration file parsing engines
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='python/bash based, distro repacker')
	parser.add_argument('--use-config',
								 dest		= 'config_file',
								 action		= "store_true" ,
								 help		= 'Use config file, if used, will ignore other options' )
	parser.add_argument('--make-disk',
								 dest		= 'make_disk',
								 action		= "store_true" ,
								 help		= 'Makes new partitions and installs Grub2/syslinux, \
									 		   takes device name from fdisk -l. Otherwise, makes a folder' )
	parser.add_argument('--use-iso',
								 dest		= 'use_live_iso',
								 action 	= "store_true" ,
								 help		= 'Uses a Live ISO instead of a repository' )
	parser.add_argument('--iso-name',
								 dest		= 'iso_name',
								 action		= "store" ,
								 help		= 'ISO to use, might need to be in same directory' )
	parser.add_argument('--user',
								 dest	= 'user',
								 action  = "store" ,
								 default = "derp" ,
								 help	= "The username to be created" )
	parser.add_argument('--password',
								 dest	= 'password',
								 action  = "store" ,
								 default = 'password' ,
								 help	= "The password to said username" )
	parser.add_argument('--extra-packages',
								 dest	= 'extra_extra',
								 action  = "store" ,
								 default = 'micro' ,
								 help	= "comma seperated list of extra packages to install" )
	parser.add_argument('--sandbox-hostname',
								 dest	= 'sand_hostname',
								 action  = "store" ,
								 default = 'sandbox' ,
								 help	= "Hostname of the Sandbox" )
	parser.add_argument('--sandbox-mac',
								 dest	= 'sand_mac',
								 action  = "store" ,
								 default = 'de:ad:be:ef:ca:fe' ,
								 help	= "MAC Address of the Sandbox" )
	parser.add_argument('--sandbox-ip',
								 dest	= 'sand_ip',
								 action  = "store" ,
								 default = '192.168.0.3' ,
								 help	= "IP Address of the Sandbox" )							
	parser.add_argument('--sandbox-interface',
								 dest	= 'sand_iface',
								 action  = "store" ,
								 default = 'hack1' ,
								 help	= "Interface name for the Sandbox" )
	parser.add_argument('--sandbox-netmask',
								 dest	= 'sandy_netmask',
								 action  = "store" ,
								 default = '/24' ,
								 help	= 'Netmask for the sandbox in slash notation, e.g. "/24"' )
	parser.add_argument('--sandbox-path',
								 dest	= 'sandy_path',
								 action  = "store" ,
								 default = '/home/moop/Desktop/sandbox' ,
								 help	= "Full Path of the Sandbox" )
	parser.add_argument('--arch',
								 dest	= 'arch',
								 action  = "store" ,
								 default = 'amd64' ,
								 help	= "amd64, x86, arm, ..." )
	parser.add_argument('--components',
								 dest	= 'components',
								 action  = "store" ,
								 default = 'main,contrib,universe,multiverse' ,
								 help	= "Which repository components are included" )
	parser.add_argument('--repository',
								 dest	= 'repository',
								 action  = "store" ,
								 default = "http://archive.ubuntu.com/ubuntu/" ,
								 help	= 'The Debian-based repository. E.g. "Ubuntu"' )		
	parser.add_argument('--livedisk_hw_name',
								 dest	= 'livedisk_hw_name',
								 action  = "store" ,
								 default = "sdc" ,
								 help	= 'Makes new partitions , takes device name from fdisk -l' )
	parser.add_argument('--logfile',
								 dest	= 'log_file',
								 action  = "store" ,
								 default = './debootstrap_log.txt' ,
								 help	= 'logfile name' )
	parser.add_argument('--host-interface',
								 dest	= 'host_iface',
								 action  = "store" ,
								 default = "eth0" ,
								 help	= 'Host network interface to use' )
	parser.add_argument('--internal-ip',
								 dest	= 'internal_ip',
								 action  = "store" ,
								 default = "192.168.0.1" ,
								 help	= 'Host IP address on the chosen interface' )
	parser.add_argument('--network-gateway',
								 dest	= 'gateway',
								 action  = "store" ,
								 default = "192.168.0.1" ,
								 help	= 'Network Gateway IP' )
	# dont use this here, not time for it to be parsed yet
	#arguments = parser.parse_args()

def import_script(script:str):
	

class Stepper:
	def __init__(self):
		self.script_cwd		   = pathlib.Path().absolute()
		self.script_osdir	   = pathlib.Path(__file__).parent.absolute()
		self.current_command   = str 

	def error_exit(self, message : str, exception : Exception):
		redprint(message)
		print(exception.with_traceback)
		sys.exit()
	
	def step(self, list_of_commands):
		try:
			for instruction in list_of_commands if (len(list_of_commands) > 1):
				self.current_command = instruction
				stepper = Stepper.step(self.current_command)
				if stepper.returncode == 1 :
					return 
				else:
					return false
		except Exception as derp:
			return derp
	
	def exec_command(self, command, blocking = True, shell_env = True):
		'''TODO: add logging/formatting'''
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

				return step
				
			elif blocking == False:
				# TODO: not implemented yet				
				pass
				
		except Exception as derp:
			yellow_bold_print("[-] Shell Command failed!")
			return derp

class CommandRunner:
	'''
Basic structure for adding commands:

def thing_to_do(self, params):
	"""
	documentation
	"""
	try:
		steps = {"command_name"  : ["string with shell command"          , "[-] failure message", "[+] success message" ] ,\
			 	 "command_name2" : ["another string with a shell command", "[-] failure message", "[+] success message" ] ,}
		for instruction in steps:
			exec_pool = self.stepper(steps)
			if exec_pool.returncode == 1:
				greenprint("[+] Task Finished Sucessfully!")
			elif exec_pool.returncode == WHATEVER:
				redprint("[-] Task Failed! Check the logfile!")
		except Exception as derp:
			error_exit("[-] Failure Message", derp)

	'''
	def __init__(self, kwargs):
		for (k, v) in kwargs.items():
			setattr(self, k, v)
		self.current_command	= str
		self.extras				= "debconf nano curl"
		self.error_code_from_current_command = ""
		self.live_disk_dir		= self.temp_dir      + '/live'
		self.temp_boot_dir		= self.live_disk_dir + '/boot'
		self.efi_dir			= self.temp_dir      + '/efi'
		self.persistance_dir	= self.temp_dir      + '/persistance'
		self.file_source_dir	= self.temp_dir + file_source_dir


	###################################################################################
	## Dynamic imports
	###################################################################################
	def dynamic_import(self, module_to_import:str, name_as:str):
		'''
		Dynamically imports a module
			- used for the extensions

		Usage:
			thing = class.dynamic_import('pybash_script.classname', name='fishy')
		''' 
		list_of_subfiles = pkgutil.iter_modules([os.path.dirname(__file__)])
		imported_module = import_module('.' + name_as, package=__name__)
		class_filter = ['Stepper']
		lambda classname: classname != any(class_filter) and not classname.startswith('__')
		class_name = list(filter(classname(), dir(imported_module)))
		new_class = getattr(imported_module, class_name[0])

		# need to put an error check here
		setattr(sys.modules[__name__], name, new_class)

		return new_class

	def setup_disk(self, diskname, efi_dir, persistance_dir, temp_boot_dir, live_disk_dir):
		# This creates the basic disk structure of an EFI disk with a single OS.
		# You CAN boot .ISO Files from the persistance partition if you mount in GRUB2 
		## EFI
		steps = ["parted /dev/{}--script mkpart EFI fat16 1MiB 100MiB".format(diskname)       ,\
		## LIVE disk partition   
		"parted /dev/{}--script mkpart live fat16 100MiB 3GiB".format(diskname)	              ,\
		## Persistance Partition															  ,\
		"parted /dev/{}--script mkpart persistence ext4 3GiB 100%".format(diskname)           ,\
		## Sets filesystem flag																  ,\
		"parted /dev/{}--script set 1 msftdata on".format(diskname)				              ,\
		## Sets boot flag for legacy (NON-EFI) BIOS											  ,\
		"parted /dev/{}--script set 2 legacy_boot on".format(diskname)			              ,\
		"parted /dev/{}--script set 2 msftdata on".format(diskname)				              ,\
		# Here we make the filesystems for the OS to live on								  ,\
		## EFI																				  ,\
		"mkfs.vfat -n EFI /dev/{}1".format(diskname)								          ,\
		## LIVE disk partition																  ,\
		"mkfs.vfat -n LIVE /dev/{}2".format(diskname)							              ,\
		## Persistance Partition															  ,\
		"mkfs.ext4 -F -L persistence /dev/{}3".format(diskname)					              ]
		exec_pool = self.stepper(steps)
		if exec_pool.returncode == 1:
			greenprint("[+] Disk Formatting Finished Sucessfully!")
		else:
			error_exit("[-] Disk Formatting Failed! Check the logfile!")

	def move_system_files(self, efi_dir, live_disk_dir,persistance_dir,file_source_dir):
		# Creating Temporary work directories
		steps = ["mkdir {} {} {} {}".format(efi_dir, live_disk_dir ,persistance_dir, file_source_dir) ,\
		# Mounting those directories on the newly created filesystem					  ,\
		"mount /dev/{}1 {}".format(diskname, efi_dir )				   ,\
		"mount /dev/{}2 {}".format(diskname, live_disk_dir)			 ,\
		"mount /dev/{}3 {}".format(diskname, persistance_dir)			,\
		# Mount the ISO on a temp folder to get the files moved						   ,\
		"mount -oro {} {}".format(live_iso, file_source_dir)					   ,\
		"cp -ar {}/* {}".format(file_source_dir, live_disk_dir)					,\
		# IMPORTANT! This establishes persistance! UNION is a special mounting option 
		# https://unix.stackexchange.com/questions/282393/union-mount-on-linux
		'echo "/ union" > {}/persistence.conf'.format(persistance_dir)] 
		exec_pool = self.stepper(steps)
		if exec_pool.returncode == 1:
			greenprint("[+] Files Moved Sucessfully!")
		else:
			error_exit("[-] File Moving Failed! Check the logfile!")

	def install_grub2(self, bit_size, arch, livedisk_hw_name, temp_boot_dir , efi_dir):
		'''
		 Install GRUB2
		 https://en.wikipedia.org/wiki/GNU_GRUB
		 Script supported targets: arm64-efi, x86_64-efi, , i386-efi
		TODO : Install 32bit brub2 then 64bit brub2 then `update-grub`
			   So's we can install 32 bit OS to live disk.
		'''
		#########################
		##	  64-BIT OS	   #
		#########################
		if bit_size == "32":
			#ARM maybe supported?
			if arch == "arm":
				greenprint("[+] Installing GRUB2 for {} to /dev/{}".format(arch, livedisk_hw_name)) 
				#########################
				self.current_command = \
					"grub-install --removable --target=arm-efi --boot-directory={} --efi-directory={} /dev{}".format(\
					 temp_boot_dir, efi_dir, livedisk_hw_name)
				#########################
				stepper = Stepper.step(self.current_command)
				if stepper.returncode == 1:
					greenprint("[+] GRUB2 Install Finished Successfully!")
				else:
					error_exit("[-]GRUB2 Install Failed! Check the logfile!", SystemError)
			#x86 Absolutley supported
			elif arch == "x86":
				greenprint("[+] Installing GRUB2 for ${} to /dev/{}".format(arch, livedisk_hw_name))
				#########################
				self.current_command = \
					"grub-install --removable --target=i386-efi --boot-directory={} --efi-directory={} /dev{}".format(\
					 temp_boot_dir, efi_dir, livedisk_hw_name)
				#########################
				stepper = Stepper.step(self.current_command)
				if stepper.returncode == 1:
					greenprint("[+] GRUB2 Install Finished Successfully!")
				else:
					error_exit("[-]GRUB2 Install Failed! Check the logfile!", SystemError)
			#these are just here for readability, if it's not helping make a ticket!
			elif arch == "x64":
				greenprint("[+] Installing GRUB2 for ${} to /dev/{}".format(arch, livedisk_hw_name))
				#########################
				self.current_command = \
					"grub-install --removable --target=X86_64-efi --boot-directory={} --efi-directory={} /dev{}".format(\
					 temp_boot_dir, efi_dir, livedisk_hw_name)
				#########################
				stepper = Stepper.step(self.current_command)
				if stepper.returncode == 1:
					greenprint("[+] GRUB2 Install Finished Successfully!")
				else:
					error_exit("[-]GRUB2 Install Failed! Check the logfile!", SystemError)
		else:
			greenprint("Something WIERD happened, Throw a banana and try again!")
	
	def install_syslinux(self, livedisk_hw_name, live_disk_dir, file_source_dir, efi_dir, persistance_dir, ):
		# Copy the MBR for syslinux booting of LIVE disk 
		try:
			steps = ["dd bs=440 count=1 conv=notrunc if=/usr/lib/syslinux/mbr/gptmbr.bin of=/dev/{}".format(livedisk_hw_name) ,\
			# Install Syslinux
			# https://wiki.syslinux.org/wiki/index.php?title=HowTos
			"syslinux --install /dev/{}2".format(livedisk_hw_name) ,\
			"mv {}/isolinux {}/syslinux".format(live_disk_dir ,live_disk_dir) ,\
			"mv {}/syslinux/isolinux.bin {}/syslinux/syslinux.bin".format(live_disk_dir ,live_disk_dir ) ,\
			"mv {}/syslinux/isolinux.cfg {}/syslinux/syslinux.cfg".format(live_disk_dir ,live_disk_dir ) ,\

			# Magic, sets up syslinux configuration and layouts 
			"sed --in-place 's#isolinux/splash#syslinux/splash#' {}/boot/grub/grub.cfg".format(\
				live_disk_dir) ,\
			"sed --in-place '0,/boot=live/{s/\(boot=live .*\)$/\1 persistence/}' {}/boot/grub/grub.cfg {}/syslinux/menu.cfg".format(\
				live_disk_dir , live_disk_dir ) ,\
			"sed --in-place '0,/boot=live/{s/\(boot=live .*\)$/\1 keyboard-layouts=en locales=en_US/}' {}/boot/grub/grub.cfg {}/syslinux/menu.cfg".format(\
				live_disk_dir, live_disk_dir  ) ,\
			"sed --in-place 's#isolinux/splash#syslinux/splash#' {}/boot/grub/grub.cfg".format(\
				live_disk_dir )]
			exec_pool = self.stepper(steps)
			if exec_pool.returncode == 1:
				greenprint("[+] Syslinux Installed!") 
			elif exec_pool.returncode != 1:
				error_exit("[-]Syslinux Install Failed! Check the logfile!", SystemError)
			# Clean up!
			steps = ["umount {} {} {} {}".format(efi_dir, live_disk_dir ,persistance_dir, file_source_dir) ,\
					 "rmdir {} {} {} {}".format(efi_dir, live_disk_dir ,persistance_dir, file_source_dir)]
			exec_pool = self.stepper(steps)
			if exec_pool.returncode == 1:
				greenprint("[+] Syslinux Installed!") 
			elif stepper.returncode != 1:
				error_exit("[-]Debootstrap Failed! Check the logfile!", SystemError)

	def stage1(self, arch, sandy_path, components, repository):
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
		self.current_command = "sudo debootstrap --components {} --arch {} , bionic {} {}".format( \
												 components,arch,sandy_path,repository)
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			greenprint("[+] Debootstrap Finished Successfully!")
		elif stepper.returncode != 1:
			error_exit("[-]Debootstrap Failed! Check the logfile!")

############################################
		#resolv.conf copy
		greenprint("[+] Copying Resolv.conf")
		self.current_command = "sudo cp /etc/resolv.conf {}/etc/resolv.conf".format(sandy_path)
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			greenprint("[+] Resolv.conf copied!") 
		else:
			error_exit("[-]Copying Resolv.conf Failed! Check the logfile!")

##########################################
		# sources.list copy
		print("[+] Copying Sources.list")
		self.current_command = ["sudo cp /etc/apt/sources.list {}/etc/apt/".format(sandy_path)]
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			print("[+] Sources.list copied!") 
		else:
			error_exit("[-]Copying Sources.list Failed! Check the logfile!")

##########################################
		#mount and bind the proper volumes
		# /dev
		print("[+] Mounting /dev" )
		self.current_command = ["sudo mount -o bind /dev {}/dev".format(sandy_path)]
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mounting /dev Failed! Check the logfile!")
		# /proc
		print("[+] Mounting /proc")
	
########################################
		self.current_command = ["sudo mount -o bind -t proc /proc {}/proc".format(sandy_path)]
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mounting /proc Failed! Check the logfile!")

#######################################
		# /sys
		print("[+] Mounting /sys")
		self.current_command = ["sudo mount -o bind -t sys /sys {}/sys".format(sandy_path)]
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			print("[+] Mounted!") 
		else:
			error_exit("[-]Mounting /sys Failed! Check the logle!")

###############################################################################
		#finish setting up the basic system
	def stage2(self, sandy_path, user, password, extras):
		'''
	Establishes Chroot
		- sets username / password

		- LOG'S IN, DONT LEAVE THE COMPUTER
			-for security purposes

		- updates packages
		- installs debconf, nano, curl
		- installs extras

		'''
		steps = ["sudo chroot {} ".format(sandy_path)								,\
				 "useradd {}".format(user)											,\
				 "passwd  {}".format(password)										,\
				 "login {}".format(user)												,\
				 "sudo -S apt-get update"													,\
				 "sudo -S apt-get --no-install-recommends install {}".format(extras)	,\
				#TODO: clean the gpg error message
				 "sudo -S apt-get update"													]#,\  
				 #If you don't talk en_US
				 #["sudo -S apt-get install locales dialog"]									,\
		#sudo -S locale-gen en_US.UTF-8  # or your preferred locale
		#tzselect; TZ='Continent/Country'; export TZ  #Congure and use our local time instead of UTC; save in .prole
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	#begin setting up services
	def deboot_third_stage(self, extra_packages):
		'''
	Installs extra user packages
		'''
		steps = ["sudo -S apt install {}".format(extra_packages)]

	#Makes an interface with iproute1
	def create_iface_ipr1(self, sand_iface, sand_mac) :
		steps = [["sudo -S modprobe dummy" ,\
				 "sudo -S ip link set {} dev dummy0".format(sandy_iface) ,\
				 "sudo -S ifconfig {} hw ether {}".format(sandy_iface, sandy_mac)]
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	#Makes an interface with iproute2
	def create_iface_ipr2(self, sandy_iface):
		steps = ["ip link add {} type veth".format(sandy_iface)]
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	def del_iface1(self,sand_ip,sandy_netmask,sand_iface):
		steps = ["sudo -S ip addr del {} brd + dev {}".format(sandy_ip,sandy_netmask,sandy_iface),\
				 "sudo -S ip link delete {} type dummy".format(sandy_iface),\
				 "sudo -S rmmod dummy".format()]
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	#Deletes the SANDBOX Interface
	def del_iface2(self, sandy_iface):
		steps = ["ip link del {}".format(sandy_iface)]
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	#run this from the HOST
	def establish_network_forwarding(self, host_iface, sandy_iface):
		#Allow forwarding on HOST IFACE
		steps = ["sysctl -w net.ipv4.conf.{}.forwarding=1".format(host_iface),\
		#Allow from sandbox to outside
				 "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(sandy_iface, host_iface),\
		#Allow from outside to sandbox
				 "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(host_iface, sandy_iface)]
		for instruction in steps:
			self.current_command = instruction
			stepper = Stepper.step(self.current_command)

	#run this from the Host
	def establish_iptables(self):
		# 1. Delete all existing rules
		steps = ["iptables -F" ,\
		 # 2. Set default chain policies
				 "iptables -P INPUT DROP",\
				 "iptables -P FORWARD DROP",\
				 "iptables -P OUTPUT DROP",\
				#4. Allow ALL incoming SSH
				"iptables -A INPUT -i eth0 -p tcp --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT",\
				"iptables -A OUTPUT -o eth0 -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT",\
				# Allow incoming HTTPS
				"iptables -A INPUT -i eth0 -p tcp --dport 443 -m state --state NEW,ESTABLISHED -j ACCEPT",\
				"iptables -A OUTPUT -o eth0 -p tcp --sport 443 -m state --state ESTABLISHED -j ACCEPT",\
				# 19. Allow MySQL connection only from a specic network
				 #iptables -A INPUT -i eth0 -p tcp -s 192.168.200.0/24 --dport 3306 -m state --state NEW,ESTABLISHED -j ACCEPT
				 #iptables -A OUTPUT -o eth0 -p tcp --sport 3306 -m state --state ESTABLISHED -j ACCEPT
				# 23. Prevent DoS attack
				"iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT"]
		for instruction in steps:
			self.current_command = instruction
			Stepper.step(self.current_command)

#call via terminal
# you must specify either config or arguments
if __name__ == "__main__":
	arguments = parser.parse_args()
	#are we using config?
	if arguments.config_file == True:
		config = configparser.ConfigParser()
		config.read('debootstrapy.config')
		# user needs to set config file or arguments
		user_choice = config['Thing To Do']['choice']
		if user_choice== 'doofus':
			yellow_bold_print("YOU HAVE TO CONFIGURE THE DARN THING FIRST!")
			raise SystemExit
			sys.exit()
		# Doesnt run for choice = DEFAULT unless (look down)
		elif user_choice in config.sections or (user_choice == 'DEFAULT'):
			kwargs = config[user_choice]
			thing_to_do = CommandRunner(**kwargs)
		
		else:
			redprint("[-] Option not in config file")
	elif arguments.config_file == False:
		thing_to_do = CommandRunner(arguments.sand_hostname ,arguments.user	   ,\
					  arguments.password,	arguments.extra_extra	 ,\
					  arguments.sand_mac,	arguments.sand_ip		 ,\
					  arguments.sand_iface, arguments.sandy_netmask ,\
					  arguments.sandy_path, arguments.arch		  ,\
					  arguments.repository, arguments.components	,\
					  arguments.log_file,	arguments.host_iface	  ,\
					  arguments.internal_ip, arguments.gateway	  ,\
					  "debconf nano curl")
		if (arguments.make_disk == True) and (arguments.use_live_iso == True):
			#TODO: should be a path.. or name?
			thing_to_do.file_source = '/tmp/live.iso' # arguments.iso_name
			thing_to_do.setup_disk(diskname="",efi_dir="",persistance_dir="",temp_boot_dir="",live_disk_dir="")
			thing_to_do.move_system_files(efi_dir="",live_disk_dir="",persistance_dir="",file_source_dir="")
			thing_to_do.install_grub2(bit_size="",arch="",livedisk_hw_name="",temp_boot_dir="",efi_dir="")
			#syslinux for USB install
			#thing_to_do.install_syslinux(livedisk_hw_name="",live_disk_dir="",file_source_dir="",efi_dir="",persistance_dir="")

			pass