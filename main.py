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

	# dont use this here, not time for it to be parsed yet
	#arguments = parser.parse_args()

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
					redprint(error_lines)

				return step
				
			elif blocking == False:
				# TODO: not implemented yet				
				pass
				
		except Exception as derp:
			yellow_bold_print("[-] Shell Command failed!")
			return derp

class CommandRunner:
	'''
NARF!
	'''
	def __init__(self, kwargs):
		for (k, v) in kwargs.items():
			setattr(self, k, v)


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

#call via terminal
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
		pass