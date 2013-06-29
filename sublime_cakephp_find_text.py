# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import re
import time
if sublime.version().startswith('3'):
	from .sublime_cakephp_find_inflector import Inflector
elif sublime.version().startswith('2'):
	from sublime_cakephp_find_inflector import Inflector


class Sel:
	def __init__(self):
		self.type = None
		self.word = ""


class Text:
	def __init__(self):
		return

	def find_action_name_this_place(self, view):
		action_name = None
		select_region = view.sel()
		point = view.line(select_region[0]).end()
		before_content = view.substr(sublime.Region(0, point))
		matches = re.finditer("function ([a-zA-Z0-9_]+) *\(", before_content)
		for match in matches:
			action_name = match.group(1)
		if action_name is None:
			after_content = view.substr(sublime.Region(point, view.size()))
			match = re.search("function ([a-zA-Z0-9_]+) *\(", after_content)
			if not match is None:
				action_name = match.group(1)
		return action_name

	def view_content(self, view):
		return view.substr(sublime.Region(0, view.size()))

	def get_cursol_info(self, view):
		region = view.sel()[0]
		select_line_str = view.substr(view.line(region))
		select_region = view.word(region.begin())
		select_word = view.substr(select_region)
		select_css_tag_region = self.get_css_tag_word_region(view, select_region)
		select_css_tag_word = view.substr(select_css_tag_region)
		if re.search("(->|::)", select_word) is not None:
			# get left word
			select_region = view.word(sublime.Region(select_region.a - 1, select_region.a))
			select_word = view.substr(select_region)
		self.sel_list = []
		self.get_word_operator_info(view, select_region, 0, True)
		(select_class_name, select_sub_name, select_sub_type) = self.get_cursol_class_info()
		return select_word, select_css_tag_word, select_region, select_css_tag_region, select_line_str, select_class_name, select_sub_name, select_sub_type

	def get_word_operator_info(self, view, region, direction, select_word_flag = False):
		word = view.substr(region)
		if re.search("^[a-zA-Z0-9_]", word) is None:
			return

		sel = Sel()
		sel.word = word

		right_operator = view.substr(sublime.Region(region.end(), region.end() + 3))
		right_region = None
		if re.search("^[,;\.\[\)\]]", right_operator) is not None:
			right_type = "variable"
		elif re.search("^\(", right_operator) is not None:
			right_type = "function"
		elif re.search("^(->|::)\$", right_operator) is not None:
			right_type = "object"
			right_region = view.word(sublime.Region(region.end() + 3, region.end() + 4))
		elif re.search("^(->|::)", right_operator) is not None:
			right_type = "object"
			right_region = view.word(sublime.Region(region.end() + 2, region.end() + 3))
		elif re.search("^[\r\n{ \t'\"]", right_operator) is not None:
			right_type = "string"
		else:
			right_type = None

		left_operator = view.substr(sublime.Region(region.begin() -3, region.begin()))
		left_region = None
		if re.search("[,\.\r\n \t\(]$", left_operator) is not None:
			left_type = "class"
		elif re.search("::\$$", left_operator) is not None:
			left_type = "object"
			left_region = view.word(sublime.Region(region.begin() - 4, region.begin() - 3))
		elif re.search("\$$", left_operator) is not None:
			left_type = "variable"
		elif re.search("(->|::)$", left_operator) is not None:
			left_type = "object"
			left_region = view.word(sublime.Region(region.begin() - 3, region.begin() - 2))
		elif re.search("['\"]$", left_operator) is not None:
			left_type = "string"
		else:
			left_type = None

		# set type
		if word == "this" or word == "self":
			type = "this"
		elif right_type == "variable" or right_type == "function":
			type = right_type
		elif (left_type == "class" and
			(right_type == "object" or right_type == "class")):
			type = "class"
		elif left_type == "variable" and right_type == "object":
			type = "object"
			new_class_name = self.search_before_new_class(word, view.substr(sublime.Region(0, region.begin())))
			if new_class_name:
				sel.word = new_class_name
		elif right_type == "object":
			type = "object"
		elif (right_type == "string" and
			(left_type == "string" or left_type == "class")):
			type = "string"
		else:
			type = None

		# save
		sel.type = type
		if direction >= 0:
			self.sel_list.append(sel)
		elif direction < 0:
			self.sel_list = [sel] + self.sel_list

		# left direction once
		if (direction <= 0 and left_region is not None and
			left_type == "object" and
			(type == "variable" or type == "function")):
			self.get_word_operator_info(view, left_region, -1)
		# right direction repeat
		if (direction >= 0 and right_region is not None and
			(type == "this" or type == "class" or type == "object")):
			self.get_word_operator_info(view, right_region, 1)

	def search_before_new_class(self, variable_name, content):
		class_name = False
		matches = re.finditer("\$" + variable_name + "[ \t]+=[ \t]+new[ \t]+([a-zA-Z0-9_]+)[(;]", content)
		for match in matches:
			class_name = match.group(1)
		return class_name

	def get_cursol_class_info(self):
		select_class_name = None
		select_sub_name = None
		select_sub_type = None
		is_object_exists = False
		is_after_this = False
		for sel in self.sel_list:
			if sel.type == "this":
				is_after_this = True
				continue
			elif sel.type == "string":
				select_class_name = sel.word
				break
			elif sel.type == "class" or sel.type == "object":
				if is_object_exists:
					select_sub_name = sel.word
					select_sub_type = "variable"
					break
				else:
					is_object_exists = True
					select_class_name = sel.word
			elif sel.type == "variable" or sel.type == "function":
				if is_object_exists:
					select_sub_name = sel.word
					select_sub_type = sel.type
				elif is_after_this:
					select_class_name = "this"
					select_sub_name = sel.word
					select_sub_type = sel.type
				break
			elif sel.type is None:
				break
			is_after_this = False
		return select_class_name, select_sub_name, select_sub_type

	def get_css_tag_word_region(self, view, region):
		before_region = region
		# left
		while True:
			new_region = sublime.Region(before_region.a - 1, before_region.b)
			word = view.substr(new_region)
			match = re.search("^[^a-zA-Z0-9\_\-]", word)
			if match is not None:
				break
			before_region = new_region
		# right
		while True:
			new_region = sublime.Region(before_region.a, before_region.b + 1)
			word = view.substr(new_region)
			match = re.search("[^a-zA-Z0-9\_\-]$", word)
			if match is not None:
				break
			before_region = new_region
		return before_region

	def move_point_controller_action(self, view, arg):
		(action_name, ) = arg
		point = self.search_point_function(Inflector().variablize(action_name), view)
		if point == -1:
			point = self.search_point_function(action_name, view)
			if point == -1:
				return
		self.move_view_point(view, point)

	def move_point_function(self, view, arg):
		(function_name, ) = arg
		point = self.search_point_function(function_name, view)
		if point == -1:
			return
		self.move_view_point(view, point)

	def move_point_variable(self, view, arg):
		(variable_name, ) = arg
		point = self.search_point_variable(variable_name, view)
		if point == -1:
			return
		self.move_view_point(view, point)

	def move_line_number(self, view, arg):
		(line_number, ) = arg
		point = view.text_point(line_number, 0)
		self.move_view_point(view, point)

	def search_point_function(self, function_name, view):
		match = re.search("function " + function_name + " *\(", self.view_content(view))
		if match is None:
			return -1
		return match.start(0)

	def search_point_variable(self, variable_name, view):
		match = re.search("(public|protected|private|var|const)[ \t]+(static[ \t]+)*\$?" + variable_name, self.view_content(view))
		if match is None:
			return -1
		return match.start(0)

	def move_view_point(self, view, point):
		view.sel().clear()
		view.sel().add(sublime.Region(point, point))
		view.show(point)
		view.show_at_center(point)

	def match_render_function(self, line_content):
		# $this->render("view") or
		# $this->render("view", "layout") or
		# $this->render('/Elements/ajaxreturn');
		# $this->render("DebugKit.ToolbarAccess/history_state");
		match = re.search("render\(['\"]([a-zA-Z0-9_/\.]+)['\"](,[ \t]*['\"]([a-zA-Z0-9_]+)['\"])?", line_content)
		if match is None:
			return False, False, False, False
		layout_name = None
		if match.group(3) is not None:
			layout_name = match.group(3)
		split = match.group(1).split('.')
		if len(split) > 1:
			plugin_name = split[0]
			split = split[1].split('/')
			controller_name = split[0]
			view_name = '/'.join(split[1:])
		else:
			plugin_name = False
			view = split[-1]
			if view[0:1] == '/':
				view = view[1:]
				split = view.split('/')
				controller_name = split[0]
				view_name = '/'.join(split[1:])
			else:
				controller_name = False
				view_name = view
		return plugin_name, controller_name, view_name, layout_name

	def match_layout_variable(self, line_content):
		# public $layout = "default";
		# ->layout = "default";
		# ->layout = "TwitterBootstrap.default";
		match = re.search("(\$|\-\>)layout[ \t]*=[ \t]*(\"|\')([a-zA-Z0-9_\.]+)(\"|\')", line_content)
		if match is None:
			return None, None
		split = match.group(3).split('.')
		if len(split) > 1:
			plugin_name = split[0]
		else:
			plugin_name = None
		file_name = split[-1]
		print(plugin_name, file_name)
		return plugin_name, file_name

	def match_element_function(self, line_content):
		# renderElement("photo")
		# element("photo")
		# element("DebugKit.log_panel");
		match = re.search("(renderElement|element)\([\"\']([a-zA-Z0-9_/\.]+)[\"\']", line_content)
		if match is None:
			return None, None
		split = match.group(2).split('.')
		if len(split) > 1:
			plugin_name = split[0]
		else:
			plugin_name = None
		file_name = split[-1]
		return plugin_name, file_name

	def match_javascript_function(self, line_content):
		# $javascript->link("window");
		# Html->script("window");
		match = re.search("(\$javascript->link|Html->script)\([\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return match.group(2)

	def match_css_function(self, line_content):
		# $html->css("font")
		# $this->Html->css("font")
		match = re.search("(\$html->css|Html->css)\([\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return match.group(2)

	def match_tag_id_class(self, line_content):
		# <span class="notice success"></span>
		# <div id="footer"></div>
		id_list = []
		class_list = []
		match = re.search("class[ \t]*=[ \t]*[\"\']([a-zA-Z0-9_\- ]+)[\"\']", line_content)
		if match is not None:
			list = match.group(1).split(' ')
			for str in list:
				if str != '':
					class_list.append(str)
		match = re.search("id[ \t]*=[ \t]*[\"\']([a-zA-Z0-9_\- ]+)[\"\']", line_content)
		if match is not None:
			list = match.group(1).split(' ')
			for str in list:
				if str != '':
					id_list.append(str)
		return id_list, class_list

	def match_background_image(self, line_content):
		# background: url('../img/cake.icon.png') no-repeat left;
		match = re.search("url\(['\"]\.\./img/([a-zA-Z0-9_/\-\.]+)['\"]", line_content)
		if match is None:
			return None
		return self.match_image_extension(match.group(1))

	def match_html_image(self, line_content):
		# $html->image("cake.icon.png");
		# $this->Html->image("ss/cake.icon.png");
		match = re.search("(\$html->image|Html->image)\([\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return self.match_image_extension(match.group(2))

	def match_image_extension(self, file_path):
		if re.search("\.(jpeg|jpe|jpg|gif|png|bmp|dib|tif|tiff|ico)$", file_path) is not None:
			return file_path
		return None

	def match_new_class(self, line_content):
		# $my_class = new TestClass();
		match = re.search("new ([a-zA-Z0-9_]+)[(;]", line_content)
		if match is None:
			return False
		return match.group(1)

	def match_app_import(self, line_content):
		# App::import('Model', 'DebugKit.ToolbarAccess');
		match = re.search("import\(['\"]([a-zA-Z0-9_]+)['\"],[ \t]*(array\()?['\"]([a-zA-Z0-9_/\.]+)['\"]", line_content)
		if match is None:
			return False, False, False
		folder_name = match.group(1)
		split = match.group(3).split('.')
		if len(split) > 1:
			plugin_name = split[0]
		else:
			plugin_name = None
		file_name = split[-1]
		return plugin_name, folder_name, file_name

	def match_app_uses(self, line_content):
		# App::uses('TimedBehavior', 'DebugKit.Model/Behavior');
		match = re.search("App::uses\(['\"]([a-zA-Z0-9]+)['\"],[ \t]*['\"]([a-zA-Z0-9/\.]+)['\"]", line_content)
		if match is None:
			return False, False, False
		file_name = match.group(1)
		split = match.group(2).split('.')
		if len(split) > 1:
			plugin_name = split[0]
		else:
			plugin_name = None
		folder_split = split[-1].split('/')
		folder_name = folder_split[-1]
		return plugin_name, folder_name, file_name

	def match_redirect_function(self, line_content):
		# $this->redirect('/orders/thanks'));
		# $this->redirect(array('controller' => 'orders', 'action' => 'thanks'));
		match = re.search("redirect\((.*?)\);$", line_content)
		if match is None:
			return None, None
		controller_name = None
		action_name = None
		content = match.group(1)
		match = re.search("(array\(|\[)", content)
		if match is not None:
			match = re.search("controller['\"][ \t]+=>[ \t]+['\"]([a-zA-Z0-9_]+)['\"]", content)
			if match is not None:
				controller_name = match.group(1)
			match = re.search("action['\"][ \t]+=>[ \t]+['\"]([a-zA-Z0-9_]+)['\"]", content)
			if match is not None:
				action_name = match.group(1)
		else:
			match = re.search("['\"]([a-zA-Z0-9_/]+)['\"]", content)
			if match is not None:
				list = match.group(1).split('/')
				if (len(list) > 2):
					controller_name = list[1]
					action_name = list[2]
		return controller_name, action_name



