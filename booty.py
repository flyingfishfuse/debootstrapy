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

It will do some disk operations necessary for usb live installs

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

class GrubbyClass:
	def __init__(self):
		pass
	
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
		bit_sizey = ["32","64"]
		archy = {'arm'   : 'arm-efi'  ,\
				 'x86'   : 'i386-efi' ,\
				 'amd64' : 'X86-64-efi'
				}
		craft_cmd = 'grub-install --removable --target={} --boot-directory={} --efi-directory={} /dev{}'.format(\
					archy.get(arch),\
					temp_boot_dir,\
					efi_dir,\
					livedisk_hwname)
		greenprint("[+] Installing GRUB2 for {} to /dev/{}".format(arch, livedisk_hw_name)) 
		self.current_command = craft_cmd
		stepper = Stepper.step(self.current_command)
		if stepper.returncode == 1:
			greenprint("[+] GRUB2 Install Finished Successfully!")
		else:
			error_exit("[-]GRUB2 Install Failed! Check the logfile!", stepper)
	
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
