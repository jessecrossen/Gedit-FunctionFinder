Gedit-FunctionFinder
================

A plugin for gedit 3+ that allows you to quickly find function and class definitions in the current file. Just use **Control-R** and start typing, and the definition you're looking for should scroll into view and get highlighted.

Installing
==========

First, make sure you have [Exuberant CTags](http://ctags.sourceforge.net/) installed. This is what's used to index the class and function definitions in your source code.

Install the plugin itself by cloning the repo:

    $ git clone https://github.com/jessecrossen/Gedit-FunctionFinder.git
    $ cd Gedit-FunctionFinder
    $ ./install.sh
    
Or by unpacking a snapshot if don't want to use git:

    $ wget https://github.com/jessecrossen/Gedit-FunctionFinder/archive/master.zip
    $ unzip master.zip
    $ cd Gedit-FunctionFinder-master
    $ ./install.sh

Then restart gedit from the console and enable the "Function Finder" plugin in the preferences dialog. If you see something like this in your console output:

    (gedit:4579): libpeas-WARNING **: Could not find loader 'python3' for plugin 'functionfinder'
    
...then you're probably running a version of gedit earlier than 3.12 that doesn't require Python 3.  Edit the second line of functionfinder.plugin to read as follows:

    Loader=python
    
Then re-run install.sh and try again from there.

Usage
=====

Use **Control-R** to enter search mode. Start typing any keyword characters (alphanumerics plus underscore) to add to your search query and use backspace to remove characters from it. The query will be fuzzy-matched against class and function definitions in the last-saved version of the current file, and the keyword you're looking for should get highlighted at some point. Click or press any other key to exit search mode. Exit using the **Return** key to select the matched keyword for instant editing.

