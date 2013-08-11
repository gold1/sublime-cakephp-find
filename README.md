sublime-cakephp-find
==================
You can find out file and open easily.

## Requirements
- Sublime Text 2.x
- CakePHP ver.1.3.x or ver.2.x or 3.0-dev(Update: 2013/08/10)

## Installation
#### OSX

    $ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    $ git clone git://github.com/gold1/sublime-cakephp-find.git

#### Linux (Ubuntu like distros)

    $ cd ~/.config/sublime-text-2/Packages/
    $ git clone git://github.com/gold1/sublime-cakephp-find.git

#### Windows 7:

    Copy the directory to: "C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages"

#### Windows XP:

    Copy the directory to: "C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages"

## Switch Command
It changes to a corresponding file. 

| Command | File | Function |
| --- | --- | --- |
| `ctrl + shift + c`, `c` | controller | cake_switch_to_controller |
| `ctrl + shift + c`, `v` | view | cake_switch_to_view |
| `ctrl + shift + c`, `m` | model | cake_switch_to_model |
| `ctrl + shift + c`, `t` | test | cake_switch_to_test |

#### Example
```php
<?php
//app/Controller/SamplesController.php
class SamplesController extends Controller {

                       // - 
    function index() { // | 
                       // | : command(V) -> app/View/Samples/index.ctp
                       // | 
    }                  // | 
                       // - 

    // : command(M) -> app/Model/Sample.php

    // : command(T) -> app/Test/Case/Controller/SamplesControllerTest.php
?>
```
```php
<?php
//app/View/Samples/index.ctp

// : command(C) -> app/Controller/SamplesController.php : function index()
?>
```

## Open directory
You can choose file from panel.

| Command | Directory |Function | 
| --- | --- | --- |
| `ctrl + shift + c`, `ctrl + d` | current directory |cake_show_directory_list | 
| `ctrl + shift + c`, `ctrl + c` | controller |cake_show_controller_list | 
| `ctrl + shift + c`, `ctrl + m` | model |cake_show_model_list | 
| `ctrl + shift + c`, `ctrl + v` | view |cake_show_view_list | 
| `ctrl + shift + c`, `ctrl + o` | component |cake_show_component_list | 
| `ctrl + shift + c`, `ctrl + b` | behavior |cake_show_behavior_list | 
| `ctrl + shift + c`, `ctrl + h` | helper |cake_show_helper_list | 
| `ctrl + shift + c`, `ctrl + l` | lib |cake_show_lib_list | 
| `ctrl + shift + c`, `ctrl + shift + l` | layout |cake_show_layout_list | 
| `ctrl + shift + c`, `ctrl + shift + v` | vendor |cake_show_vendor_list | 
| `ctrl + shift + c`, `ctrl + s` | css |cake_show_css_list | 
| `ctrl + shift + c`, `ctrl + j` | javascript |cake_show_javascript_list | 
| `ctrl + shift + c`, `ctrl + e` | element |cake_show_element_list | 
| `ctrl + shift + c`, `ctrl + g` | config |cake_show_config_list | 
| `ctrl + shift + c`, `ctrl + p` | plugin |cake_show_plugin_list | 
| `ctrl + shift + c`, `ctrl + t` | test |cake_show_test_list | 
| `ctrl + shift + c`, `ctrl + f` | fixture |cake_show_fixture_list | 


#### Example
controller directory

![controller](https://raw.github.com/gold1/sublime-cakephp-find/master/docs/0001.png)

#### Open folder
- You can open folder that contains the file.

| Command | Folder |Function | 
| --- | --- | --- |
| `ctrl + shift + c`, `s`, `f` | current directory |cake_open_folder | 

## Grep
- This uses the find panel of Sublime Text.
- exclude tmp directory and several extension file

| Command | Function | 
| --- | --- |
| `ctrl + shift + c`, `s`, `g` | cake_grep | 

#### Example
![grep](https://raw.github.com/gold1/sublime-cakephp-find/master/docs/0002.png)

If you want to add or delete the string in "Where", you need to write on settings.

Write on `/Sublime Text 2/Packages/User/Preferences.sublime-settings`
```json
    "sublime_cakephp_find":
    {
        "grep_exclude_list": ["*.sh", "*.md"],
        "grep_include_list": [""]
    }
```


## Find file
A command to jump to file for the current word.

| Command | Function |
| --- | --- |
| `ctrl + shift + c`, `f` | cake_find |

### Example
```php
<?php
    //app/Controller/SamplesController.php
    
    public $components = array("Auth");
                             //|----| : command on Auth -> AuthComponent
                             
    public $helpers = array("Post"); // app/View/Helper/PostHelper.php
                          //|----| : command on Post -> PostHelper

    public function index() {
        
        // : command with the following line -> AuthComponent::allow()
        $this->Auth->allow('index');
        
        // : command with the following line -> AuthComponent::$loginRedirect
        $this->Auth->loginRedirect = null;
    }
?>
```

| Word | File |
| --- | --- |
| **Config/routes.php** | &nbsp; |
| array('controller' => 'books', 'action' => 'post') | app/Controller/BooksController.php : post() |
| **Controller** | &nbsp; |
| public $layout = 'default'; or $this->layout = 'default'; | app/View/Layouts/default.ctp |
| $this->render('index'); | app/View/Samples/index.ctp |
| $this->redirect('/Samples/index'); | function index() |
| **View** | &nbsp; |
| $this->element("photo"); | app/View/Elements/photo.ctp |
| $this->Html->script("popup"); | app/webroot/js/popup.js |
| $this->Html->css("font"); | app/webroot/css/font.css |
| $this->Html->image("cake.power.gif"); | open "app/webroot/img/cake.power.gif" |
| &lt;span class="notice"&gt;&lt;/span&gt; | find app/webroot/css/* and open file |
| &lt;div id="footer"&gt;&lt;/div&gt; | find app/webroot/css/* and open file |
| **Css** | &nbsp; |
| background: #003d4c url('../img/cake.icon.png'); | open "app/webroot/img/cake.icon.png" |
| **Anywhere** | &nbsp; |
| App::import('Lib', 'Libr'); | app/Lib/Libr.php |
| App::uses('TimedBehavior', 'DebugKit.Model/Behavior'); | app/Plugin/DebugKit/Model/Behavior/TimedBehavior.php |
| use Cake\Utility\CakeTime; // namespace | lib/Cake/Utility/CakeTime.php |
| require or include APP . 'Config' . DS . 'routes.php'; | app/Config/routes.php |
| $this->privateFunc(); | function privateFunc() |
| $this->log("message"); | lib/Cake/Core/Object.php : log() |
| self::CONST_K | const CONST_K = 'K'; |
| static::$static_k | public static $static_k = 'k'; |
| $this->Auth->allow('*'); | lib/Cake/Controller/Component/AuthComponent.php : allow() |
| CakeTime::timezone(); | lib/Cake/Utility/CakeTime.php : listTimezones() |
| CakeTime::$wordFormat | lib/Cake/Utility/CakeTime.php : $wordFormat |
| "Auth" | lib/Cake/Controller/Component/AuthComponent.php |
| $time = new CakeTime(); // It continues below. | lib/Cake/Utility/CakeTime.php |
| $time->listTimezones(); | lib/Cake/Utility/CakeTime.php : listTimezones() |
| $Email->template('default'); | app/View/Emails/text/default.ctp |
| 'datasource' => 'Database/Mysql' | lib/Cake/Model/Datasource/Database/Mysql.php |
| $fixtures = array('app.comment'); | app/Test/Fixture/CommentFixture.php |
| __("Hello!"); | app/Locale/eng/LC_MESSAGES/default.po |

## Run Test
If you want to run test, we recommend you this plug-in.

- [jwindmuller / SublimeCake](https://github.com/jwindmuller/SublimeCake)

## License
BSD License

## Version

#### 0.8.x

## Reference
Reference code, Thank you.

- [bermi](https://github.com/bermi) / [Python-Inflector](https://github.com/bermi/Python-Inflector)
- [violetyk](https://github.com/violetyk) / [cake.vim](https://github.com/violetyk/cake.vim)
- [k1LoW](https://github.com/k1LoW) / [emacs-cake2](https://github.com/k1LoW/emacs-cake2)

