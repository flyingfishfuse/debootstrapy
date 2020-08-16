# -*- coding: utf-8 -*-
################################################################################
##			debootstrapy - a linux tool for using debootstrap				  ##
################################################################################
# Copyright (c) 2020 Adam Galindo											  ##
#																			  ##
# Permission is hereby granted, free of charge, to any person obtaining a copy##
# of this software and associated documentation files (the "Software"),to deal##
# in the Software without restriction, including without limitation the rights##
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell   ##
# copies of the Software, and to permit persons to whom the Software is		  ##
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
This is a test of the command framework

It will chroot into the folder of your choice from commandline args

"""
import os
import sys
import inspect
import logging 
import pathlib
import pkgutil
import argparse
import subprocess
import configparser
from pathlib import Path
from io import BytesIO,StringIO
from importlib import import_module

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
## Dynamic imports
###################################################################################
def dynamic_import(module_to_import:str, name_as:str):
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

###################################################################################
# Commandline Arguments
###################################################################################
# If the user is running the program as a script we parse the arguments or use the 
# config file. 
# If the user is importing this as a module for usage as a command framework we do
# not activate the argument or configuration file parsing engines
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='python/bash based, distro repacker')
	parser.add_argument('--user',
								 dest	= 'user',
								 action  = "store" ,
								 default = "derp" ,
								 help	= "The username to be userd" )
	parser.add_argument('--password',
								 dest	= 'password',
								 action  = "store" ,
								 default = 'password' ,
								 help	= "The password to said username" )
	parser.add_argument('--device',
								 dest	= 'device',
								 action  = "store" ,
								 default = '/home/moop/Desktop/sandbox' ,
								 help	= "Device name, including partition number, to mount for chroot" )
	parser.add_argument('--chroot-path',
								 dest	= 'chroot_path',
								 action  = "store" ,
								 default = '/home/moop/Desktop/sandbox' ,
								 help	= "Full Path of the folder to make/mount for chroot" )
	parser.add_argument('--logfile',
								 dest	= 'log_file',
								 action  = "store" ,
								 default = './chroot_log.txt' ,
								 help	= 'logfile name' )

class Stepper:
#getattr, setattr and self.__dict__
	'''
	steps = {"command_name"  : ["string with shell command"		  , "[-] failure message", "[+] success message" ] ,
		 	 "command_name2" : ["another string with a shell command", "[-] failure message", "[+] success message" ] ,}
	'''
	def __init__(self, kwargs):
		for (k, v) in kwargs.items():
			setattr(self, k, v)
		self.script_cwd		   	= pathlib.Path().absolute()
		self.script_osdir	   	= pathlib.Path(__file__).parent.absolute()
		self.logging.basicConfig(filename=self.log_file, 
								format='%(asctime)s %(message)s', 
								filemode='w')
		self.logger		   		= logging.getLogger()
		self.logger.setLevel(logging.DEBUG)
		debug_message			= lambda message: logger.debug(blueprint(message)) 
		info_message	 		= lambda message: logger.info(greenprint(message)) 
		warning_message  		= lambda message: logger.warning(yellow_bold_print(message)) 
		error_message			= lambda message: logger.error(redprint(message)) 
		critical_message 		= lambda message: logger.critical(yellow_bold_print(message)) 

	def error_exit(self, message : str, exception : Exception):
		redprint(message)
		print(exception.with_traceback)
		sys.exit()
	
	def step_test(self, dict_of_commands : dict):
		example  = {"command_name"  : ["string with shell command", "[+] success message", "[-] failure message" ]}
		example2 = {"command_name"  : ["string with shell command"		  , "[-] failure message", "[+] success message" ] ,
		 	 		"command_name2" : ["another string with a shell command", "[-] failure message", "[+] success message" ] ,}
		try:
			for instruction in example.values(), example2.values():
				cmd 	= instruction[0]
				success = instruction[1]
				fail 	= instruction[2]
				self.current_command = cmd
				stepper = self.exec_command(self.current_command)
				if stepper.returncode == 1 :
					return success
				else:
					return fail
		except Exception as derp:
			return derp

	def step(self, dict_of_commands : dict):
		try:
			for instruction in dict_of_commands.values():
				cmd 	= instruction[0]
				success = instruction[1]
				fail 	= instruction[2]
				self.current_command = cmd
				stepper = self.exec_command(self.current_command)
				if stepper.returncode == 1 :
					return success
				else:
					return fail
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

class Chroot:
	'''
	fuck it, we doin' this
	'''
	def __init__(self, kwargs):
		for (k, v) in kwargs.items():
			setattr(self, k, v)
		
	def chroot(self):
		steps = { 'mount_dev' : ["sudo mount -o bind /dev {}/dev".format(self.sandy_path)					   ,\
							 	 "[+] Mounted /dev on {}!".format(self.sandy_path)							   ,\
								 "[-] Mounting /dev on {} Failed! Check the logfile!".format(self.sandy_path) ],\
				 'mount_proc' : ["sudo mount -o bind /dev {}/dev".format(self.sandy_path)					   ,\
								 "[+] Mounted /proc on {}!".format(self.sandy_path)							   ,\
								 "[-] Mounting /proc on {} Failed! Check the logfile!".format(self.sandy_path)],\
				 'mount_sys'  : ["sudo mount -o bind /dev {}/dev".format(self.sandy_path)					   ,\
								 "[+] Mounted /proc on {}!".format(self.sandy_path)							   ,\
								 "[-] Mounting /proc on {} Failed! Check the logfile!".format(self.sandy_path) ]}
	#self.current_command = steps['mount_dev']
	stepper = Stepper.step(steps=steps)
	if stepper.returncode == 1:
		print("")
	else:
		error_exit()

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