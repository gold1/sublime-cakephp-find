# -*- coding: utf-8 -*-

import sublime
import os
import sys
import subprocess
import threading
import functools

class CommandThread(threading.Thread):
	def __init__(self, command):
		self.command = command
		self.stdin = None
		self.stdout = subprocess.PIPE
		threading.Thread.__init__(self)

	def timeout(self, callback, *args):
		sublime.set_timeout(functools.partial(callback, *args), 0)

	def print_result(self, message):
		if message is not None:
			print(message)

	def run(self):
		callback = self.print_result
		try:
			if sys.platform.startswith('darwin'): # Mac OS X
				output = subprocess.call(self.command)
			elif os.name == "posix": # linux
				output = subprocess.call(self.command)
			elif os.name == "nt": # windows
				output = os.startfile(self.command)
			self.timeout(callback, output)
		except subprocess.CalledProcessError, e:
			self.timeout(callback, e.returncode)
		except:
			self.timeout(callback, "Error.")
