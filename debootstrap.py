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

It will do the debootstrap stuff

"""
import os
import sys
import pathlib
import subprocess
from pathlib import Path

__author__ = 'Adam Galindo'
__email__ = 'null@null.com'
__version__ = '1'
__license__ = 'GPLv3'

class Debootstrap:
	'''
	Does disk stuff
	'''
	def __init__(self, kwargs):
		for (k, v) in kwargs.items():
			setattr(self, k, v)
	
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
