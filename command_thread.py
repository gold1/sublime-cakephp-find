# -*- coding: utf-8 -*-

import sublime
import os
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
		print(message)

	def run(self):
		try:
			shell = os.name == 'nt'
			proc = subprocess.Popen(self.command,
				stdout=self.stdout, stderr=subprocess.STDOUT,
				stdin=subprocess.PIPE,
				shell=shell, universal_newlines=True)
			output = proc.communicate(self.stdin)[0]
			if not output:
				output = ''
			callback = self.print_result
			self.timeout(callback, output)
		except subprocess.CalledProcessError, e:
			self.timeout(callback, e.returncode)
		except:
			self.timeout(callback, "Error.")
