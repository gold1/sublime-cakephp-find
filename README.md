sublime-cakephp-find
==================
You can find out file and open easily.

## Requirements

- Sublime Text 2.x
- CakePHP ver.1.3.x or ver.2.x

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
- It changes to a corresponding file. 

| Command | Function |
| --- | --- |
| `ctrl + shift + c`, `c` | cake_switch_to_controller |
| `ctrl + shift + c`, `v` | cake_switch_to_view |
| `ctrl + shift + c`, `m` | cake_switch_to_model |
| `ctrl + shift + c`, `t` | cake_switch_to_test |

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
- You can choose file from panel.

| Command | Function | Directory |
| --- | --- | --- |
| `ctrl + shift + c`, `ctrl + d` | cake_show_directory_list | current directory |
| `ctrl + shift + c`, `ctrl + c` | cake_show_controller_list | controller |
| `ctrl + shift + c`, `ctrl + m` | cake_show_model_list | model |
| `ctrl + shift + c`, `ctrl + v` | cake_show_view_list | view |
| `ctrl + shift + c`, `ctrl + o` | cake_show_component_list | component |
| `ctrl + shift + c`, `ctrl + b` | cake_show_behavior_list | behavior |
| `ctrl + shift + c`, `ctrl + h` | cake_show_helper_list | helper |
| `ctrl + shift + c`, `ctrl + l` | cake_show_lib_list | lib |
| `ctrl + shift + c`, `ctrl + y` | cake_show_layout_list | layout |
| `ctrl + shift + c`, `ctrl + s` | cake_show_css_list | css |
| `ctrl + shift + c`, `ctrl + j` | cake_show_javascript_list | javascript |
| `ctrl + shift + c`, `ctrl + e` | cake_show_element_list | element |
| `ctrl + shift + c`, `ctrl + g` | cake_show_config_list | config |
| `ctrl + shift + c`, `ctrl + p` | cake_show_plugin_list | plugin |
| `ctrl + shift + c`, `ctrl + t` | cake_show_test_list | test |


#### Example

- controller directory

![controller](https://raw.github.com/gold1/sublime-cakephp-find/master/docs/0001.png)



## Find file

- A command to jump to file for the current word.

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
| **Controller** | &nbsp; |
| public $layout = 'default'; | app/View/Layouts/default.ctp |
| $this->layout = 'default'; | app/View/Layouts/default.ctp |
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
| self::$static_k | public static $static_k = 'k'; |
| self::CONST_K | const CONST_K = 'K'; |
| $this->index(); | function index() |
| App::import('Lib', 'Libr'); | app/Lib/Libr.php |
| App::uses('TimedBehavior', 'DebugKit.Model/Behavior'); | app/Plugin/DebugKit/Model/Behavior/TimedBehavior.php |
| $time = new CakeTime(); // It continues below. | lib/Cake/Utility/CakeTime.php |
| $time->listTimezones(); | lib/Cake/Utility/CakeTime.php : listTimezones |
| CakeTime::timezone(); | lib/Cake/Utility/CakeTime.php : listTimezones |
| CakeTime::$wordFormat | lib/Cake/Utility/CakeTime.php : $wordFormat |
|  $this->Auth->allow('*'); | lib/Cake/Controller/Component/AuthComponent.php : allow() |


## Reference

Reference code, Thank you.

- [violetyk](https://github.com/violetyk) / [cake.vim](https://github.com/violetyk/cake.vim)
- [k1LoW](https://github.com/k1LoW) / [emacs-cake2](https://github.com/k1LoW/emacs-cake2)

