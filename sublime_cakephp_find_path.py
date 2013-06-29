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


class CakephpFindCoreList:
	def __init__(self):
		self.set_core_list()
		return

	def set_core_list(self):
		self.core_list = {}
		list = ["1", "2"]
		for version in list:
			file_path = sublime.packages_path() + "/sublime-cakephp-find/json/core" + version + ".json"
			f = open(file_path)
			self.core_list[version] = json.load(f)
			f.close()

# Sublime Text 2
if sublime.version().startswith('2'):
	cakephp_find_core_list = CakephpFindCoreList()
# Sublime Text 3
def plugin_loaded():
	cakephp_find_core_list = CakephpFindCoreList()


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
		self.dir_path = {}
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
		self.dir_path['authenticate'] = "Controller/Component/Auth/"
		self.dir_path['css'] = "webroot/css/"
		self.dir_path['javascript'] = "webroot/js/"
		self.dir_path['image'] = "webroot/img/"

		if self.major_version == 1:
			self.dir_path['config'] = "config/"
			self.dir_path['controller'] = "controllers/"
			self.dir_path['model'] = "models/"
			self.dir_path['view'] = "views/"
			self.dir_path['component'] = "controllers/components/"
			self.dir_path['behavior'] = "models/behaviors/"
			self.dir_path['helper'] = "views/helpers/"
			self.dir_path['lib'] = "libs/"
			self.dir_path['vendor'] = "vendors/"
			self.dir_path['layout'] = "views/layouts/"
			self.dir_path['element'] = "views/elements/"
			self.dir_path['plugin'] = "plugins/"
			self.dir_path['test'] = "tests/cases/"
			self.dir_path['controller_test'] = "tests/cases/controllers/"
			self.dir_path['model_test'] = "tests/cases/models/"
			self.dir_path['component_test'] = "tests/cases/components/"
			self.dir_path['behavior_test'] = "tests/cases/behaviors/"
			self.dir_path['helper_test'] = "tests/cases/helpers/"
			if self.folder_path['core'] is not None:
				self.dir_path['core_controller'] = "controller/"
				self.dir_path['core_model'] = "model/"
				self.dir_path['core_view'] = "view/"
				self.dir_path['core_component'] = "controller/components/"
				self.dir_path['core_model'] = "model/behaviors/"
				self.dir_path['core_helper'] = "view/helpers/"
				self.dir_path['core_lib'] = ""
		elif self.major_version == 2:
			self.dir_path['config'] = "Config/"
			self.dir_path['controller'] = "Controller/"
			self.dir_path['model'] = "Model/"
			self.dir_path['view'] = "View/"
			self.dir_path['component'] = "Controller/Component/"
			self.dir_path['behavior'] = "Model/Behavior/"
			self.dir_path['helper'] = "View/Helper/"
			self.dir_path['lib'] = "Lib/"
			self.dir_path['vendor'] = "Vendor/"
			self.dir_path['layout'] = "View/Layouts/"
			self.dir_path['element'] = "View/Elements/"
			self.dir_path['plugin'] = "Plugin/"
			self.dir_path['test'] = "Test/Case/"
			self.dir_path['controller_test'] = "Test/Case/Controller/"
			self.dir_path['model_test'] = "Test/Case/Model/"
			self.dir_path['component_test'] = "Test/Case/Controller/Component/"
			self.dir_path['behavior_test'] = "Test/Case/Model/Behavior/"
			self.dir_path['helper_test'] = "Test/Case/View/Helper/"
			if self.folder_path['core'] is not None:
				self.dir_path['core_controller'] = "Controller/"
				self.dir_path['core_model'] = "Model/"
				self.dir_path['core_view'] = "View/"
				self.dir_path['core_component'] = "Controller/Component/"
				self.dir_path['core_behavior'] = "Model/Behavior/"
				self.dir_path['core_helper'] = "View/Helper/"
				self.dir_path['core_lib'] = "Utility/"

		list = [
			'authenticate',
			'css',
			'javascript',
			'image',
			# common
			'config',
			'controller',
			'model',
			'view',
			'component',
			'behavior',
			'helper',
			'lib',
			'vendor',
			'layout',
			'element',
			'plugin',
			'test',
			# test
			'controller_test',
			'model_test',
			'component_test',
			'behavior_test',
			'helper_test',
		]
		for category in list:
			self.folder_path[category] = self.folder_path['app'] + self.dir_path[category]
		list = [
			'core_controller',
			'core_model',
			'core_view',
			'core_component',
			'core_behavior',
			'core_helper',
			'core_lib',
		]
		for category in list:
			self.folder_path[category] = self.folder_path['core'] + self.dir_path[category]

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
		dir_list = ["lib", "vendor", "view", "controller", "model", "authenticate"]
		for dir_name in dir_list:
			file_path = self.search_file_recursive(file_name + ".php", self.folder_path[dir_name])
			if file_path:
				return file_path

		dir_list = self.get_search_add_dir_list(current_file_type)
		if current_file_type == 'view' or current_file_type == 'helper':
			search_class_name = self.modify_helper_class_name(search_class_name)
		for class_type in dir_list:
			file_path = self.search_file_recursive(self.complete_file_name(class_type, search_class_name), self.folder_path[class_type])
			if file_path: return file_path

		self.search_class_file_plugin_all(search_class_name, current_file_type)

		if self.folder_path['core'] is not None:
			self.set_core_list()
			file_path = self.search_core_file_recursive(file_name, self.core_list, self.folder_path['core_list_root'])
			if file_path:
				return file_path
			for class_type in dir_list:
				file_path = self.search_core_file_recursive(self.complete_core_list_name(class_type, file_name), self.core_list, self.folder_path['core_list_root'])
				if file_path: return file_path
		return False

	def search_class_file_plugin_all(self, search_class_name, current_file_type=None, plugin_name = None):
		if self.major_version == 1:
			file_name = Inflector().underscore(search_class_name)
		elif self.major_version == 2:
			file_name = search_class_name

		file_path = self.search_plugin_file(file_name + ".php", plugin_name)
		if file_path:
			return file_path

		list = self.get_search_add_dir_list(current_file_type)
		if current_file_type == 'view' or current_file_type == 'helper':
			search_class_name = self.modify_helper_class_name(search_class_name)
		for class_type in list:
			file_path = self.search_plugin_file(self.complete_file_name(class_type, search_class_name), plugin_name)
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

	def get_search_add_dir_list(self, current_file_type = None):
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
		return list

	def modify_helper_class_name(self, class_name):
		# change class name : $form->input() -> $Form->input()
		if re.match('^[a-z]', class_name) is not None:
			class_name = class_name[0:1].upper() + class_name[1:len(class_name)]
		return class_name

	def search_plugin_file(self, search_file_name, plugin_name = None):
		#file_path = self.search_file_recursive(search_file_name, self.folder_path['plugin'])
		root = self.folder_path['plugin']
		list = os.listdir(root)
		for name in list:
			if os.path.isfile(root + name):
				continue
			if plugin_name is not None and plugin_name != name:
				continue
			if os.path.isdir(root + name):
				dir_path = root + name + "/"
				sub_dir_list = [
					'Controller/',
					'Lib/',
					'Model/',
					'View/Helper/',
					'Vendor/',
				]
				for sub_dir_name in sub_dir_list:
					file_path = self.search_file_recursive(search_file_name, dir_path + sub_dir_name)
					if file_path:
						return file_path
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
		self.core_list = cakephp_find_core_list.core_list[str(self.major_version)]

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

	def get_category_path(self, category, plugin_name = False, options = {}):
		if options.has_key('core'):
			if self.dir_path.has_key('core_' + category): return False
			return self.folder_path['core_' + category]
		if options.has_key('test'):
			if self.dir_path.has_key(category + '_test'): return False
			return self.folder_path[category + '_test']

		if not self.dir_path.has_key(category): return False
		if plugin_name:
			return self.folder_path['plugin'] + plugin_name + "/" + self.dir_path[category]
		return self.folder_path['app'] + self.dir_path[category]
