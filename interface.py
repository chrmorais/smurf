#!/usr/bin/env python
# -*- coding: utf-8 -*-

import libcurses
import config

def key_word(key='', word=''):
    a = config.attribute('information_key')
    b = config.attribute('information_sep')
    c = config.attribute('information_word')
    return [['[', b], [key, a], [']', b], [word+' ', c]]


class ViewDirContents(libcurses.ScreenList):

    def __init__(self, win):
        libcurses.ScreenList.__init__(self, win)
        self.setAttributes()
        self.setInfoFirstLine()
        self.select_char = config.select_char
        
    def setAttributes(self):
        self.attr_input = config.attribute('user_input')
        self.attr_message = config.attribute('user_message')
        self.attr_line = config.attribute('cursor_position')
        self.attr_brktext = config.attribute('breaked_text')
        self.attr_empty = config.attribute('empty_dir')
        self.select_attr = config.attribute('select')
        self.file_color = { 
                '-': 0, 
                'd': config.attribute('directory'),
                'b': config.attribute('blockdev'),
                'c': config.attribute('chardev'),
                'p': config.attribute('pipe'),
                's': config.attribute('socket'),
                'l': config.attribute('link'),
                '?': config.attribute('unknown'),
                'bin': config.attribute('binary')
            }

    def setInfoFirstLine(self):
        text = 'q:quit ?:help o:option /:regex x,X:select '\
                ';:open d:delete'
        info = []
        for field in text.split(' '):
            k, w = field.split(':')
            info.extend(key_word(k, w))
        self.setInfo(1, info)

    def setInfoSecondLine(self, cwd='', opt='', re=''):
        info = []
        info.extend(key_word(cwd))
        info.extend(key_word(opt))
        info.extend(key_word(re))
        self.setInfo(2, info)

    def selectLine(self):
        self.text[self.y][0] = self.select_char
        self.attr[(self.y,0)] = self.select_attr
        border = min(self.len_text-1, self.max_y-1)
        if self.Y == 0 or self.Y == border:
            self.cursor(True)
        else:
            self.writeLine()
            self.win.move(self.Y, 0)

    def unselectLine(self):
        self.text[self.y][0] = ' '
        self.attr[(self.y,0)] = 0
        border = min(self.len_text-1, self.max_y-1)
        if self.Y == 0 or self.Y == border:
            self.cursor(True)
        else:
            self.writeLine()
            self.win.move(self.Y, 0)


def show_help_screen(win):
    view = libcurses.ScreenText(win)
    win.clear()
    win.refresh()
    view.addInfo('[', config.attribute('information_sep'))
    view.addInfo('q', config.attribute('information_key'))
    view.addInfo(']', config.attribute('information_sep'))
    view.addInfo('quit', config.attribute('information_word'))
    view.addText( open(config.app_dir + '/HELP').read() )
    view.write()
    view.loop()

