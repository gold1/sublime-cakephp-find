# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import threading
import functools

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


class FindParentThread(threading.Thread):
	def __init__(self, parent, find_type, find_name, new_list = [], count = 0):
		# delete duplicate
		list = []
		for name in new_list:
			new_name = name.encode('utf-8')
			if not new_name in list:
				list.append(new_name)
		self.parent = parent
		self.find_type = find_type
		self.find_name = find_name
		self.list = list
		self.count = count + 1
		threading.Thread.__init__(self)

	def run(self):
		# search list class
		class_name = self.list.pop(0)
		file_path = self.parent.path.search_class_file_all_dir(class_name)
		if file_path == False:
			return
		# read class file
		f = open(file_path)
		file_content = f.read()
		f.close()
		# search method or variable
		if self.find_type == "function":
			move_point = Text().search_point_function(self.find_name, file_content)
		elif self.find_type == "variable":
			move_point = Text().search_point_variable(self.find_name, file_content)
		elif self.find_type == "class_head":
			move_point = Text().search_point_class_head(file_content)
		if move_point != -1:
			sublime.set_timeout(functools.partial(self.parent.find_parent_open_file,
								file_path), 0)
			return
		# search parent class
		(extend, interfaces) = Text().match_extend_implement(file_content)
		if extend:
			self.list.append(extend)
		traits = Text().match_use_trait(file_content)
		if traits:
			self.list += traits
		# stop roop if bug
		if self.count > 100:
			return
		if len(self.list) == 0:
			return
		# call next
		sublime.set_timeout(functools.partial(self.parent.find_parent_call_next,
							self.list,
							self.count), 0)


class SublimeCakephpFind(sublime_plugin.TextCommand):
	def set_app_path(self):
		self.path = Path()
		self.current_file_type = None
		self.action_name = None
		self.plural_name = None
		self.singular_name = None
		self.lower_camelized_action_name = None
		self.select_word = None
		self.select_class_name = None
		self.select_sub_name = None
		self.select_sub_type = None
		self.user_settings = self.view.settings().get('sublime_cakephp_find')
		if not self.path.set_app(self.view, self.user_settings):
			return False
		return True

	def is_file(self):
		if (self.is_controller_file() or
			self.is_model_file() or
			self.is_view_file() or
			self.is_component_file() or
			self.is_behavior_file() or
			self.is_helper_file() or
			self.is_layout_file() or
			self.is_css_file() or
			self.is_plugin_file() or
			self.is_core_list_file() or
			self.is_app_file()):
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
		if self.plural_name is None:
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
		return (self.is_render_function() or
				self.is_redirect_function() or
				self.is_layout_variable())

	def is_word_only_view(self):
		return (self.is_element_function() or
				self.is_javascript_function() or
				self.is_css_function() or
				self.is_tag_id_class() or
				self.is_image_function())

	def is_word_only_helper(self):
		return self.is_image_function()

	def is_word_only_layout(self):
		return (self.is_element_function() or
				self.is_javascript_function() or
				self.is_css_function() or
				self.is_tag_id_class() or
				self.is_image_function())

	def is_word_only_css(self):
		return self.is_background_image()

	def is_word_any_file(self):
		if (self.is_app_import() or
			self.is_app_uses() or
			self.is_new_class() or
			self.is_local_function() or
			self.is_email_template() or
			self.is_datasource() or
			self.is_route() or
			self.is_namespace_use() or
			self.is_include_require() or
			self.is_extend_implement() or
			self.is_configure_read() or
			self.is_enclosed_word() or
			self.is_class_operator()):
			return True
		return False

	def is_render_function(self):
		(plugin_name, controller_name, view_name, self.layout_name) = Text().match_render_function(self.select_line_str)
		if not view_name:
			return False
		if self.layout_name:
			if self.layout_name == self.select_word:
				self.path.switch_to_category(self.view, 'layout', self.layout_name)
				return True
		if not controller_name:
			controller_name = self.plural_name
		return self.path.switch_to_view(self.view, controller_name, view_name, plugin_name)

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
		(plugin_name, self.layout_name) = Text().match_layout_variable(self.select_line_str)
		if self.layout_name is None:
			return False
		layout_file_name = self.path.complete_file_name('layout', self.layout_name)
		category_path = self.path.get_category_path('layout', plugin_name)
		if category_path == False:
			return False
		file_path = category_path + layout_file_name
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_element_function(self):
		(plugin_name, self.element_name) = Text().match_element_function(self.select_line_str)
		if self.element_name is None:
			return False
		element_file_name = self.path.complete_file_name('element', self.element_name)
		category_path = self.path.get_category_path('element', plugin_name)
		if category_path == False:
			return False
		file_path = category_path + element_file_name
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
		self.path.set_open_file_callback(Text().move_line_number, 0) # 0: dummy
		self.copy_word_to_find_panel('css_word')
		self.path.search_css_list(self.view, name, type)
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
		if not self.new_class_name or self.new_class_name != self.select_word:
			return False
		file_path = self.path.search_class_file_all_dir(self.new_class_name, self.current_file_type)
		if file_path == False:
			return False
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_enclosed_word(self):
		if not self.enclosed_word:
			return False
		if self.is_fixture():
			return True

		split = self.enclosed_word.split('.')
		class_name = split[-1]
		if len(split) > 1:
			plugin_name = split[0]
			file_path = self.path.search_class_file_plugin_all(class_name, self.current_file_type, plugin_name)
		else:
			file_path = self.path.search_class_file_all_dir(class_name, self.current_file_type)
		if not file_path:
			return False
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_fixture(self):
		split = self.enclosed_word.split('.')
		if len(split) == 1 or not Text().match_fixture(self.enclosed_word):
			return False

		type = split[0]
		if type == "plugin":
			plugin_name = split[1]
			class_name = split[2]
		else:
			plugin_name = False
			class_name = split[1]
		return self.path.switch_to_fixture(self.view, type, class_name, plugin_name)

	def is_class_operator(self):
		if self.select_class_name is None:
			return False
		if (self.select_class_name == "this" or
			self.select_class_name == "static" or
			self.select_class_name == "self" or
			self.select_class_name == "parent"):
			return self.find_type_this()
		# search class
		list = [self.select_class_name]
		if self.select_sub_type is None:
			self.select_sub_type = "class_head"
			self.select_sub_name = ""
		thread = FindParentThread(self, self.select_sub_type, self.select_sub_name, list)
		thread.start()
		return True

	def is_app_import(self):
		(plugin_name, folder_name, file_name) = Text().match_app_import(self.select_line_str)
		if not file_name:
			return False
		if plugin_name and folder_name:
			category_path = self.path.get_category_path(folder_name.lower(), plugin_name)
			if not category_path:
				return False
			file_path = category_path + file_name + ".php"
			self.path.switch_to_file(file_path, self.view)
		else:
			file_path = self.path.search_class_file_all_dir(file_name, self.current_file_type)
			if not file_path:
				return False
			self.path.switch_to_file(file_path, self.view)
		return True

	def is_app_uses(self):
		(plugin_name, folder_name, file_name) = Text().match_app_uses(self.select_line_str)
		if not file_name:
			return False
		if plugin_name and folder_name:
			category_path = self.path.get_category_path(folder_name.lower(), plugin_name)
			if not category_path:
				return False
			file_path = category_path + file_name + ".php"
			self.path.switch_to_file(file_path, self.view)
		else:
			file_path = self.path.search_class_file_all_dir(file_name, self.current_file_type)
			if not file_path:
				return False
			self.path.switch_to_file(file_path, self.view)
		return True

	def is_local_function(self):
		(plugin_name, msg_id) = Text().match_local_function(self.select_line_str)
		if not msg_id:
			return False
		self.path.set_open_file_callback(Text().move_point_msgid, msg_id)
		return self.path.switch_to_locale(self.view, plugin_name)

	def is_datasource(self):
		(plugin_name, text) = Text().match_datasource(self.select_line_str)
		if not text:
			return False
		return self.path.path_to_datasource(self.view, plugin_name, text)

	def is_email_template(self):
		(template_name, layout_name) = Text().match_email_template(self.select_line_str)
		if not template_name and not layout_name:
			return False
		if (layout_name and layout_name != template_name and
			(not template_name or self.enclosed_word == layout_name)):
			(plugin_name, file_name) = self.path.split_plugin_name(layout_name)
			category_path = self.path.get_category_path('email_layout', plugin_name)
		elif template_name:
			(plugin_name, file_name) = self.path.split_plugin_name(template_name)
			category_path = self.path.get_category_path('email', plugin_name)
		else:
			return False
		if not category_path:
			return False
		return self.path.switch_to_email_template(self.view, category_path, file_name)

	def is_route(self):
		if not self.path.is_routes_file(self.view):
			return False
		(plugin_name, controller_name, action_name) = Text().match_route(self.select_line_str)
		if not controller_name:
			return False
		category_path = self.path.get_category_path("controller", plugin_name)
		if not category_path:
			return False
		file_path = category_path + self.path.complete_file_name('controller', controller_name)
		if action_name:
			self.path.set_open_file_callback(Text().move_point_function, action_name)
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_include_require(self):
		(up_dir_count, path_words) = Text().match_include_require(self.select_line_str)
		if not path_words:
			return False
		file_path = self.path.convert_include_require_word(self.view, up_dir_count, path_words)
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_namespace_use(self):
		class_name = Text().match_namespace_use(self.select_line_str)
		if not class_name:
			return False
		file_path = self.path.search_class_file_all_dir(class_name, self.current_file_type)
		if file_path == False:
			return False
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_extend_implement(self):
		(extend, interfaces) = Text().match_extend_implement(self.select_line_str)
		class_name = False
		if extend:
			if extend == self.select_word:
				class_name = extend
		if interfaces:
			for interface in interfaces:
				if interface == self.select_word:
					class_name = interface
		# When a cursor is outside
		if not class_name:
			if extend:
				class_name = extend
			elif interfaces:
				class_name = interfaces[0]
		if not class_name:
			return False
		file_path = self.path.search_class_file_all_dir(class_name, self.current_file_type)
		if file_path == False:
			return False
		self.path.switch_to_file(file_path, self.view)
		return True

	def is_configure_read(self):
		word = Text().match_configure_read(self.select_line_str)
		if not word or word != self.enclosed_word:
			return False
		load_files = self.path.get_configure_load_files(Text().match_configure_load, self.view)
		if len(load_files) == 0:
			return False
		path_app_list = self.path.get_configure_file(Text().match_configure_load_variables, load_files, word)
		if len(path_app_list) == 0:
			return False
		self.path.set_open_file_callback(Text().move_line_number, 0) # 0: dummy
		self.path.show_configure_list(self.view, path_app_list)
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

	def find_type_this(self):
		if self.select_sub_type is None:
			return False
		if (self.select_class_name == "this" or
			self.select_class_name == "static" or
			self.select_class_name == "self"):
			if self.select_sub_type == "function":
				move_flag = Text().move_point_function(self.view, [self.select_sub_name])
			elif self.select_sub_type == "variable":
				move_flag = Text().move_point_variable(self.view, [self.select_sub_name])
			if move_flag:
				return True
			if self.select_class_name == "static":
				return True # True because user miss type
		# this, self, parent
		# search parent class
		list = []
		(extend, interfaces) = Text().match_extend_implement(Text().view_content(self.view))
		if extend:
			list.append(extend)
		traits = Text().match_use_trait(Text().view_content(self.view))
		if traits:
			list += traits
		if len(list) == 0:
			return True
		thread = FindParentThread(self, self.select_sub_type, self.select_sub_name, list)
		thread.start()
		return True

	def find_parent_call_next(self, list = [], count = 0):
		thread = FindParentThread(self, self.select_sub_type, self.select_sub_name, list, count)
		thread.start()

	def find_parent_open_file(self, file_path):
		if self.select_sub_type == "function":
			self.path.set_open_file_callback(Text().move_point_function, self.select_sub_name)
		elif self.select_sub_type == "variable":
			self.path.set_open_file_callback(Text().move_point_variable, self.select_sub_name)
		self.path.switch_to_file(file_path, self.view)


class CakeFindCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return False
		if not self.is_file():
			sublime.status_message("Can't find file type.")
			return
		(self.select_word, self.select_css_tag_word, self.select_word_region,
			self.select_css_tag_region, self.select_line_str, self.select_class_name,
			self.select_sub_name, self.select_sub_type, self.enclosed_word) = Text().get_cursol_info(self.view)

		found = False
		if self.current_file_type == "controller":
			found = self.is_word_only_controller()
		elif self.current_file_type == "view":
			found = self.is_word_only_view()
		elif self.current_file_type == "helper":
			found = self.is_word_only_helper()
		elif self.current_file_type == "layout":
			found = self.is_word_only_layout()
		elif self.current_file_type == "css":
			found = self.is_word_only_css()
		if found:
			return
		if not self.is_word_any_file():
			sublime.status_message("Can't find file.")
			return

class CakeGrepCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		where = self.path.get_grep_where(self.view, self.user_settings)
		self.view.window().run_command("show_panel", {"panel": "find_in_files", "where": where})

class CakeSwitchToModelCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file() or self.singular_name is None:
			sublime.status_message("Can't switch to model.")
			return
		self.path.switch_to_category(self.view, 'model', self.singular_name)

class CakeSwitchToControllerCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file() or self.plural_name is None:
			sublime.status_message("Can't switch to contoroller.")
			return
		if self.action_name is not None:
			self.path.set_open_file_callback(Text().move_point_controller_action, self.action_name)
		self.path.switch_to_category(self.view, 'controller', self.plural_name)

class CakeSwitchToViewCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file() or self.action_name is None or self.plural_name is None:
			sublime.status_message("Can't switch to view.")
			return
		return self.path.switch_to_view(self.view, self.plural_name, self.action_name)

class CakeSwitchToTestCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file():
			sublime.status_message("Can't switch to test file.")
			return
		type = self.current_file_type
		if type != "plugin" and type != "core":
			type = "app"
		return self.path.switch_to_test(self.view, type)

class CakeShowDirectoryListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.get_this_dir(self.view), self.view)

class CakeShowControllerListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("controller", self.view)

class CakeShowModelListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("model", self.view)

class CakeShowViewListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("view", self.view)

class CakeShowComponentListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("component", self.view)

class CakeShowBehaviorListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("behavior", self.view)

class CakeShowHelperListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("helper", self.view)

class CakeShowLibListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("lib", self.view)

class CakeShowVendorListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("vendor", self.view)

class CakeShowLayoutListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("layout", self.view)

class CakeShowCssListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("css", self.view)

class CakeShowJavascriptListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("javascript", self.view)

class CakeShowElementListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("element", self.view)

class CakeShowConfigListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("config", self.view)

class CakeShowPluginListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("plugin", self.view)

class CakeShowTestListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("test", self.view)

class CakeShowFixtureListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list_by_folder("fixture", self.view)

class CakeOpenFolderCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.execute(self.path.get_this_dir(self.view))

