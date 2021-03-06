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
		matches = re.finditer("function[ \t]+([a-zA-Z0-9_]+)[ \t]*\(", before_content)
		for match in matches:
			action_name = match.group(1)
		if action_name is None:
			after_content = view.substr(sublime.Region(point, view.size()))
			match = re.search("function[ \t]+([a-zA-Z0-9_]+)[ \t]*\(", after_content)
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
		enclosed_word = self.get_enclosed_word(view, region)
		if re.search("(->|::)", select_word) is not None:
			# get left word
			select_region = view.word(sublime.Region(select_region.a - 1, select_region.a))
			select_word = view.substr(select_region)
		self.sel_list = []
		self.get_word_operator_info(view, select_region, 0, True)
		(select_class_name, select_sub_name, select_sub_type) = self.get_cursol_class_info()
		return (select_word, select_css_tag_word, select_region,
			select_css_tag_region, select_line_str, select_class_name,
			select_sub_name, select_sub_type, enclosed_word)

	def get_word_operator_info(self, view, region, direction, select_word_flag = False):
		word = view.substr(region)
		if re.search("^[a-zA-Z0-9_]", word) is None:
			return

		last_point = view.size()
		sel = Sel()
		sel.word = word

		right_region = None
		if region.end() > last_point - 4:
			right_type = None
		else:
			right_operator = view.substr(sublime.Region(region.end(), region.end() + 3))
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
			elif re.search("^[\r\n{ \t]", right_operator) is not None:
				right_type = "string"
			else:
				right_type = None

		left_region = None
		if region.begin() < 4:
			left_type = None
		else:
			left_operator = view.substr(sublime.Region(region.begin() -3, region.begin()))
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
			else:
				left_type = None

		# set type
		if word == "this" or word == "self" or word == "static" or word == "parent":
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
		elif left_type == "object" and right_type == "string":
			type = "variable"
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
		matches = re.finditer("\$" + variable_name + "[ \t]*=[ \t]*new[ \t]+([a-zA-Z0-9_]+)[(;]", content)
		for match in matches:
			class_name = match.group(1)
		return class_name

	def get_cursol_class_info(self):
		select_class_name = None
		select_sub_name = None
		select_sub_type = None
		is_object_exists = False
		is_after_this = False
		this_type = False
		for sel in self.sel_list:
			if sel.type == "this":
				is_after_this = True
				this_type = sel.word
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
					select_class_name = this_type # "this" or "static" or "self"
					select_sub_name = sel.word
					select_sub_type = sel.type
				break
			elif sel.type is None:
				break
			is_after_this = False
		return select_class_name, select_sub_name, select_sub_type

	def get_css_tag_word_region(self, view, region):
		before_region = region
		last_point = view.size()
		# left
		while True:
			if before_region.a < 1:
				break
			new_region = sublime.Region(before_region.a - 1, before_region.b)
			word = view.substr(new_region)
			match = re.search("^[^a-zA-Z0-9\_\-]", word)
			if match is not None:
				break
			before_region = new_region
		# right
		while True:
			if before_region.b > last_point - 1:
				break
			new_region = sublime.Region(before_region.a, before_region.b + 1)
			word = view.substr(new_region)
			match = re.search("[^a-zA-Z0-9\_\-]$", word)
			if match is not None:
				break
			before_region = new_region
		return before_region

	def get_enclosed_word(self, view, region):
		before_region = sublime.Region(region.a, region.a)
		before_word = after_word = ''
		last_point = view.size()
		# left
		while True:
			if before_region.a < 1:
				break
			new_region = sublime.Region(before_region.a - 1, before_region.b)
			word = view.substr(new_region)
			match = re.search("^[^a-zA-Z0-9\_\.]", word)
			if match is not None:
				before_word = word[0:1]
				break
			before_region = new_region
		# right
		while True:
			if before_region.b > last_point - 1:
				break
			new_region = sublime.Region(before_region.a, before_region.b + 1)
			word = view.substr(new_region)
			match = re.search("[^a-zA-Z0-9\_\.]$", word)
			if match is not None:
				after_word = word[-1]
				break
			before_region = new_region

		if (before_word == after_word and
			(before_word == '"' or
			 before_word == "'")):
			return view.substr(before_region)
		return False

	def move_point_controller_action(self, view, arg):
		(action_name, ) = arg
		point = self.search_point_function(Inflector().variablize(action_name), self.view_content(view))
		if point == -1:
			point = self.search_point_function(action_name, self.view_content(view))
			if point == -1:
				return
		self.move_view_point(view, point)

	def move_point_function(self, view, arg):
		(function_name, ) = arg
		point = self.search_point_function(function_name, self.view_content(view))
		if point == -1:
			return False
		self.move_view_point(view, point)
		return True

	def move_point_variable(self, view, arg):
		(variable_name, ) = arg
		point = self.search_point_variable(variable_name, self.view_content(view))
		if point == -1:
			return False
		self.move_view_point(view, point)
		return True

	def move_point_msgid(self, view, arg):
		(msg_id, ) = arg
		point = self.search_point_msgid(msg_id, self.view_content(view))
		if point == -1:
			return
		self.move_view_point(view, point)

	def move_line_number(self, view, arg):
		(line_number, ) = arg
		point = view.text_point(line_number, 0)
		self.move_view_point(view, point)

	def search_point_function(self, function_name, text):
		match = re.search("function[ \t]+\&?" + function_name + "[ \t]*\(", text)
		if match is None:
			return -1
		return match.start(0)

	def search_point_variable(self, variable_name, text):
		match = re.search("(public|protected|private|var|const)[ \t]+(static[ \t]+)*\$?" + variable_name, text)
		if match is None:
			return -1
		return match.start(0)

	def search_point_class_head(self, text):
		match = re.search("(class|interface|trait)[ \t]+[a-zA-Z0-9]+[ \t\r\n]+", text)
		if match is None:
			return -1
		return match.start(0)

	def search_point_msgid(self, msg_id, text):
		match = re.search("msgid[ \t]+\"" + msg_id + "\"", text)
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
		# $this->render("/common/feed.atom");
		match = re.search("render\([ \t]*['\"]([a-zA-Z0-9_/\.]+)['\"](,[ \t]*['\"]([a-zA-Z0-9_]+)['\"])?", line_content)
		if match is None:
			return False, False, False, False
		layout_name = None
		if match.group(3) is not None:
			layout_name = match.group(3)
		split = match.group(1).split('.')
		if len(split) > 1 and re.search("/", split[0]) is None:
			plugin_name = split[0]
			split = split[1].split('/')
			controller_name = split[0]
			view_name = '/'.join(split[1:])
		else:
			plugin_name = False
			view = match.group(1)
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
		return plugin_name, file_name

	def match_element_function(self, line_content):
		# renderElement("photo")
		# element("photo")
		# element("DebugKit.log_panel");
		match = re.search("(renderElement|element)\([ \t]*[\"\']([a-zA-Z0-9_/\.]+)[\"\']", line_content)
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
		match = re.search("(\$javascript->link|Html->script)\([ \t]*[\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return match.group(2)

	def match_css_function(self, line_content):
		# $html->css("font")
		# $this->Html->css("font")
		match = re.search("(\$html->css|Html->css)\([ \t]*[\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
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
		match = re.search("(\$html->image|Html->image)\([ \t]*[\"\']([a-zA-Z0-9_/\-\.]+)[\"\']", line_content)
		if match is None:
			return None
		return self.match_image_extension(match.group(2))

	def match_image_extension(self, file_path):
		if re.search("\.(jpeg|jpe|jpg|gif|png|bmp|dib|tif|tiff|ico)$", file_path) is not None:
			return file_path
		return None

	def match_new_class(self, line_content):
		# $my_class = new TestClass();
		# new Error\Exception(
		match = re.search("new[ \t]+([a-zA-Z0-9_\\\\]+)[(;]", line_content)
		if match is None:
			return False
		class_name = match.group(1).split("\\")[-1]
		return class_name

	def match_app_import(self, line_content):
		# App::import('Model', 'DebugKit.ToolbarAccess');
		# App::import('Vendor', 'georgious-cakephp-yaml-migrations-and-fixtures/spyc/spyc');
		# App::import('Vendor', 'PclZip', array('file' => 'pclzip-2-8-2/pclzip.lib.php'));
		match = re.search("import\([ \t]*['\"]([a-zA-Z0-9_]+)['\"],[ \t]*['\"]([a-zA-Z0-9_/\-\.]+)['\"](,[ \t]*array\((.*?))?\)", line_content)
		if match is None:
			return False, False, False
		folder_name = match.group(1)
		split = match.group(2).split('.')
		if len(split) > 1:
			plugin_name = split[0]
		else:
			plugin_name = False
		file_name = split[-1]
		# check option file
		if match.group(4) is not None:
			file_match = re.search("['\"]file['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_/\-\.]+)\.php['\"]", match.group(4))
			if file_match is not None:
				file_name = file_match.group(1)
		return plugin_name, folder_name, file_name

	def match_app_uses(self, line_content):
		# App::uses('TimedBehavior', 'DebugKit.Model/Behavior');
		match = re.search("App::uses\([ \t]*['\"]([a-zA-Z0-9]+)['\"],[ \t]*['\"]([a-zA-Z0-9/\.]+)['\"]", line_content)
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
		# $this->redirect(array('action' => 'thanks'));
		match = re.search("redirect\((.*?)\)", line_content)
		if match is None:
			return None, None
		controller_name = None
		action_name = None
		content = match.group(1)
		match = re.search("(array\(|\[)", content)
		if match is not None:
			match = re.search("controller['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_]+)['\"]", content)
			if match is not None:
				controller_name = match.group(1)
			match = re.search("action['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_]+)['\"]", content)
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

	def match_local_function(self, line_content):
		# __("Hello!");
		# __c("Hello!");
		match = re.search("__[c]?\([ \t]*['\"](.*?)['\"][,\)]", line_content)
		if match is not None:
			return False, match.group(1)
		# __d("domain", "Hello!");
		# __dc("domain", "Hello!");
		match = re.search("__d[c]?\([ \t]*['\"](.*?)['\"],[ \t]*['\"](.*?)['\"][,\)]", line_content)
		if match is not None:
			return match.group(1), match.group(2)
		return False, False

	def match_email_template(self, line_content):
		# ->template('default');
		# ->template('default', 'default');
		# ->template(false, 'default');
		# ->template('DebugKit.default', 'DebugKit.default');
		match = re.search("->template\([ \t]*(false|['\"]([a-zA-Z0-9_\.]+)['\"])(,[ \t]*['\"]([a-zA-Z0-9_\.]+)['\"])?", line_content)
		if match is None:
			return False, False
		template_name = match.group(2)
		if template_name is None:
			template_name = False
		if match.group(4) is None:
			return template_name, False
		return template_name, match.group(4)

	def match_fixture(self, text):
		# 'app.fixt'
		# 'plugin.debug_kit.attachment'
		# 'core.comment'
		match = re.search("^[a-z0-9\._]+$", text)
		if match is None:
			return False
		return True

	def match_route(self, text):
		# array('controller' => 'pages')
		# array('controller' => 'pages', 'action' => 'display')
		# array('controller' => 'pages', 'action' => 'display', 'home')
		# array('plugin' => 'debug_kit', 'controller' => 'toolbar_access', 'action' => 'history_state')
		plugin_name = False
		controller_name = False
		action_name = False
		match = re.search("['\"]controller['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_]+)['\"]", text)
		if match is not None:
			controller_name = match.group(1)
		match = re.search("['\"]action['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_]+)['\"]", text)
		if match is not None:
			action_name = match.group(1)
		match = re.search("['\"]plugin['\"][ \t]*=>[ \t]*['\"]([a-zA-Z0-9_]+)['\"]", text)
		if match is not None:
			plugin_name = match.group(1)
		return plugin_name, controller_name, action_name

	def match_datasource(self, text):
		# 'datasource' => 'Database/Mysql',
		# $default['datasource'] = 'Database/Mysql';
		plugin_name = False
		path = False
		match = re.search("['\"]datasource['\"]\]?[ \t]*=>?[ \t]*['\"]([a-zA-Z0-9_/\.]+)['\"]", text)
		if match is not None:
			split = match.group(1).split('.')
			path = split[-1]
			if len(split) > 1:
				plugin_name = split[0]
		return plugin_name, path
	
	def match_include_require(self, text):
		# 	if (!include ('Cake' . DS . 'bootstrap.php')) {
		#   if (!include APP . 'Config' . DS . 'core.php') {
		# 	include_once APP . 'Config' . DS . 'database.php';
		# 	include APP . 'Config' . DS . 'routes.php';
		#   require CAKE . 'Error' . DS . 'exceptions.php';
		#   require_once dirname(dirname(dirname(dirname(__FILE__)))) . DS . 'Model' . DS . 'models.php';
		# 	require_once CORE_TEST_CASES . DS . 'Log' . DS . 'Engine' . DS . 'ConsoleLogTest.php';
		#   require_once (APP . 'Config' . DS . 'database.php');
		words = []
		match = re.search("(include|include_once|require|require_once)[ \t]+(.*)", text)
		if match is None:
			return 0, False
		line = base_line = match.group(2)
		parenthesis_count = 0
		up_dir_count = 0;
		words = []
		while (len(line) > 0):
			if re.search("^([ \t\.]+)", line):
				line = re.sub("^([ \t\.]+)", "", line)
				continue
			elif re.search("^\(", line):
				line = re.sub("^\(", "", line)
				parenthesis_count += 1
				continue
			elif re.search("^\)", line):
				line = re.sub("^\)", "", line)
				parenthesis_count -= 1
				if parenthesis_count <= 0 and len(words) != 0:
					break
				continue
			elif re.search("^;", line):
				break
			elif re.search("^dirname\(dirname\(dirname\(dirname\(", line) and len(words) == 0:
				line = re.sub("^dirname\(dirname\(dirname\(dirname\(", "", line)
				up_dir_count += 4;
				continue
			elif re.search("^dirname\(dirname\(dirname\(", line) and len(words) == 0:
				line = re.sub("^dirname\(dirname\(dirname\(", "", line)
				up_dir_count += 3;
				continue
			elif re.search("^dirname\(dirname\(", line) and len(words) == 0:
				line = re.sub("^dirname\(dirname\(", "", line)
				up_dir_count += 2;
				continue
			elif re.search("^dirname\(", line) and len(words) == 0:
				line = re.sub("^dirname\(", "", line)
				up_dir_count += 1;
				continue
			elif re.search("^__DIR__", line) and len(words) == 0:
				line = re.sub("^__DIR__", "", line)
				up_dir_count += 1;
				continue
			elif re.search("^__FILE__", line) and len(words) == 0:
				line = re.sub("^__FILE__", "", line)
				continue
			elif re.search("^(['\"]([a-zA-Z0-9/_\.]+)['\"])", line):
				match = re.search("^(['\"]([a-zA-Z0-9/_\.]+)['\"])", line)
				line = re.sub("^" + match.group(1), "", line)
				words.append(match.group(2))
				continue
			# example: APP, CAKE_CORE_INCLUDE_PATH
			elif re.search("^([A-Z/_]+)", line):
				match = re.search("^([A-Z/_]+)", line)
				line = re.sub("^" + match.group(1), "", line)
				words.append(match.group(1))
				continue
			return 0, False
		return up_dir_count, words

	def match_namespace_use(self, text):
		# use Cake\Network\Email\Email;
		# use App\Model\Test01;
		# use Cake\Database\Query as DatabaseQuery;
		match = re.search("[ \t]*use[ \t]+([a-zA-Z0-9_\\\\]+)([ \t]+as[ \t]+([a-zA-Z0-9_]+))?;", text)
		if match is None:
			return False
		path = match.group(1)
		as_name = match.group(3)
		class_name = path.split("\\")[-1]
		return class_name
	
	def match_extend_implement(self, text):
		# class AppController extends Controller {
		# class SessionHandler implements SessionHandlerInterface {
		# class Exception extends \Cake\Error\Exception {
		# class CustomTestEventListerner extends EventTestListener implements EventListener {
		# class CustomTestEventListerner extends EventManagerTest implements EventListener {
		# class StatementDecorator implements
		#     StatementInterface,
		#     \Countable,
		#     \IteratorAggregate
		# {
		extend = implements = False
		match = re.search("(class|interface|trait)[ \t\r\n]+[a-zA-Z0-9]+([ \t\r\n]+extends[ \t\r\n]+([a-zA-Z0-9\\\\]+))?([ \t\r\n]+implements[ \t\r\n]+([a-zA-Z0-9, \t\r\n\\\\]+)[ \t\r\n]*)?[ \t\r\n]*{", text)
		if match is None:
			match = re.search("(class|interface|trait)[ \t]+[a-zA-Z0-9]+([ \t]+extends[ \t]+([a-zA-Z0-9\\\\]+))?([ \t]+implements[ \t]+([a-zA-Z0-9, \t\\\\]+)[ \t]*)?([ \t]*{)?", text)
			if match is None:
				return False, False
		type = match.group(1) # class, interface, trait
		if match.group(3) is not None:
			extend = match.group(3).split("\\")[-1]
		if match.group(5) is not None:
			implement_befores = re.sub("[ \t]+", "", match.group(5)).split(",")
			implements = []
			for class_name in implement_befores:
				implements.append(class_name.split("\\")[-1])
		return extend, implements

	def match_use_trait(self, text):
		# class Object {
		#     use LogTrait, ViewVarsTrait;
		#     use LogTrait;
		#     use LogTrait
		#     {
		#     }
		point = self.search_point_class_head(text)
		if point == -1:
			return False
		content = text[point:]
		matches = re.finditer("[; \t\r\n]+use[ \t]+([a-zA-Z0-9_, \t\r\n]+)[;{]", content)
		traits = []
		for match in matches:
			find_traits = re.sub("[ \t\r\n]+", "", match.group(1)).split(",")
			traits += find_traits
		if len(traits) == 0:
			return False
		return traits

	def match_configure_read(self, text):
		# Configure::read('system');
		# Configure::read('db.default');
		match = re.search("Configure::read\([ \t]*['\"]([a-zA-Z0-9_\.]+)['\"]\)", text)
		if match is None:
			return False
		return match.group(1)

	def match_configure_load(self, text):
		# Configure::load('settings');
		# Configure::load('MyPlugin.settings');
		match = re.search("Configure::load\([ \t]*['\"]([a-zA-Z0-9_\-\.]+)['\"]\)", text)
		if match is None:
			return False, False, False
		split = match.group(1).split(".")
		if len(split) > 2:
			return False, False, False
		elif len(split) == 2:
			plugin_name = split[0]
			setting_name = split[1]
			return match.group(1), plugin_name, setting_name
		else:
			setting_name = split[0]
			return match.group(1), False, setting_name

	def match_configure_load_variables(self, text):
		# $config["mail"]['from'] = 'test@test.com';
		# $config["test3"] = array(
		# 	'test4' => [
		# 		'db' => [
		# 			'default' => '',
		# 		]],
		# 	'test5' => [
		# 		'cc' => 'test@test.com'
		# 	]
		# );
		text = text.replace("\r\n", "\n")
		text = text.replace("\r", "\n")
		split_text = text.split("\n")
		list = []
		count_line = -1
		array_base_variable = ''
		for line in split_text:
			count_line += 1
			# add value
			# $config["mail"]['from'] = 'test@test.com';
			match = re.search("config([a-zA-Z0-9_\[\]'\"]+)[ \t]*=[ \t]*['\"]", line)
			if match is not None:
				split = re.sub("[\['\"]", "", match.group(1)).split("]")
				if split[-1] == '':
					split.pop()
				list.append([".".join(split), count_line])
				continue
			#     'cc' => 'test@test.com'
			match = re.search("['\"]([a-zA-Z0-9_]+)['\"][ \t]*=>[ \t]*['\"]", line)
			if match is not None:
				if array_base_variable == '':
					append_word = match.group(1)
				else:
					append_word = array_base_variable + "." + match.group(1)
				list.append([append_word, count_line])
				continue
			# set base array
			# $config["test3"] = array(
			match = re.search("config([a-zA-Z0-9_\[\]'\"]+)?[ \t]*=[ \t]*(array\(|\[)", line)
			if match is not None:
				if match.group(1) is not None:
					split = re.sub("[\['\"]", "", match.group(1)).split("]")
					if split[-1] == '':
						split.pop()
					array_base_variable = ".".join(split)
				continue
			# add array
			# 	'test5' => [
			match = re.search("['\"]([a-zA-Z0-9_]+)['\"][ \t]*=>[ \t]*(array\(|\[)", line)
			if match is not None:
				if array_base_variable == '':
					array_base_variable = match.group(1)
				else:
					array_base_variable += "." + match.group(1)
				continue
			# pop array
			# 		]],
			# );
			match = re.search("[ \t]*([\)\],]+)(;?)[ \t]*", line)
			if match is not None:
				# end array
				# );
				if match.group(2):
					array_base_variable = ''
					continue
				split = array_base_variable.split(".")
				if len(split) <= 1:
					array_base_variable = ''
				else:
					count = match.group(1).count("]") + match.group(1).count(")")
					for var in range(count):
						if len(split) > 0:
							split.pop()
					array_base_variable = '.'.join(split)
				continue
		return list

	def match_view_blocks(self, text):
		# $this->assign("test", "assign");
		# $this->start("test");
		# $this->prepend("test", "prepend");
		# $this->append("test", "append");
		match = re.search("this->(assign|start|prepend|append)\([ \t]*['\"]([a-zA-Z0-9_\-]+)['\"]", text)
		if match is None:
			return False
		return match.group(2)

	def match_view_fetch(self, text):
		# $this->fetch('content');
		match = re.search("this->fetch\([ \t]*['\"]([a-zA-Z0-9_\-]+)['\"]", text)
		if match is None:
			return False
		return match.group(1)

	def match_model_actsas(self, text):
		text = text.replace("\r\n", "\n")
		text = text.replace("\r", "\n")
		split_text = text.split("\n")
		count_line = -1
		comment_flag = False
		found_flag = False
		found_text = ''
		for read_line in split_text:
			count_line += 1
			line = False
			if comment_flag:
				match = re.search("\*/", read_line)
				if match is None:
					cut_line = ''
				else:
					cut_line = read_line[match.end():]
					comment_flag = False
			else:
				match = re.search("/\*", read_line)
				if match is None:
					cut_line = read_line
				else:
					cut_line = read_line[:match.start()]
					comment_flag = True
			match = re.search("(//|#)", cut_line)
			if match is not None:
				cut_line = cut_line[:match.start()]
			if len(cut_line) == 0:
				continue
			# set base array
			if found_flag:
				match = re.search("(.*)(\)|\])[ \t]*;", cut_line)
				if match is not None:
					line = match.group(1)
					found_text += line
					break
				else:
					line = cut_line
			else:
				# public $actsAs = array(
				match = re.search("(var|public)[ \t]+\$actsAs[ \t]*=[ \t]*(array\(|\[)(.*)", cut_line)
				if match is not None:
					found_flag = True
					line = match.group(3)
			if not line:
				continue
			found_text += line
			# line over
			match = re.search("(private|public|protected)[ \t]+function[ \t]", cut_line)
			if match is not None:
				break
		# stop roop bug
		roop_count = 0
		parenthesis = 0
		arrow_flag = False
		get_word_flag = False
		get_word_start_char = ''
		get_word = ''
		list = []
		while len(found_text) > 0 and roop_count < 500:
			# get class word
			if parenthesis == 0 and arrow_flag == False:
				match = re.match("^(['\"]([a-zA-Z0-9.]+)['\"])", found_text)
				if match is not None:
					found_text = found_text[len(match.group(1)):]
					list.append(match.group(2))
					continue
			# word
			if get_word_flag:
				match = re.match("^(\\\\" + get_word_start_char + ")", found_text)
				if match is not None:
					found_text = found_text[len(match.group(1)):]
					continue
				else:
					match = re.match("^(\\" + get_word_start_char + ")", found_text)
					if match is not None:
						get_word = ''
						get_word_flag = not get_word_flag
						found_text = found_text[len(match.group(1)):]
						continue
					# get len(1)
					get_word += found_text[:1]
					found_text = found_text[1:]
				continue
			else:
				match = re.match("^(['\"])", found_text)
				if match is not None:
					get_word_flag = not get_word_flag
					get_word_start_char = match.group(1)
					found_text = found_text[len(match.group(1)):]
					continue
			# remove space
			match = re.match("^([ \t]+)", found_text)
			if match is not None:
				found_text = found_text[len(match.group(1)):]
				continue
			# check arrow
			match = re.match("^(=>)", found_text)
			if match is not None:
				found_text = found_text[len(match.group(1)):]
				arrow_flag = True
				continue
			# check comma
			match = re.match("^(,)", found_text)
			if match is not None:
				found_text = found_text[len(match.group(1)):]
				if parenthesis == 0:
					arrow_flag = False
				continue
			# check parenthesis add
			match = re.match("^(array\(|\[)", found_text)
			if match is not None:
				found_text = found_text[len(match.group(1)):]
				parenthesis += 1
				continue
			# check parenthesis delete
			match = re.match("^(\)|\])", found_text)
			if match is not None:
				found_text = found_text[len(match.group(1)):]
				parenthesis -= 1
				# error
				if parenthesis < 0:
					break
				continue
			# get len(1)
			found_text = found_text[1:]
			roop_count += 1
		if len(list) == 0:
			return False
		return list

