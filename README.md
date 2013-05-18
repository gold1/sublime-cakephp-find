SublimeCakePHPFind
==================
You can find out file and open easily.
For more information, [check the wiki.](https://github.com/gold1/SublimeCakePHPFind/wiki/Wiki)

# Installation
### OSX

    $ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    $ git clone git://github.com/gold1/SublimeCakePHPFind.git

### Linux (Ubuntu like distros)

    $ cd ~/.config/sublime-text-2/Packages/
    $ git clone git://github.com/gold1/SublimeCakePHPFind.git

### Windows 7:

    Copy the directory to: "C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages"

### Windows XP:

    Copy the directory to: "C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages"

# Example

- A command to jump to class file for the current word.

```php
<?php
    //app/Controller/SamplesController.php
    
    public $components = array("Auth");
                             //|----| : command on Auth -> AuthComponent
                             
    public $helpers = array("Post"); // app/View/Helper/PostHelper.php
                          //|----| : command on Post -> PostHelper

    public function index() {
        
        $this->Auth->allow('index');
      //|-----------------| : command on line -> AuthComponent::allow()
        
        $this->Auth->loginRedirect = null;
      //|-------------------------| : command on line -> AuthComponent::$loginRedirect
        
    }
```

- You can choose file from panel.

![controller](https://raw.github.com/gold1/SublimeCakePHPFind/master/docs/0001.png)

