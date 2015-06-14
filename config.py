#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses

# colors
colors = {
    'user_input'        : 'white_blue_bold',
    'user_message'      : 'yellow_blue_bold',
    'error_message'     : 'yellow_red_bold',
    'cursor_position'   : 'cyan_blue_bold',
    'empty_dir'         : 'black_default_bold',
    'breaked_text'      : 'cyan_default',
    'information_key'   : 'white_blue_bold',
    'information_word'  : 'white_blue',
    'information_sep'   : 'red_blue_bold',
    'select'            : 'red_default_bold',
    'directory'         : 'blue_default_bold',
    'binary'            : 'green_default_bold',
    'blockdev'          : 'yellow_default_bold',
    'chardev'           : 'yellow_default_bold',
    'pipe'              : 'yellow_default',
    'socket'            : 'magenta_default_bold',
    'link'              : 'cyan_default_bold',
    'unknown'           : 'black_default_bold'
}

# programs used to open file by extension type
commands = {
    'html' : 'iceweasel',
    'pdf'  : 'xpdf',
    'ps'   : 'gv',
    'dvi'  : 'xdvi',
    'tex'  : 'xterm -e vim',
    'txt'  : 'xterm -e vim',
    'py'   : 'xterm -e vim',
    'c'    : 'xterm -e vim',
    'djvu' : 'djview',
    'djv'  : 'djview',
    'chm'  : 'xchm',
    'wmv'  : 'vlc',
    'mpeg' : 'vlc',
    'mpg'  : 'vlc',
    'avi'  : 'vlc',
    'gif'  : 'gthumb',
    'jpg'  : 'gthumb',
    'png'  : 'gthumb',
    'ppt'  : 'ooffice',
    'doc'  : 'ooffice',
    'mp3'  : 'rythmbox'
}

# favorite text editor
editor = 'gvim'

# selected item character
select_char = 'X'

# directory of the application
app_dir = '/home/gui/prog/smurf'


# end of configuration settings
#==============================================================================

pairs = {}
for i, names in enumerate(colors.keys()):
    pairs[names] = i+1

curses_vars = {
    'blue'      : curses.COLOR_BLUE,
    'white'     : curses.COLOR_WHITE,
    'magenta'   : curses.COLOR_MAGENTA,
    'red'       : curses.COLOR_RED,
    'black'     : curses.COLOR_BLACK,
    'yellow'    : curses.COLOR_YELLOW,
    'green'     : curses.COLOR_GREEN,
    'cyan'      : curses.COLOR_CYAN,
    'bold'      : curses.A_BOLD,
    'default'   : -1
}

def attribute(name):
    pair = pairs[name]
    a = colors[name].split('_')
    if len(a) == 3:
        return curses.color_pair(pair) | curses_vars[a[2]]
    else:
        return curses.color_pair(pair)

def fg_bg(name):
    return [ curses_vars[a] for a in name.split('_')[:2] ]
    
for name, number in pairs.items():
    curses.init_pair( number, *fg_bg(colors[name]) )

