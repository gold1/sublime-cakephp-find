# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import re
import os
import time
import subprocess
import threading
import functools
from command_thread import CommandThread
from inflector import Inflector

class Path:
	def __init__(self):
		return

	def set_app(self, view):
		self.core = None
		self.open_file_view = None
		self.open_file_callback = None
		self.open_file_callback_arg = None
		self.app = self.find_app(view)
		if self.app == False:
			return False
		self.root = os.path.dirname(os.path.dirname(self.app)) + "/"
		if not self.set_major_version():
			return False
		self.set_regexp()
		return True

	def find_app(self, view):
		dirname = os.path.dirname(self.convert_file_path(view))
		count = 0
		count_limit = 5
		while count < count_limit:
			if (os.path.exists(dirname + "/config/core.php") or
				os.path.exists(dirname + "/Config/core.php")):
				return dirname + "/"
			count += 1
			dirname = os.path.dirname(dirname)
		sublime.status_message("Can't find app path.")
		return False

	def convert_file_path(self, view):
		file_path = view.file_name()
		if os.name == "nt":
			file_path = file_path.replace("\\", "/")
		return file_path

	def set_major_version(self):
		self.major_version = self.get_major_version_from_file()
		if self.major_version is None:
			self.major_version = self.get_major_version_from_path()
		if self.major_version is None:
			sublime.status_message("Can't find CakePHP version file.")
			return False
		return True

	def get_major_version_from_path(self):
		if os.path.exists(self.app + "controllers"):
			return 1
		elif os.path.exists(self.app + "Controller"):
			return 2
		return None

	def get_major_version_from_file(self):
		dirname = os.path.dirname(os.path.dirname(self.app))
		if os.path.exists(dirname + "/cake/VERSION.txt"):
			for line in open(dirname + "/cake/VERSION.txt", "r"):
				match = re.search("([1-9])\.([0-9])\.([0-9])+", line)
				if match is not None:
					# 1
					self.core = dirname + "/cake/libs/"
					return int(match.group(1))
		elif os.path.exists(dirname + "/lib/Cake/VERSION.txt"):
			for line in open(dirname + "/lib/Cake/VERSION.txt", "r"):
				match = re.search("([1-9])\.([0-9])\.([0-9])+", line)
				if match is not None:
					# 2
					self.core = dirname + "/lib/Cake/"
					return int(match.group(1))
		return None

	def set_regexp(self):
		if self.major_version == 1:
			self.config_folder_name = "config"
			self.controller_folder_name = "controllers"
			self.model_folder_name = "models"
			self.view_folder_name = "views"
			self.component_folder_name = "components"
			self.behavior_folder_name = "behaviors"
			self.helper_folder_name = "helpers"
			self.lib_folder_name = "libs"
			self.vendor_folder_name = "vendors"
			self.layout_folder_name = "layouts"
			self.element_folder_name = "elements"
			self.plugin_folder_name = "plugins"
			self.test_folder_name = "tests/cases"
			self.core_controller_folder_name = "controller"
			self.core_model_folder_name = "model"
			self.core_view_folder_name = "view"
			self.core_component_folder_name = "components"
			self.core_behavior_folder_name = "behaviors"
			self.core_helper_folder_name = "helpers"
			self.core_lib_folder_name = ""
		elif self.major_version == 2:
			self.config_folder_name = "Config"
			self.controller_folder_name = "Controller"
			self.model_folder_name = "Model"
			self.view_folder_name = "View"
			self.component_folder_name = "Component"
			self.behavior_folder_name = "Behavior"
			self.helper_folder_name = "Helper"
			self.lib_folder_name = "Lib"
			self.vendor_folder_name = "Vendor"
			self.layout_folder_name = "Layouts"
			self.element_folder_name = "Elements"
			self.plugin_folder_name = "Plugin"
			self.test_folder_name = "Test/Case"
			self.core_controller_folder_name = "Controller"
			self.core_model_folder_name = "Model"
			self.core_view_folder_name = "View"
			self.core_component_folder_name = "Component"
			self.core_behavior_folder_name = "Behavior"
			self.core_helper_folder_name = "Helper"
			self.core_lib_folder_name = "Utility/"

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
			regexp = self.app + "controllers/([a-zA-Z0-9_]+)_controller\.php$"
		elif self.major_version == 2:
			regexp = self.app + ".+/([a-zA-Z0-9_]+)Controller\.php$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_model_file(self, view):
		regexp = self.app + self.model_folder_name + "/([^/]+)\.php"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_behavior_file(view) != False):
			return False
		return match.group(1)

	def match_view_file(self, view):
		regexp = self.app + self.view_folder_name + "/([^/]+)/([^/]+/)?([^/.]+)\.([a-z]+)$"
		match = self.match(regexp, self.convert_file_path(view))
		if (match == False or
			self.match_helper_file(view) != False or
			self.match_layout_file(view) != False):
			return False
		return match.group(1), match.group(3), match.group(4)

	def match_component_file(self, view):
		if self.major_version == 1:
			regexp = (self.app + self.controller_folder_name + "/" +
				self.component_folder_name + "/([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.app + self.controller_folder_name + "/" +
				self.component_folder_name + "/([a-zA-Z0-9_]+)Component\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_behavior_file(self, view):
		regexp = (self.app + self.model_folder_name + "/" + self.behavior_folder_name +
			"/([^/]+)\.php")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_helper_file(self, view):
		if self.major_version == 1:
			regexp = (self.app + self.view_folder_name + "/" +
				self.helper_folder_name + "/([a-zA-Z0-9_]+)\.php$")
		elif self.major_version == 2:
			regexp = (self.app + self.view_folder_name + "/" +
				self.helper_folder_name + "/([a-zA-Z0-9_]+)Helper\.php$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_layout_file(self, view):
		regexp = (self.app + self.view_folder_name + "/" + self.layout_folder_name +
			"/([^/.]+)\.([a-z]+)$")
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def match_css_file(self, view):
		regexp = self.app + "webroot/css/(.+)\.css$"
		match = self.match(regexp, self.convert_file_path(view))
		if match == False:
			return False
		return match.group(1)

	def dir_type(self, type):
		if type == "controller":
			return self.app + self.controller_folder_name + "/"
		elif type == "model":
			return self.app + self.model_folder_name + "/"
		elif type == "view":
			return self.app + self.view_folder_name + "/"
		elif type == "component":
			return (self.app + self.controller_folder_name + "/" +
				"/" + self.component_folder_name + "/")
		elif type == "helper":
			return (self.app + self.view_folder_name + "/" +
				"/" + self.helper_folder_name + "/")
		elif type == "behavior":
			return (self.app + self.model_folder_name + "/" +
				"/" + self.behavior_folder_name + "/")
		elif type == "lib":
			return self.app + self.lib_folder_name + "/"
		elif type == "vendor":
			return self.app + self.vendor_folder_name + "/"
		elif type == "layout":
			return (self.app + self.view_folder_name + "/" +
				self.layout_folder_name + "/")
		elif type == "element":
			return (self.app + self.view_folder_name + "/" +
				self.element_folder_name + "/")
		elif type == "javascript":
			return self.app + "webroot/js/"
		elif type == "css":
			return self.app + "webroot/css/"
		elif type == "image":
			return self.app + "webroot/img/"
		elif type == "config":
			return self.app + self.config_folder_name + "/"
		elif type == "plugin":
			return self.app + self.plugin_folder_name + "/"
		elif type == "test":
			return self.app + self.test_folder_name + "/"
		elif type == "core_component":
			return (self.core + self.core_controller_folder_name + "/" +
				"/" + self.core_component_folder_name + "/")
		elif type == "core_helper":
			return (self.core + self.core_view_folder_name + "/" +
				"/" + self.core_helper_folder_name + "/")
		elif type == "core_behavior":
			return (self.core + self.core_model_folder_name + "/" +
				"/" + self.core_behavior_folder_name + "/")
		elif type == "core_lib":
			return self.core + self.core_lib_folder_name
		return False

	def switch_to_controller(self, view, plural_name):
		file_path = self.dir_type("controller") + self.controller_file_name(plural_name)
		return self.switch_to_file(file_path, view)

	def switch_to_model(self, view, singular_name):
		file_path = self.dir_type("model") + singular_name + ".php"
		return self.switch_to_file(file_path, view)

	def switch_to_view(self, view, plural_name, action_name, view_extension):
		file_path = self.dir_type("view") + plural_name + "/" + action_name + "." + view_extension
		return self.switch_to_file(file_path, view)

	def switch_to_layout(self, view, layout_name, view_extension):
		file_path = self.dir_type("layout") + layout_name + "." + view_extension
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
				while thread_parent.is_open_file_loading and count < 30:
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
		if re.match(self.root, dir_path) is None:
			return
		if dir_path != self.root:
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
			if path[len(path) -len(extension) -1: len(path)] == "." + extension:
				return True
		return False

	def execute(self, path):
		if os.name == "nt":
			command = [path]
		elif os.name == "mac":
			command = ["open", path]
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

	def search_class_file_all_dir(self, search_class_name):
		if self.major_version == 1:
			file_name = Inflector().underscore(search_class_name)
		elif self.major_version == 2:
			file_name = search_class_name
		dir_list = ["lib", "vendor", "component", "helper", "behavior", "controller", "model"]
		for dir_name in dir_list:
			file_path = self.search_file_recursive(file_name + ".php", self.dir_type(dir_name))
			if file_path:
				return file_path

		if self.core is not None:
			file_path = self.search_file_recursive(file_name + ".php", self.dir_type("core_lib"))
			if file_path: return file_path

		file_path = self.search_file_recursive(self.complete_file_name_component(search_class_name), self.dir_type("component"))
		if file_path: return file_path
		file_path = self.search_file_recursive(self.complete_file_name_helper(search_class_name), self.dir_type("helper"))
		if file_path: return file_path
		file_path = self.search_file_recursive(self.complete_file_name_behavior(search_class_name), self.dir_type("behavior"))
		if file_path: return file_path

		if self.core is not None:
			file_path = self.search_file_recursive(self.complete_file_name_component(search_class_name), self.dir_type("core_component"))
			if file_path: return file_path
			file_path = self.search_file_recursive(self.complete_file_name_helper(search_class_name), self.dir_type("core_helper"))
			if file_path: return file_path
			file_path = self.search_file_recursive(self.complete_file_name_behavior(search_class_name), self.dir_type("core_behavior"))
			if file_path: return file_path
		return False

	def controller_file_name(self, plural_name):
		if self.major_version == 1:
			return plural_name + "_controller.php"
		elif self.major_version == 2:
			return plural_name + "Controller.php"

	def complete_file_name_controller(self, name):
		if self.major_version == 1:
			return Inflector().underscore(name) + '_controller.php'
		elif self.major_version == 2:
			return name + 'Controller.php'
		return None

	def complete_file_name_model(self, name):
		if self.major_version == 1:
			return Inflector().underscore(name) + '.php'
		elif self.major_version == 2:
			return name + '.php'
		return None

	def complete_file_name_component(self, name):
		if self.major_version == 1:
			return Inflector().underscore(name) + '.php'
		elif self.major_version == 2:
			return name + 'Component.php'
		return None

	def complete_file_name_behavior(self, name):
		if self.major_version == 1:
			return Inflector().underscore(name) + '.php'
		elif self.major_version == 2:
			return name + 'Behavior.php'
		return None

	def complete_file_name_helper(self, name):
		if self.major_version == 1:
			return Inflector().underscore(name) + '.php'
		elif self.major_version == 2:
			return name + 'Helper.php'
		return None

	def complete_file_name_element(self, name):
		return Inflector().underscore(name) + '.ctp'

	def complete_file_name_javascript(self, name):
		if re.search("\.js$", name) is not None:
			return name
		return name + '.js'

	def complete_file_name_css(self, name):
		if re.search("\.css$", name) is not None:
			return name
		return name + '.css'



