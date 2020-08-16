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
import logging 
import pathlib
import argparse
import subprocess
from pathlib import Path

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

class Stepper:
#getattr, setattr and self.__dict__
	'''
Steps through the command list
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
		self.debug_message			= lambda message: logger.debug(blueprint(message)) 
		self.info_message	 		= lambda message: logger.info(greenprint(message)) 
		self.warning_message  		= lambda message: logger.warning(yellow_bold_print(message)) 
		self.error_message			= lambda message: logger.error(redprint(message)) 
		self.critical_message 		= lambda message: logger.critical(yellow_bold_print(message)) 

	def error_exit(self, message : str, exception : Exception):
		self.error_message(message = message)
		print(exception.with_traceback)
		sys.exit()
	
	def step_test(self, dict_of_commands : dict):
		self.example  = {"ls_root"  : ["ls -la /", "[+] success message", "[-] failure message" ]}
		self.example2 = {"ls_etc"  : ["ls -la /etc"		  , "[-] failure message", "[+] success message" ] ,
		 	 			 "ls_home" : ["ls -la ~/", "[-] failure message", "[+] success message" ] ,}
		try:
			for instruction in self.example.values(), self.example2.values():
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
					self.info_message(output_line)
				for error_lines in derp[0].decode(encoding='utf-8').split('\n'):
					self.critical_message(error_lines)

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

	def ls_test(self):
		steps = { 'ls_user' : ["ls -la ~/",
							 	 "[+] Command Sucessful",
								 "[-]  Command Failed! Check the logfile!"],
				 'ls_root' : ["ls -la /",
								 "[+] Command Sucessful!",
								 "[-]  Command Failed! Check the logfile!"],
				 'ls_etc'  : ["ls -la /etc",
								 "[+] Command Sucessful",
								 "[-] ls -la Failed! Check the logfile!"],
				 'cowsay_dicks'	 :	['lolcat cowsay "Magikarp used Dick Slap"',
					  			 "[+] LOL!",
					  			 "[-] DICKS Failed! Check the logfile!"]}
		#self.current_command = steps['mount_dev']
		#stepper = Stepper.step(steps=self.current_command)
	
		stepper = Stepper.step(steps=steps)
		if stepper.returncode == 1:
			self.info_message("wat")
		else:
			error_exit("oh no", stepper)
		
	def step_on_through(self):
		steps = { 'mount_dev': 
					["sudo mount -o bind /dev {}/dev".format(self.chroot_base),
					 "[+] Mounted /dev on {}!".format(self.chroot_base),
					 "[-] Mounting /dev on {} Failed! Check the logfile!".format(self.chroot_base) ],
				 'mount_proc': 
				 	["sudo mount -o bind /proc {}/proc".format(self.chroot_base),
					 "[+] Mounted /proc on {}!".format(self.chroot_base),
					 "[-] Mounting /proc on {} Failed! Check the logfile!".format(self.chroot_base)],
				 'mount_sys': 
				 	["sudo mount -o bind /sys {}/sys".format(self.chroot_base),
					 "[+] Mounted /sys on {}!".format(self.chroot_base),
					 "[-] Mounting /sys on {} Failed! Check the logfile!".format(self.chroot_base)],
	 	 	 	 'move_resolvconf':
	 	 	 	 	 ["sudo cp /etc/resolv.conf {}/etc/resolv.conf".format(self.chroot_base),
	 	 	 	 	 "[+] Resolv.conf Copied!",
	 	 	 	 	 "[-] Failure To Copy Resolv.conf! Check the logfile!"],
				'chroot':	
					["sudo chroot {} ".format(chroot_base),
					"[+] Success!",
					"[-] Failed! Check the logfile!"]
				}
	#self.current_command = steps['mount_dev']
		stepper = Stepper.step(steps=steps)
		if stepper.returncode == 1:
			self.info_message("[+] Chroot Sucessful!")
		else:
			error_exit('[-] Chroot Failure, Check the Logfile!', stepper)

if __name__ == "__main__":
	#arguments = parser.parse_args()
	#if 	arguments.use_args == True:
	Stepper.step_test()
	Chroot.ls_test()
