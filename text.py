# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import re
import time
from sel import Sel
from inflector import Inflector

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
		if re.search("(->|::)", select_word) is not None:
			# get left word
			select_region = view.word(sublime.Region(select_region.a - 1, select_region.a))
			select_word = view.substr(select_region)
		self.sel_list = []
		self.get_word_operator_info(view, select_region, 0, True)
		(select_class_name, select_sub_name, select_sub_type) = self.get_cursol_class_info()
		return select_word, select_line_str, select_class_name, select_sub_name, select_sub_type

	def get_word_operator_info(self, view, region, direction, select_word_flag = False):
		word = view.substr(region)
		if re.search("^[a-zA-Z0-9_]", word) is None:
			return

		sel = Sel()
		sel.word = word
		right_operator = view.substr(sublime.Region(region.end(), region.end() + 3))
		if re.search("^[,;\[]", right_operator) is not None:
			right_type = "variable"
		elif re.search("^\(", right_operator) is not None:
			right_type = "function"
		elif re.search("^(->|::)\$", right_operator) is not None:
			right_type = "object"
			right_region = view.word(sublime.Region(region.end() + 3, region.end() + 4))
		elif re.search("^(->|::)", right_operator) is not None:
			right_type = "object"
			right_region = view.word(sublime.Region(region.end() + 2, region.end() + 3))
		else:
			right_type = None
		left_operator = view.substr(sublime.Region(region.begin() -3, region.begin()))
		if re.search("[, \t\(]$", left_operator) is not None:
			left_type = "class"
		elif re.search("::\$$", left_operator) is not None:
			left_type = "object"
			left_region = view.word(sublime.Region(region.begin() - 4, region.begin() - 3))
		elif re.search("\$$", left_operator) is not None:
			left_type = "variable"
		elif re.search("(->|::)$", left_operator) is not None:
			left_type = "object"
			left_region = view.word(sublime.Region(region.begin() - 3, region.begin() - 2))
		else:
			left_type = None

		# set type
		if word == "this" or word == "self":
			type = "this"
		elif right_type == "variable" or right_type == "function":
			type = right_type
		elif left_type == "class" and right_type == "object":
			type = "class"
		elif left_type == "variable" and right_type == "object":
			type = "object"
			new_class_name = self.search_before_new_class(word, view.substr(sublime.Region(0, region.begin())))
			if new_class_name:
				sel.word = new_class_name
		elif right_type == "object":
			type = "object"
		else:
			type = None

		# save
		sel.type = type
		if direction >= 0:
			self.sel_list.append(sel)
		elif direction < 0:
			self.sel_list = [sel] + self.sel_list

		# left direction once
		if (direction <= 0 and
			left_type == "object" and
			(type == "variable" or type == "function")):
			self.get_word_operator_info(view, left_region, -1)
		# right direction repeat
		if (direction >= 0 and
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
		# $this->render("view", "layout")
		match = re.search("render\((\"|\')([a-zA-Z0-9_]+)(\"|\')(,[ \t]*(\"|\')([a-zA-Z0-9_]+)(\"|\'))?", line_content)
		if match is None:
			return None, None
		if match.group(6) is None:
			return match.group(2), None
		return match.group(2), match.group(6)

	def match_layout_variable(self, line_content):
		# public $layout = "default";
		# ->layout = "default";
		match = re.search("(\$|\-\>)layout[ \t]*=[ \t]*(\"|\')([a-zA-Z0-9\-_]+)(\"|\')", line_content)
		if match is None:
			return None
		return match.group(3)

	def is_loaded_class(self, word, line_content):
		# public $components = array('Post');
		matches = re.finditer("(\"|\')([a-zA-Z0-9_]+)(\"|\')", line_content)
		for match in matches:
			if match.group(2) == word:
				return True
		return False

	def is_arrow_class(self, word, line_content):
		# ->Post->set();
		matches = re.finditer("\-\>([a-zA-Z0-9_]+)[\- \t\;\(]+", line_content)
		for match in matches:
			if match.group(1) == word:
				return True
		return False

	def match_element_function(self, line_content):
		# renderElement("photo")
		# element("photo")
		match = re.search("(renderElement|element)\([\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return match.group(2)

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
		match = re.search("[$>:]([a-zA-Z0-9_]+)[ \t]+=[ \t]+new ([a-zA-Z0-9_]+)[(;]", line_content)
		if match is None:
			return False, False
		return match.group(2), match.group(1)



