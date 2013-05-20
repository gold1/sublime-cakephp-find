# -*- coding: utf-8 -*-

import sublime, sublime_plugin
from inflector import Inflector
from path import Path
from text import Text

path = Path()

def set_app_path(self):
	self.action_name = None
	self.lower_camelized_action_name = None
	self.view_extension = "ctp"
	self.select_word = None
	self.select_class_name = None
	self.select_sub_name = None
	self.select_sub_type = None
	if not path.set_app(self.view):
		return False
	return True

def is_file(self):
	if (is_controller_file(self) or
		is_model_file(self) or
		is_view_file(self) or
		is_component_file(self) or
		is_behavior_file(self) or
		is_helper_file(self) or
		is_layout_file(self) or
		is_css_file(self)):
		return True
	else:
		return False

def is_controller_file(self):
	match = path.match_controller_file(self.view)
	if not match:
		return False
	self.plural_name = match
	self.action_name = Text().find_action_name_this_place(self.view)
	if self.action_name is not None:
		# private function
		if self.action_name[0] == '_':
			self.action_name = None
		else:
			self.lower_camelized_action_name = Inflector().variablize(self.action_name)
			self.snake_action_name = Inflector().underscore(self.action_name)
	self.singular_name = Inflector().singularize(self.plural_name)
	self.camelize_name = Inflector().camelize(Inflector().underscore(self.singular_name))
	self.current_file_type = "controller"
	return True

def is_model_file(self):
	match = path.match_model_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.plural_name = Inflector().pluralize(self.singular_name)
	self.current_file_type = "model"
	return True

# Theme view is not supported.
def is_view_file(self):
	match = path.match_view_file(self.view)
	if not match:
		return False
	(self.plural_name, self.action_name, self.view_extension) = match
	self.lower_camelized_action_name = Inflector().variablize(self.action_name)
	self.singular_name = Inflector().singularize(self.plural_name)
	self.current_file_type = "view"
	return True

def is_component_file(self):
	match = path.match_component_file(self.view)
	if not match:
		return False
	self.current_file_type = "component"
	return True

def is_behavior_file(self):
	match = path.match_behavior_file(self.view)
	if not match:
		return False
	self.current_file_type = "behavior"
	return True

def is_helper_file(self):
	match = path.match_helper_file(self.view)
	if not match:
		return False
	self.current_file_type = "helper"
	return True

def is_layout_file(self):
	match = path.match_layout_file(self.view)
	if not match:
		return False
	self.current_file_type = "layout"
	return True

def is_css_file(self):
	match = path.match_css_file(self.view)
	if not match:
		return False
	self.current_file_type = "css"
	return True

def is_word_only_controller(self):
	return (is_render_function(self) or
			is_layout_variable(self) or
			is_loaded_component(self) or
			is_loaded_model(self) or
			is_loaded_helper(self))

def is_word_only_model(self):
	return is_loaded_behavior(self)

def is_word_only_view(self):
	return (is_element_function(self) or
			is_javascript_function(self) or
			is_css_function(self) or
			is_image_function(self))

def is_word_only_component(self):
	return is_loaded_component(self)

def is_word_only_behavior(self):
	return is_loaded_behavior(self)

def is_word_only_helper(self):
	return (is_loaded_helper(self) or
			is_image_function(self))

def is_word_only_layout(self):
	return (is_element_function(self) or
			is_javascript_function(self) or
			is_css_function(self) or
			is_image_function(self))

def is_word_only_css(self):
	return is_background_image(self)

def is_word_any_file(self):
	if (is_new_class(self) or
		is_class_operator(self)):
		return True
	return False

def is_render_function(self):
	(self.action_name, self.layout_name) = Text().match_render_function(self.select_line_str)
	if self.action_name is None:
		return False
	if self.layout_name is not None:
		if self.layout_name == self.select_word:
			path.switch_to_layout(self.view, self.layout_name, self.view_extension)
			return True
	path.switch_to_view(self.view, self.plural_name, self.action_name, self.view_extension)
	return True

def is_layout_variable(self):
	self.layout_name = Text().match_layout_variable(self.select_line_str)
	if self.layout_name is None:
		return False
	path.switch_to_layout(self.view, self.layout_name, self.view_extension)
	return True

def is_loaded_model(self):
	if not Text().is_loaded_class(self.select_word, self.select_line_str):
		return False
	model_file_name = path.complete_file_name_model(self.select_word)
	file_path = path.search_file_recursive(model_file_name, path.dir_type("model"))
	if file_path == False:
		return False
	path.switch_to_file(file_path, self.view)
	return True

def is_loaded_component(self):
	if not Text().is_loaded_class(self.select_word, self.select_line_str):
		return False
	component_file_name = path.complete_file_name_component(self.select_word)
	file_path = path.search_file_recursive(component_file_name, path.dir_type("component"))
	if file_path == False:
		file_path = path.search_file_recursive(component_file_name, path.dir_type("core_component"))
		if file_path == False:
			return False
	path.switch_to_file(file_path, self.view)
	return True

def is_loaded_helper(self):
	if not Text().is_loaded_class(self.select_word, self.select_line_str):
		return False
	helper_file_name = path.complete_file_name_helper(self.select_word)
	file_path = path.search_file_recursive(helper_file_name, path.dir_type("helper"))
	if file_path == False:
		file_path = path.search_file_recursive(helper_file_name, path.dir_type("core_helper"))
		if file_path == False:
			return False
	path.switch_to_file(file_path, self.view)
	return True

def is_loaded_behavior(self):
	if not Text().is_loaded_class(self.select_word, self.select_line_str):
		return False
	behavior_file_name = path.complete_file_name_behavior(self.select_word)
	file_path = path.search_file_recursive(behavior_file_name, path.dir_type("behavior"))
	if file_path == False:
		file_path = path.search_file_recursive(behavior_file_name, path.dir_type("core_behavior"))
		if file_path == False:
			return False
	path.switch_to_file(file_path, self.view)
	return True

def is_element_function(self):
	self.element_name = Text().match_element_function(self.select_line_str)
	if self.element_name is None:
		return False
	element_file_name = path.complete_file_name_element(self.element_name)
	file_path = path.search_file_recursive(element_file_name, path.dir_type("element"))
	if file_path == False:
		return False
	path.switch_to_file(file_path, self.view)
	return True

def is_javascript_function(self):
	self.javascript_name = Text().match_javascript_function(self.select_line_str)
	if self.javascript_name is None:
		return False
	javascript_file_name = path.complete_file_name_javascript(self.javascript_name)
	file_path = path.search_file_recursive(javascript_file_name, path.dir_type("javascript"))
	if file_path == False:
		return False
	path.switch_to_file(file_path, self.view)
	return True

def is_css_function(self):
	self.css_name = Text().match_css_function(self.select_line_str)
	if self.css_name is None:
		return False
	css_file_name = path.complete_file_name_css(self.css_name)
	file_path = path.search_file_recursive(css_file_name, path.dir_type("css"))
	if file_path == False:
		return False
	path.switch_to_file(file_path, self.view)
	return True

def is_background_image(self):
	image_path = Text().match_background_image(self.select_line_str)
	if image_path is None:
		return False
	file_path = path.search_file_recursive(image_path, path.dir_type("image"))
	if file_path == False:
		return False
	path.execute(file_path)
	return True

def is_image_function(self):
	image_path = Text().match_html_image(self.select_line_str)
	if image_path is None:
		return False
	file_path = path.search_file_recursive(image_path, path.dir_type("image"))
	if file_path == False:
		return False
	path.execute(file_path)
	return True

def is_new_class(self):
	(self.new_class_name, self.new_class_var_name) = Text().match_new_class(self.select_line_str)
	if not self.new_class_name:
		return False
	file_path = path.search_class_file_all_dir(self.new_class_name)
	if file_path == False:
		return False
	path.switch_to_file(file_path, self.view)
	return True

def is_class_operator(self):
	if self.select_class_name is None:
		return False
	if self.select_class_name == "this":
		file_path = self.view.file_name()
	else:
		file_path = path.search_class_file_all_dir(self.select_class_name)
	if file_path == False:
		return False
	if self.select_sub_type is not None:
		if self.select_sub_type == "function":
			path.set_open_file_callback(Text().move_point_function, self.select_sub_name)
		elif self.select_sub_type == "variable":
			path.set_open_file_callback(Text().move_point_variable, self.select_sub_name)
	path.switch_to_file(file_path, self.view)
	return True

class CakeFindCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return False
		if not is_file(self):
			sublime.status_message("Can't find file type.")
			return
		(self.select_word, self.select_line_str, self.select_class_name,
			self.select_sub_name, self.select_sub_type) = Text().get_cursol_info(self.view)

		found = False
		if self.current_file_type == "controller":
			found = is_word_only_controller(self)
		elif self.current_file_type == "model":
			found = is_word_only_model(self)
		elif self.current_file_type == "view":
			found = is_word_only_view(self)
		elif self.current_file_type == "component":
			found = is_word_only_component(self)
		elif self.current_file_type == "behavior":
			found = is_word_only_behavior(self)
		elif self.current_file_type == "helper":
			found = is_word_only_helper(self)
		elif self.current_file_type == "layout":
			found = is_word_only_layout(self)
		elif self.current_file_type == "css":
			found = is_word_only_css(self)
		if found:
			return
		if not is_word_any_file(self):
			sublime.status_message("Can't find file.")
			return

class CakeSwitchToModelCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if not is_file(self):
			sublime.status_message("Can't switch to model.")
			return
		path.switch_to_model(self.view, self.singular_name)

class CakeSwitchToControllerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if not is_file(self):
			sublime.status_message("Can't switch to contoroller.")
			return
		if self.action_name is not None:
			path.set_open_file_callback(Text().move_point_controller_action, self.action_name)
		path.switch_to_controller(self.view, self.plural_name)

class CakeSwitchToViewCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if not is_file(self) or self.action_name is None:
			sublime.status_message("Can't switch to view.")
			return
		path.switch_to_view(self.view, self.plural_name, self.action_name, self.view_extension)

class CakeShowDirectoryListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.get_this_dir(self.view), self.view)

class CakeShowControllerListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("controller"), self.view)

class CakeShowModelListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("model"), self.view)

class CakeShowViewListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("view"), self.view)

class CakeShowComponentListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("component"), self.view)

class CakeShowBehaviorListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("behavior"), self.view)

class CakeShowHelperListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("helper"), self.view)

class CakeShowLibListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("lib"), self.view)

class CakeShowLayoutListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("layout"), self.view)

class CakeShowCssListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("css"), self.view)

class CakeShowJavascriptListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("javascript"), self.view)

class CakeShowElementListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("element"), self.view)

class CakeShowConfigListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("config"), self.view)

class CakeShowPluginListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("plugin"), self.view)

class CakeShowTestListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		path.show_dir_list(path.dir_type("test"), self.view)


