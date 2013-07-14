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


class SublimeCakephpFind(sublime_plugin.TextCommand):
	def set_app_path(self):
		self.path = Path()
		self.current_file_type = None
		self.action_name = None
		self.lower_camelized_action_name = None
		self.select_word = None
		self.select_class_name = None
		self.select_sub_name = None
		self.select_sub_type = None
		self.user_settings = self.view.settings().get('sublime_cakephp_find')
		#if self.user_settings is not None:
		if not self.path.set_app(self.view):
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
			self.is_enclosed_word() or
			self.is_local_function() or
			self.is_email_template() or
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
		if not self.new_class_name:
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
			return False
		where = self.path.get_grep_where(self.view, self.user_settings)
		self.view.window().run_command("show_panel", {"panel": "find_in_files", "where": where})

class CakeSwitchToModelCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file():
			sublime.status_message("Can't switch to model.")
			return
		self.path.switch_to_category(self.view, 'model', self.singular_name)

class CakeSwitchToControllerCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file():
			sublime.status_message("Can't switch to contoroller.")
			return
		if self.action_name is not None:
			self.path.set_open_file_callback(Text().move_point_controller_action, self.action_name)
		self.path.switch_to_category(self.view, 'controller', self.plural_name)

class CakeSwitchToViewCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path():
			return
		if not self.is_file() or self.action_name is None:
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
		self.path.show_dir_list(self.path.folder_path["controller"], self.view)

class CakeShowModelListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["model"], self.view)

class CakeShowViewListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["view"], self.view)

class CakeShowComponentListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["component"], self.view)

class CakeShowBehaviorListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["behavior"], self.view)

class CakeShowHelperListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["helper"], self.view)

class CakeShowLibListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["lib"], self.view)

class CakeShowVendorListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["vendor"], self.view)

class CakeShowLayoutListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["layout"], self.view)

class CakeShowCssListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["css"], self.view)

class CakeShowJavascriptListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["javascript"], self.view)

class CakeShowElementListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["element"], self.view)

class CakeShowConfigListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["config"], self.view)

class CakeShowPluginListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["plugin"], self.view)

class CakeShowTestListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["test"], self.view)

class CakeShowFixtureListCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.show_dir_list(self.path.folder_path["fixture"], self.view)

class CakeOpenFolderCommand(SublimeCakephpFind):
	def run(self, edit):
		if not self.set_app_path(): return
		self.path.execute(self.path.get_this_dir(self.view))

