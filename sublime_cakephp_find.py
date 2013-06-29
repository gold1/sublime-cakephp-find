# -*- coding: utf-8 -*-

import sublime, sublime_plugin

if sublime.version().startswith('3'):
	from .sublime_cakephp_find_path import Path
	from .sublime_cakephp_find_text import Text
	from .sublime_cakephp_find_inflector import Inflector
	#from .dump import Dump
elif sublime.version().startswith('2'):
	from sublime_cakephp_find_path import Path
	from sublime_cakephp_find_text import Text
	from sublime_cakephp_find_inflector import Inflector
	#from dump import Dump


def set_app_path(self):
	self.path = Path()
	self.action_name = None
	self.lower_camelized_action_name = None
	self.select_word = None
	self.select_class_name = None
	self.select_sub_name = None
	self.select_sub_type = None
	if not self.path.set_app(self.view):
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
		is_css_file(self) or
		is_controller_test_file(self) or
		is_model_test_file(self) or
		is_component_test_file(self) or
		is_behavior_test_file(self) or
		is_helper_test_file(self) or
		is_plugin_file(self) or
		is_core_list_file(self) or
		is_app_file(self)):
		return True
	else:
		return False

def is_controller_file(self):
	match = self.path.match_controller_file(self.view)
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
	match = self.path.match_model_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.plural_name = Inflector().pluralize(self.singular_name)
	self.camelize_name = Inflector().camelize(Inflector().underscore(self.singular_name))
	self.current_file_type = "model"
	return True

# Theme view is not supported.
def is_view_file(self):
	(self.plural_name, self.action_name, view_extension) = self.path.match_view_file(self.view)
	if not self.plural_name:
		return False
	self.path.set_view_extension(view_extension)
	self.lower_camelized_action_name = Inflector().variablize(self.action_name)
	self.singular_name = Inflector().singularize(self.plural_name)
	self.current_file_type = "view"
	return True

def is_component_file(self):
	match = self.path.match_component_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "component"
	return True

def is_behavior_file(self):
	match = self.path.match_behavior_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "behavior"
	return True

def is_helper_file(self):
	match = self.path.match_helper_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "helper"
	return True

def is_layout_file(self):
	match = self.path.match_layout_file(self.view)
	if not match:
		return False
	self.current_file_type = "layout"
	return True

def is_css_file(self):
	match = self.path.match_css_file(self.view)
	if not match:
		return False
	self.current_file_type = "css"
	return True

def is_plugin_file(self):
	match = self.path.match_plugin_file(self.view)
	if not match:
		return False
	self.current_file_type = "plugin"
	return True

def is_controller_test_file(self):
	match = self.path.match_controller_test_file(self.view)
	if not match:
		return False
	self.plural_name = match
	self.singular_name = Inflector().singularize(self.plural_name)
	self.camelize_name = Inflector().camelize(Inflector().underscore(self.singular_name))
	self.current_file_type = "controller_test"
	return True

def is_model_test_file(self):
	match = self.path.match_model_test_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.plural_name = Inflector().pluralize(self.singular_name)
	self.camelize_name = Inflector().camelize(Inflector().underscore(self.singular_name))
	self.current_file_type = "model_test"
	return True

def is_component_test_file(self):
	match = self.path.match_component_test_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "component_test"
	return True

def is_behavior_test_file(self):
	match = self.path.match_behavior_test_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "behavior_test"
	return True

def is_helper_test_file(self):
	match = self.path.match_helper_test_file(self.view)
	if not match:
		return False
	self.singular_name = match
	self.current_file_type = "helper_test"
	return True

def is_core_list_file(self):
	match = self.path.match_core_list_file(self.view)
	if not match:
		return False
	self.current_file_type = "core"
	return True

def is_app_file(self):
	match = self.path.match_app_file(self.view)
	if not match:
		return False
	self.current_file_type = "app"
	return True

def is_word_only_controller(self):
	return (is_render_function(self) or
			is_redirect_function(self) or
			is_layout_variable(self))

def is_word_only_view(self):
	return (is_element_function(self) or
			is_javascript_function(self) or
			is_css_function(self) or
			is_tag_id_class(self) or
			is_image_function(self))

def is_word_only_helper(self):
	return is_image_function(self)

def is_word_only_layout(self):
	return (is_element_function(self) or
			is_javascript_function(self) or
			is_css_function(self) or
			is_tag_id_class(self) or
			is_image_function(self))

def is_word_only_css(self):
	return is_background_image(self)

def is_word_any_file(self):
	if (is_app_import(self) or
		is_app_uses(self) or
		is_new_class(self) or
		is_class_operator(self)):
		return True
	return False

def is_render_function(self):
	(controller_name, self.action_name, self.layout_name) = Text().match_render_function(self.select_line_str)
	if self.action_name is None:
		return False
	if controller_name is None:
		controller_name = self.plural_name
	if self.layout_name is not None:
		if self.layout_name == self.select_word:
			self.path.switch_to_category(self.view, 'layout', self.layout_name)
			return True
	self.path.switch_to_category(self.view, 'view', controller_name, self.action_name)
	return True

def is_redirect_function(self):
	(controller_name, self.action_name) = Text().match_redirect_function(self.select_line_str)
	if self.action_name is None:
		return False
	if controller_name is None:
		controller_name = self.plural_name
	file_path = self.path.search_class_file_all_dir(self.path.complete_file_name('controller', controller_name, False), self.current_file_type)
	if file_path == False:
		return False
	self.path.set_open_file_callback(Text().move_point_function, self.action_name)
	self.path.switch_to_file(file_path, self.view)
	return True

def is_layout_variable(self):
	self.layout_name = Text().match_layout_variable(self.select_line_str)
	if self.layout_name is None:
		return False
	self.path.switch_to_category(self.view, 'layout', self.layout_name)
	return True

def is_element_function(self):
	self.element_name = Text().match_element_function(self.select_line_str)
	if self.element_name is None:
		return False
	element_file_name = self.path.complete_file_name('element', self.element_name)
	file_path = self.path.search_file_recursive(element_file_name, self.path.folder_path["element"])
	if file_path == False:
		return False
	self.path.switch_to_file(file_path, self.view)
	return True

def is_javascript_function(self):
	self.javascript_name = Text().match_javascript_function(self.select_line_str)
	if self.javascript_name is None:
		return False
	javascript_file_name = self.path.complete_file_name('javascript', self.javascript_name)
	file_path = self.path.search_file_recursive(javascript_file_name, self.path.folder_path["javascript"])
	if file_path == False:
		return False
	self.path.switch_to_file(file_path, self.view)
	return True

def is_css_function(self):
	self.css_name = Text().match_css_function(self.select_line_str)
	if self.css_name is None:
		return False
	css_file_name = self.path.complete_file_name('css', self.css_name)
	file_path = self.path.search_file_recursive(css_file_name, self.path.folder_path["css"])
	if file_path == False:
		return False
	self.path.switch_to_file(file_path, self.view)
	return True

def is_tag_id_class(self):
	(id_list, class_list) = Text().match_tag_id_class(self.select_line_str)
	name = None
	type = None
	for str in id_list:
		if str == self.select_css_tag_word:
			name = str
			type = 'id'
	for str in class_list:
		if str == self.select_css_tag_word:
			name = str
			type = 'class'
	if name is None:
		return False
	list = self.path.get_css_list(name, type)
	if list is None:
		return False
	copy_word_to_find_panel(self, 'css_word')
	self.path.set_open_file_callback(Text().move_line_number, 0) # 0: dummy
	self.path.show_css_list(self.view, list)
	return True

def is_background_image(self):
	image_path = Text().match_background_image(self.select_line_str)
	if image_path is None:
		return False
	file_path = self.path.search_file_recursive(image_path, self.path.folder_path["image"])
	if file_path == False:
		return False
	self.path.execute(file_path)
	return True

def is_image_function(self):
	image_path = Text().match_html_image(self.select_line_str)
	if image_path is None:
		return False
	file_path = self.path.search_file_recursive(image_path, self.path.folder_path["image"])
	if file_path == False:
		return False
	self.path.execute(file_path)
	return True

def is_new_class(self):
	self.new_class_name = Text().match_new_class(self.select_line_str)
	if not self.new_class_name:
		return False
	file_path = self.path.search_class_file_all_dir(self.new_class_name)
	if file_path == False:
		return False
	self.path.switch_to_file(file_path, self.view)
	return True

def is_class_operator(self):
	if self.select_class_name is None:
		return False
	if self.select_class_name == "this":
		file_path = self.view.file_name()
	else:
		file_path = self.path.search_class_file_all_dir(self.select_class_name, self.current_file_type)
	if file_path == False:
		return False
	if self.select_sub_type is not None:
		if self.select_sub_type == "function":
			self.path.set_open_file_callback(Text().move_point_function, self.select_sub_name)
		elif self.select_sub_type == "variable":
			self.path.set_open_file_callback(Text().move_point_variable, self.select_sub_name)
	self.path.switch_to_file(file_path, self.view)
	return True

def is_app_import(self):
	(plugin_name, folder_name, file_name) = Text().match_app_import(self.select_line_str)
	if not file_name:
		return False
	category_path = self.path.get_category_path(folder_name.lower(), plugin_name)
	if category_path == False:
		return False
	file_path = category_path + file_name + ".php"
	self.path.switch_to_file(file_path, self.view)
	return True

def is_app_uses(self):
	(plugin_name, folder_name, file_name) = Text().match_app_uses(self.select_line_str)
	category_path = self.path.get_category_path(folder_name.lower(), plugin_name)
	if category_path == False:
		return False
	file_path = category_path + file_name + ".php"
	self.path.switch_to_file(file_path, self.view)
	return True

def copy_word_to_find_panel(self, type = 'word'):
	if type == 'word':
		region = self.select_word_region
	elif type == 'css_word':
		region = self.select_css_tag_region
	self.view.sel().add(region)
	self.view.window().run_command("show_panel", {"panel": "find"})
	self.view.window().run_command("hide_panel")
	if len(self.view.sel()) > 1:
		self.view.sel().subtract(region)

class CakeFindCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return False
		if not is_file(self):
			sublime.status_message("Can't find file type.")
			return
		(self.select_word, self.select_css_tag_word, self.select_word_region,
			self.select_css_tag_region, self.select_line_str, self.select_class_name,
			self.select_sub_name, self.select_sub_type) = Text().get_cursol_info(self.view)

		found = False
		if self.current_file_type == "controller":
			found = is_word_only_controller(self)
		elif self.current_file_type == "view":
			found = is_word_only_view(self)
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
		self.path.switch_to_category(self.view, 'model', self.singular_name)

class CakeSwitchToControllerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if not is_file(self):
			sublime.status_message("Can't switch to contoroller.")
			return
		if self.action_name is not None:
			self.path.set_open_file_callback(Text().move_point_controller_action, self.action_name)
		self.path.switch_to_category(self.view, 'controller', self.plural_name)

class CakeSwitchToViewCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if not is_file(self) or self.action_name is None:
			sublime.status_message("Can't switch to view.")
			return
		self.path.switch_to_category(self.view, 'view', self.plural_name, self.action_name)

class CakeSwitchToTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self):
			return
		if is_controller_file(self):
			self.path.switch_to_category(self.view, 'controller_test', self.plural_name)
			return
		elif is_controller_test_file(self):
			self.path.switch_to_category(self.view, 'controller', self.plural_name)
			return
		elif is_model_file(self):
			self.path.switch_to_category(self.view, 'model_test', self.singular_name)
			return
		elif is_model_test_file(self):
			self.path.switch_to_category(self.view, 'model', self.singular_name)
			return
		elif is_component_file(self):
			self.path.switch_to_category(self.view, 'component_test', self.singular_name)
			return
		elif is_component_test_file(self):
			self.path.switch_to_category(self.view, 'component', self.singular_name)
			return
		elif is_behavior_file(self):
			self.path.switch_to_category(self.view, 'behavior_test', self.singular_name)
			return
		elif is_behavior_test_file(self):
			self.path.switch_to_category(self.view, 'behavior', self.singular_name)
			return
		elif is_helper_file(self):
			self.path.switch_to_category(self.view, 'helper_test', self.singular_name)
			return
		elif is_helper_test_file(self):
			self.path.switch_to_category(self.view, 'helper', self.singular_name)
			return
		sublime.status_message("Can't switch to testcase.")

class CakeShowDirectoryListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.get_this_dir(self.view), self.view)

class CakeShowControllerListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["controller"], self.view)

class CakeShowModelListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["model"], self.view)

class CakeShowViewListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["view"], self.view)

class CakeShowComponentListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["component"], self.view)

class CakeShowBehaviorListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["behavior"], self.view)

class CakeShowHelperListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["helper"], self.view)

class CakeShowLibListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["lib"], self.view)

class CakeShowLayoutListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["layout"], self.view)

class CakeShowCssListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["css"], self.view)

class CakeShowJavascriptListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["javascript"], self.view)

class CakeShowElementListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["element"], self.view)

class CakeShowConfigListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["config"], self.view)

class CakeShowPluginListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["plugin"], self.view)

class CakeShowTestListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not set_app_path(self): return
		self.path.show_dir_list(self.path.folder_path["test"], self.view)


