# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import json
import re
import os
import sys
import time
import subprocess
import threading
import functools
if sublime.version().startswith('3'):
	from .sublime_cakephp_find_inflector import Inflector
elif sublime.version().startswith('2'):
	from sublime_cakephp_find_inflector import Inflector


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
		except (subprocess.CalledProcessError, e):
			self.timeout(callback, e.returncode)
		except:
			self.timeout(callback, "Error.")


class Path:
	def __init__(self):
		return

	def set_app(self, view):
		self.folder_path = {}
		self.folder_path['core'] = None
		self.folder_path['core_list_root'] = None
		self.view_extension = 'ctp'
		self.core_list = None
		self.open_file_view = None
		self.open_file_callback = None
		self.open_file_callback_arg = None
		(self.folder_path['root'], self.folder_path['app']) = self.find_root(view)
		if self.folder_path['root'] == False:
			return False
		if not self.set_major_version():
			return False
		self.set_core_list_root()
		self.set_folder_path()
		return True

	def find_root(self, view):
		dirname = os.path.dirname(self.convert_file_path(view))
		count = 0
		count_limit = 7
		while count < count_limit:
			if (os.path.exists(dirname + "/config/core.php") or
				os.path.exists(dirname + "/Config/core.php")):
				return os.path.dirname(dirname) + "/", dirname + "/"
			# core file
			elif (os.path.exists(dirname + "/app/config/core.php") or
				os.path.exists(dirname + "/app/Config/core.php")):
				return dirname + "/", dirname + "/app/"
			count += 1
			dirname = os.path.dirname(dirname)
		sublime.status_message("Can't find app path.")
		return False, False

	def convert_file_path(self, view):
		file_path = view.file_name()
		if os.name == "nt":
			file_path = file_path.replace("\\", "/")
		return file_path

	def set_major_version(self):
		self.major_version = self.get_major_version_from_file()
		if self.major_version is not None:
			if self.major_version == 1:
				self.folder_path['core'] = self.folder_path['root'] + "cake/libs/"
			elif self.major_version == 2:
				self.folder_path['core'] = self.folder_path['root'] + "lib/Cake/"
		else:
			self.major_version = self.get_major_version_from_path()
		if self.major_version is None:
			sublime.status_message("Can't find CakePHP version file.")
			return False
		return True

	def get_major_version_from_file(self):
		list = ["cake/VERSION.txt", "lib/Cake/VERSION.txt"]
		for path in list:
			if os.path.exists(self.folder_path['root'] + path):
				for line in open(self.folder_path['root'] + path, "r"):
					match = re.search("([1-9])\.([0-9])\.([0-9])+", line)
					if match is not None:
						return int(match.group(1))
		return None

	def get_major_version_from_path(self):
		if os.path.exists(self.folder_path['app'] + "controllers"):
			return 1
		elif os.path.exists(self.folder_path['app'] + "Controller"):
			return 2
		return None

	def set_folder_path(self):
		self.folder_path['authenticate'] = self.folder_path['app'] + "Controller/Component/Auth/"
		self.folder_path['css'] = self.folder_path['app'] + "webroot/css/"
		self.folder_path['javascript'] = self.folder_path['app'] + "webroot/js/"
		self.folder_path['image'] = self.folder_path['app'] + "webroot/img/"

		if self.major_version == 1:
			self.folder_path['config'] = self.folder_path['app'] + "config/"
			self.folder_path['controller'] = self.folder_path['app'] + "controllers/"
			self.folder_path['model'] = self.folder_path['app'] + "models/"
			self.folder_path['view'] = self.folder_path['app'] + "views/"
			self.folder_path['component'] = self.folder_path['app'] + "controllers/components/"
			self.folder_path['behavior'] = self.folder_path['app'] + "models/behaviors/"
			self.folder_path['helper'] = self.folder_path['app'] + "views/helpers/"
			self.folder_path['lib'] = self.folder_path['app'] + "libs/"
			self.folder_path['vendor'] = self.folder_path['app'] + "vendors/"
			self.folder_path['layout'] = self.folder_path['app'] + "views/layouts/"
			self.folder_path['element'] = self.folder_path['app'] + "views/elements/"
			self.folder_path['plugin'] = self.folder_path['app'] + "plugins/"
			self.folder_path['test'] = self.folder_path['app'] + "tests/cases/"
			self.folder_path['controller_test'] = self.folder_path['app'] + "tests/cases/controllers/"
			self.folder_path['model_test'] = self.folder_path['app'] + "tests/cases/models/"
			self.folder_path['component_test'] = self.folder_path['app'] + "tests/cases/controllers/components/"
			self.folder_path['behavior_test'] = self.folder_path['app'] + "tests/cases/models/behaviors/"
			self.folder_path['helper_test'] = self.folder_path['app'] + "tests/cases/views/helpers/"
			if self.folder_path['core'] is not None:
				self.folder_path['core_controller'] = self.folder_path['core'] + "controller/"
				self.folder_path['core_model'] = self.folder_path['core'] + "model/"
				self.folder_path['core_view'] = self.folder_path['core'] + "view/"
				self.folder_path['core_component'] = self.folder_path['core'] + "conroller/components/"
				self.folder_path['core_behavior'] = self.folder_path['core'] + "model/behaviors/"
				self.folder_path['core_helper'] = self.folder_path['core'] + "view/helpers/"
				self.folder_path['core_lib'] = self.folder_path['core'] + ""
		elif self.major_version == 2:
			self.folder_path['config'] = self.folder_path['app'] + "Config/"
			self.folder_path['controller'] = self.folder_path['app'] + "Controller/"
			self.folder_path['model'] = self.folder_path['app'] + "Model/"
			self.folder_path['view'] = self.folder_path['app'] + "View/"
			self.folder_path['component'] = self.folder_path['app'] + "Controller/Component/"
			self.folder_path['behavior'] = self.folder_path['app'] + "Model/Behavior/"
			self.folder_path['helper'] = self.folder_path['app'] + "View/Helper/"
			self.folder_path['lib'] = self.folder_path['app'] + "Lib/"
			self.folder_path['vendor'] = self.folder_path['app'] + "Vendor/"
			self.folder_path['layout'] = self.folder_path['app'] + "View/Layouts/"
			self.folder_path['element'] = self.folder_path['app'] + "View/Elements/"
			self.folder_path['plugin'] = self.folder_path['app'] + "Plugin/"
			self.folder_path['test'] = self.folder_path['app'] + "Test/Case/"
			self.folder_path['controller_test'] = self.folder_path['app'] + "Test/Case/Controller/"
			self.folder_path['model_test'] = self.folder_path['app'] + "Test/Case/Model/"
			self.folder_path['component_test'] = self.folder_path['app'] + "Test/Case/Controller/Component/"
			self.folder_path['behavior_test'] = self.folder_path['app'] + "Test/Case/Model/Behavior/"
			self.folder_path['helper_test'] = self.folder_path['app'] + "Test/Case/View/Helper/"
			if self.folder_path['core'] is not None:
				self.folder_path['core_controller'] = self.folder_path['core'] + "Controller/"
				self.folder_path['core_model'] = self.folder_path['core'] + "Model/"
				self.folder_path['core_view'] = self.folder_path['core'] + "View/"
				self.folder_path['core_component'] = self.folder_path['core'] + "Conroller/Component/"
				self.folder_path['core_behavior'] = self.folder_path['core'] + "Model/Behavior/"
				self.folder_path['core_helper'] = self.folder_path['core'] + "View/Helper/"
				self.folder_path['core_lib'] = self.folder_path['core'] + "Utility/"

	def get_this_dir(self, view):
		return os.path.dirname(self.convert_file_path(view))

	def match(self, pattern, string):
		match = re.search(pattern, string)
		if match is None:
			return False
		else:
			return match

	def match_controller_file(self, view):
		if self.major_version == 1:
			regexp = self.folder_path['app'] + "controllers/([a-zA-Z0-9_]+)_controller\.php$"
		elif self.major_version == 2:
			regexp = self.folder_path['app'] + ".+/([a-zA-Z0-9_]+)Controller\.php$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_model_file(self, view):
		regexp = self.folder_path['model'] + "([^/]+)\.php"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_behavior_file(view) != False):
			return False
		return match.group(1)

	def match_view_file(self, view):
		regexp = self.folder_path['view'] + "([^/]+)/([^/]+/)?([^/.]+)\.([a-z]+)$"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_helper_file(view) != False or
			self.match_layout_file(view) != False):
			return False, False, False
		return match.group(1), match.group(3), match.group(4)

	def match_component_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['component'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['component'] + "([a-zA-Z0-9_]+)Component\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_behavior_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['behavior'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['behavior'] + "([a-zA-Z0-9_]+)Behavior\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_helper_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['helper'] + "([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['helper'] + "([a-zA-Z0-9_]+)Helper\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_layout_file(self, view):
		regexp = (self.folder_path['layout'] + "/([^/.]+)\.([a-z]+)$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_css_file(self, view):
		regexp = self.folder_path['css'] + "(.+)\.css$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_plugin_file(self, view):
		regexp = (self.folder_path['plugin'] + "(.+/)*([a-zA-Z0-9_]+)\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		# match.group(2) : file_name
		return True

	def match_controller_test_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['controller_test'] + "([a-zA-Z0-9_]+)_controller\.test\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['controller_test'] + "([a-zA-Z0-9_]+)ControllerTest\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_model_test_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['model_test'] + "([^/]+)\.test\.php")
		elif self.major_version == 2:
			regexp = (self.folder_path['model_test'] + "([^/]+)Test\.php")
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_behavior_file(view) != False):
			return False
		return match.group(1)

	def match_component_test_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['component_test'] + "([a-zA-Z0-9_]+)\.test\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['component_test'] + "([a-zA-Z0-9_]+)ComponentTest\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_behavior_test_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['behavior_test'] + "([^/]+)\.test\.php")
		elif self.major_version == 2:
			regexp = (self.folder_path['behavior_test'] + "([^/]+)BehaviorTest\.php")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_helper_test_file(self, view):
		if self.major_version == 1:
			regexp = (self.folder_path['helper_test'] + "([a-zA-Z0-9_]+)\.test\.php$")
		elif self.major_version == 2:
			regexp = (self.folder_path['helper_test'] + "([a-zA-Z0-9_]+)HelperTest\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_core_list_file(self, view):
		if self.folder_path['core_list_root'] is None:
			return False
		regexp = (self.folder_path['core_list_root'] + "(.+/)*([a-zA-Z0-9_\.]+)\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_app_file(self, view):
		regexp = (self.folder_path['app'] + "(.+/)*([a-zA-Z0-9_\-\.]+)$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(2)

	def switch_to_category(self, view, category, name, option_name = None):
		if (category == 'controller' or
			category == 'model' or
			category == 'component' or
			category == 'behavior' or
			category == 'helper' or
			category == 'layout' or
			category == 'controller_test' or
			category == 'model_test' or
			category == 'component_test' or
			category == 'behavior_test' or
			category == 'helper_test'):
			file_path = (self.folder_path[category] + self.complete_file_name(category, name))
		elif (category == 'view'):
			# option_name : action_name
			file_path = (self.folder_path[category] + name + "/" + 
				self.complete_file_name('view', option_name))
		else:
			return False
		return self.switch_to_file(file_path, view)

	def switch_to_file(self, file_path, view):
		if os.path.exists(file_path):
			self.open_file(file_path, view)
			return True
		else:
			if sublime.ok_cancel_dialog("Make new file?"):
				open(file_path, "w")
				if os.path.exists(file_path):
					self.open_file(file_path, view)
					return True
				else:
					sublime.error_message("Can't find " + file_path)
		return False

	def open_file(self, file_path, view):
		self.open_file_view = view.window().open_file(file_path)
		if self.open_file_callback is None:
			return

		thread_parent = self
		self.check_open_file_loading()
		class OpenFileThread(threading.Thread):
			def run(self):
				count = 0
				while thread_parent.is_open_file_loading and count < 20:
					time.sleep(0.1)
					sublime.set_timeout(thread_parent.check_open_file_loading, 0)
					count += 1
				if not thread_parent.is_open_file_loading:
					sublime.set_timeout(functools.partial(thread_parent.open_file_callback,
										thread_parent.open_file_view,
										thread_parent.open_file_callback_arg), 0)
		OpenFileThread().start()

	def check_open_file_loading(self):
		self.is_open_file_loading = self.open_file_view.is_loading()

	def set_open_file_callback(self, callback, *arg):
		self.open_file_callback = callback
		self.open_file_callback_arg = arg

	def show_dir_list(self, dir_path, view):
		if not dir_path: return

		self.show_list_view = view
		if not dir_path.endswith("/"):
			dir_path = dir_path + "/"
		dir_list = []
		file_list = []
		# search dir list
		for file in os.listdir(dir_path):
			if os.path.isfile(dir_path + file):
				file_list.append(file)
			else:
				dir_list.append(file)
		dir_list.sort()
		file_list.sort()
		# create list
		self.show_list_dir = dir_path
		self.show_list = []
		# out of app dir
		if re.match(self.folder_path['root'], dir_path) is None:
			return
		if dir_path != self.folder_path['root']:
			self.show_list = ["../"]
		for dir_name in dir_list:
			self.show_list.append(dir_name + "/")
		for file_name in file_list:
			self.show_list.append(file_name)
		view.window().show_quick_panel(self.show_list, self.result_select_dir_list)

	def result_select_dir_list(self, result):
		if result == -1: return
		if result == 0 and self.show_list[0] == "../":
			self.show_dir_list(os.path.dirname(os.path.dirname(self.show_list_dir)) + "/",
				self.show_list_view)
			return
		# open file or move dir
		selected = self.show_list[result]
		if selected.endswith("/"):
			self.show_dir_list(self.show_list_dir + selected, self.show_list_view)
			return
		if self.is_execute_extension(self.show_list_dir + selected):
			self.execute(self.show_list_dir + selected)
		else:
			self.switch_to_file(self.show_list_dir + selected, self.show_list_view )

	def is_execute_extension(self, path):
		list = ["jpeg", "jpe", "jpg", "gif", "png", "bmp", "dib", "tif", "tiff", "ico",
			"doc", "docx", "dot", "dotx", "xls", "xlsx", "ppt", "pptx",
			"ai", "dwt", "fla", "indd", "psd", "pdf",
			"asf", "asx", "acd", "au", "avi", "aif", "mid", "midi", "mov", "mp3", "mpg", "swf", "wav", "wma",
			"zip", "lzh", "tar", "gz", "tgz", "cab",
			"exe", "dll", "jar"]
		for extension in list:
			if path[-len("." + extension):] == "." + extension:
				return True
		return False

	def execute(self, path):
		if sys.platform.startswith('darwin'): # Mac OS X
			command = ['open', path]
		elif os.name == "posix": # linux
			command = ['xdg-open', path]
		elif os.name == "nt": # windows
			command = path
		else:
			return
		thread = CommandThread(command)
		thread.start()

	def search_file_recursive(self, search_file_name, root):
		# "subdir/file", "root/" -> "file", "root/subdir/"
		if len(search_file_name.split("/")) > 1:
			dirs = search_file_name.split("/")
			search_file_name = dirs.pop()
			root = root + "/".join(dirs) + "/"
		if not os.path.exists(root):
			return False

		list = os.listdir(root)
		for name in list:
			if os.path.isdir(root + name):
				dir_result = self.search_file_recursive(search_file_name, root + name + "/")
				if dir_result == False:
					continue
				return dir_result
			if os.path.isfile(root + name) and search_file_name == name:
				return root + name
		return False

	def search_class_file_all_dir(self, search_class_name, current_file_type=None):
		if self.major_version == 1:
			file_name = Inflector().underscore(search_class_name)
		elif self.major_version == 2:
			file_name = search_class_name
		dir_list = ["lib", "vendor", "component", "helper", "behavior", "controller", "model", "plugin"]
		for dir_name in dir_list:
			file_path = self.search_file_recursive(file_name + ".php", self.folder_path[dir_name])
			if file_path:
				return file_path

		if self.folder_path['core'] is not None:
			self.set_core_list()
			file_path = self.search_core_file_recursive(file_name, self.core_list, self.folder_path['core_list_root'])
			if file_path: return file_path

		list = ["component", "helper", "behavior", "authenticate"]
		if current_file_type is not None:
			# sort list
			# because 'Session' word find 'SessionComponent' and 'SessionHelper'
			change_file_type = None
			if current_file_type == 'controller' or current_file_type == 'component':
				change_file_type = 'component'
			if current_file_type == 'view' or current_file_type == 'helper':
				change_file_type = 'helper'
			if current_file_type == 'model' or current_file_type == 'behavior':
				change_file_type = 'behavior'
			if change_file_type is not None:
				list.remove(change_file_type)
				list.insert(0, change_file_type)
			# change class name : $form->input() -> $Form->input()
			if change_file_type == 'helper' and re.match('^[a-z]', search_class_name) is not None:
				search_class_name = search_class_name[0:1].upper() + search_class_name[1:len(search_class_name)]
		for class_type in list:
			file_path = self.search_file_recursive(self.complete_file_name(class_type, search_class_name), self.folder_path[class_type])
			if file_path: return file_path

		if self.folder_path['core'] is not None:
			for class_type in list:
				file_path = self.search_core_file_recursive(self.complete_core_list_name(class_type, file_name), self.core_list, self.folder_path['core_list_root'])
				if file_path: return file_path
		return False

	def search_core_file_recursive(self, search_file_name, content_dict, root):
		for class_name, file_name in content_dict.items():
			if class_name[0:1] == '>':
				file_path = self.search_core_file_recursive(search_file_name, file_name['c'], root + file_name['n'] + '/')
				if file_path: return file_path
			elif search_file_name == class_name:
				if file_name == '':
					return root + class_name + '.php'
				else:
					return root + file_name
		return False

	def complete_file_name(self, type, name, ext_flag = True):
		ext = add_ext = '.php'
		if not ext_flag: add_ext = ''
		new_name = self.check_and_remove_tail(name, ext)

		if type == 'controller':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(new_name), '_controller') + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Controller') + add_ext
		elif type == 'model':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return Inflector().camelize(new_name) + add_ext
		elif type == 'component':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Component') + add_ext
		elif type == 'behavior':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Behavior') + add_ext
		elif type == 'helper':
			if self.major_version == 1:
				return Inflector().underscore(new_name) + add_ext
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(new_name), 'Helper') + add_ext
		elif type == 'authenticate':
			# self.major_version : 1 is not exist
			return self.check_and_add_tail(Inflector().camelize(new_name), 'Authenticate') + add_ext
		elif type == 'controller_test':
			if self.major_version == 1:
				new_name = self.check_and_add_tail(Inflector().underscore(new_name), '_controller')
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
			elif self.major_version == 2:
				new_name = self.check_and_add_tail(Inflector().camelize(new_name), 'Controller')
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
		elif type == 'model_test':
			if self.major_version == 1:
				new_name = Inflector().underscore(new_name)
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
			elif self.major_version == 2:
				new_name = Inflector().camelize(new_name)
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
		elif type == 'component_test':
			if self.major_version == 1:
				new_name = Inflector().underscore(new_name)
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
			elif self.major_version == 2:
				new_name = self.check_and_add_tail(Inflector().camelize(new_name), 'Component')
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
		elif type == 'behavior_test':
			if self.major_version == 1:
				new_name = Inflector().underscore(new_name)
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
			elif self.major_version == 2:
				new_name = self.check_and_add_tail(Inflector().camelize(new_name), 'Behavior')
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
		elif type == 'helper_test':
			if self.major_version == 1:
				new_name = Inflector().underscore(new_name)
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext
			elif self.major_version == 2:
				new_name = self.check_and_add_tail(Inflector().camelize(new_name), 'Helper')
				return self.check_and_remove_tail(self.add_file_path_test(new_name), '.php') + add_ext

		if (type == 'element' or
			type == 'view' or
			type == 'layout'):
			ext = add_ext = '.' + self.view_extension
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return Inflector().underscore(new_name) + add_ext
		elif type == 'javascript':
			ext = add_ext = '.js'
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return new_name + add_ext
		elif type == 'css':
			ext = add_ext = '.css'
			if not ext_flag: add_ext = ''
			new_name = self.check_and_remove_tail(name, ext)
			return new_name + add_ext
		return None

	def complete_core_list_name(self, type, name):
		if type == 'component':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_component')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Component')
		elif type == 'behavior':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_behavior')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Behavior')
		elif type == 'helper':
			if self.major_version == 1:
				return self.check_and_add_tail(Inflector().underscore(name), '_helper')
			elif self.major_version == 2:
				return self.check_and_add_tail(Inflector().camelize(name), 'Helper')
		return None

	def check_and_add_tail(self, name, add_name):
		if len(name) < len(add_name) or name[-len(add_name):] != add_name:
			name += add_name
		return name

	def check_and_remove_tail(self, name, remove_name):
		if len(name) >= len(remove_name) and name[-len(remove_name):] == remove_name:
			name = name[0:len(name)-len(remove_name)]
		return name

	def add_file_path_test(self, file_path):
		new_file_path = self.check_and_remove_tail(file_path, '.php')
		if self.major_version == 1:
			new_file_path = self.check_and_remove_tail(new_file_path, '.test')
			return new_file_path + '.test.php'
		elif self.major_version == 2:
			new_file_path = self.check_and_remove_tail(new_file_path, 'Test')
			return file_path + 'Test.php'
		return None

	def set_core_list(self):
		if self.core_list is not None:
			return
		file_path = sublime.packages_path() + "/sublime-cakephp-find/json/core" + str(self.major_version) + ".json"
		f = open(file_path)
		self.core_list = json.load(f)
		f.close()

	def set_core_list_root(self):
		if self.folder_path['core'] is None:
			return
		if self.major_version == 1:
			self.folder_path['core_list_root'] = self.folder_path['root'] + 'cake/'
		elif self.major_version == 2:
			self.folder_path['core_list_root'] = self.folder_path['root'] + 'lib/'

	def set_view_extension(self, ext):
		self.view_extension = ext

	def get_css_list(self, word, type):
		file_list = []
		for file in os.listdir(self.folder_path['css']):
			if os.path.isfile(self.folder_path['css'] + file):
				file_list.append(file)
		if len(file_list) == 0: return None
		file_list.sort()

		if type == 'id':
			regexp = "#" + word
		elif type == 'class':
			regexp = "\." + word

		css_list = []
		for file in file_list:
			line_num = 0
			for line in open(self.folder_path['css'] + file, 'r'):
				match = re.search(regexp, line)
				if match is not None:
					result = []
					result.append(file)
					result.append(line_num)
					css_list.append(result)
					break
				line_num += 1

		if len(css_list) == 0:
			return None
		return css_list

	def show_css_list(self, view, css_list):
		self.show_list_view = view
		self.css_list = css_list
		if len(css_list) == 1:
			self.result_css_list(0)
			return

		show_list = []
		for info in css_list:
			show_list.append(info[0])
		view.window().show_quick_panel(show_list, self.result_css_list)

	def result_css_list(self, result):
		if result == -1: return
		self.set_open_file_callback(self.open_file_callback, self.css_list[result][1])
		# open file
		selected = self.css_list[result][0]
		self.switch_to_file(self.folder_path['css'] + selected, self.show_list_view)
