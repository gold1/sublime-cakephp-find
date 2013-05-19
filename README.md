sublime-cakephp-find
==================
You can find out file and open easily.
For more information, [check the wiki.](https://github.com/gold1/sublime-cakephp-find/wiki/Wiki)

# Installation
### OSX

    $ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    $ git clone git://github.com/gold1/sublime-cakephp-find.git

### Linux (Ubuntu like distros)

    $ cd ~/.config/sublime-text-2/Packages/
    $ git clone git://github.com/gold1/sublime-cakephp-find.git

### Windows 7:

    Copy the directory to: "C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages"

### Windows XP:

    Copy the directory to: "C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages"

# Example

- A command to jump to file for the current word.

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
```

- You can choose file from panel.

![controller](https://raw.github.com/gold1/sublime-cakephp-find/master/docs/0001.png)

