#!/usr/bin/env python
# -*- coding: utf-8 -*-

from curses import KEY_LEFT, KEY_RIGHT
import re
import os
import commands

from interface import *
from manipulatefiles import *
import config


class FileManager(ManipulateDirContents):

    def __init__(self, win, dir=''):
        if dir:
            if dir[0] != '/':
                dir = os.getcwd() + os.sep + dir
            if not os.path.isdir(dir):
                dir = os.getcwd()
        else:
            dir = os.getcwd()
        ManipulateDirContents.__init__(self, dir)
        self.win = win
        self.view = ViewDirContents(win)
        keys = {
                KEY_LEFT: self.back,
                KEY_RIGHT: self.next,
                ord(';'): self.open,
                ord(':'): self.execute,
                ord('o'): self.setOption,
                ord('/'): self.setRegex,
                ord('h'): self.home,
                ord('g'): self.goto,
                ord('m'): self.move,
                ord('d'): self.delete,
                ord('c'): self.copy,
                ord('x'): self.selectGoDown,
                ord('X'): self.selectGoUp,
                ord('a'): self.selectAllItems,
                ord('n'): self.createDir,
                ord('r'): self.refresh,
                ord('?'): self.help
            }

        self.view.addKey(keys)
        self.programs = config.commands
        self.refresh()
        
    def showContents(self, index=0):
        j = 0; attr = {}; text = [];
        for info, name in self.getContents():
            text.append([])
            f = self.contents[j]
            if f.isBinary():
                type = 'bin'
            else:
                type = f.type()
            if j in self.selected:
                text[j].append(self.view.select_char)
                attr[(j, 0)] = self.view.select_attr
            else:
                text[j].append(' ')
            if 'l' in self.option:
                i = 2
                text[j].extend([info, name])
                attr[(j, i)] = self.view.file_color[type]
            else:
                i = 1
                text[j].append(name)
                attr[(j, i)] = self.view.file_color[type]
            j += 1
        self.view.setInfoSecondLine(self.cwd+os.sep,self.option,self.regex)
        self.view.setText(text, attr)
        self.view.write(index)

    def refresh(self):
        self.setContents()
        self.showContents(self.view.y)

    def back(self):
        if self.cwd:
            actualdir = self.cwd
            try:
                self.cwd = os.path.dirname(self.cwd).rstrip(os.sep)
                self.selected = []
                self.setContents()
                name = os.path.basename(actualdir)
                if name in self.file_names:
                    i = self.file_names.index(os.path.basename(actualdir))
                    if i > self.view.max_y-1:
                        self.view.Y = (self.view.max_y-1)/2
                    else:
                        self.view.Y = i
                else:
                    i = 0
                    self.view.Y = 0
                self.showContents(i)
            except OSError, error:
                self.cwd = actualdir
                self.view.message(str(error), 
                                    config.attribute('error_message'))

    def next(self):
        if self.contents:
            item_under_cursor = self.contents[self.view.y]
            actualdir = self.cwd
            if item_under_cursor.type() == 'd':
                try:
                    self.cwd = item_under_cursor.dir.rstrip(os.sep)+\
                                os.sep+item_under_cursor.name
                    self.selected = []
                    self.setContents()
                    self.showContents()
                except OSError, error:
                    self.cwd = actualdir
                    self.view.message(str(error),
                            config.attribute('error_message'))

    def home(self):
        userhome = os.path.expanduser('~').rstrip(os.sep)
        if self.cwd != userhome:
            self.cwd = userhome
            self.selected = []
            self.setContents()
            self.showContents()

    def goto(self):
        gotodir = self.view.input('Go to: ')
        if not gotodir:
            self.refresh()
            return None
        if gotodir[0] != os.sep:
            gotodir = self.cwd + os.sep + gotodir.rstrip(os.sep)
        if os.access(gotodir, os.F_OK):
            actualdir = self.cwd
            try:
                self.cwd = gotodir.rstrip(os.sep)
                self.selected = []
                self.setContents()
                self.showContents()
            except OSError, error:
                self.cwd = actualdir
                self.view.message(str(error),
                        config.attribute('error_message'))
        else:
            self.view.message("Not a directory: '%s'" % gotodir,
                    config.attribute('error_message'))

    def loop(self):
        self.view.loop()

    def setOption(self):
        option = self.view.input('Option [latr]: ')
        if re.match('[latr]+', option) or option == '':
            self.option = option
        else:
            self.option = 'l'
        self.setContents()
        self.showContents(self.view.y)

    def setRegex(self):
        regex = self.view.input('regex: ')
        if regex:
            self.regex = regex
            self.pattern = re.compile(r'%s'%regex)
            self.setContents()
            if self.contents:
                self.showContents()
            else:
                self.regex = ''
                self.setContents()
                self.showContents(self.view.y)
                self.view.message("Pattern not found: '%s'" % regex)
        else:
            self.regex = ''
            self.refresh()
    
    def selectGoDown(self):
        if self.contents:
            self.select(self.view.y)
            if self.view.y in self.selected:
                self.view.selectLine()
            else:
                self.view.unselectLine()
            self.view.move_down()
    
    def selectGoUp(self):
        if self.contents:
            self.select(self.view.y)
            if self.view.y in self.selected:
                self.view.selectLine()
            else:
                self.view.unselectLine()
            self.view.move_up()

    def selectAllItems(self):
        if self.contents:
            self.selectAll()
            self.showContents(self.view.y)

    def delete(self):
        if self.contents:
            if not self.selected:
                self.select(self.view.y)
            input = self.view.input('Remove [y/n]? ')
            if input.lower() == 'y':
                try:
                    self.deleteSelected()
                    self.refresh()
                except Exception, e:
                    self.refresh()
                    self.view.message(str(e),
                            config.attribute('error_message'))
            else:
                self.refresh()

    def copy(self):
        if self.contents:
            if not self.selected:
                self.select(self.view.y)
            input = self.view.input('Copy name: ')
            if input:
                try:
                    self.copySelected(input)
                    self.refresh()
                except Exception, e:
                    self.refresh()
                    self.view.message(str(e),
                            config.attribute('error_message'))
            else:
                self.refresh()

    def move(self):
        if self.contents:
            if not self.selected:
                self.select(self.view.y)
            input = self.view.input('Move to: ')
            if input:
                try:
                    self.moveSelected(input)
                    self.refresh()
                except Exception, e:
                    self.refresh()
                    self.view.message(str(e),
                            config.attribute('error_message'))
            else:
                self.refresh()

    def createDir(self):
        dirname = self.view.input('New directory: ')
        if dirname:
            try:
                self.makeDir(dirname)
                self.refresh()
            except Exception, e:
                self.refresh()
                self.view.message(str(e),
                        config.attribute('error_message'))
        else:
            self.refresh()
    
    def open(self):
        if self.contents:
            if not self.selected:
                self.selected.append(self.view.y)
            for i in self.selected[:]:
                item = self.contents[i]
                ext = item.extension
                if item.type() == '-' and ext in self.programs:
                    fname = item.dir+os.sep+item.name
                    cmd = '%s "%s" &>/dev/null &'%(self.programs[ext], fname)
                    os.system(cmd)
                    self.selected.remove(i)
            self.refresh()
    
    def execute(self):
        current_dir = os.getcwd()
        os.chdir(self.cwd+os.sep)
        cmd = self.view.input('Command: ')
        if cmd[0] == '!':
            cmd = cmd[1:]
            if cmd:
                try:
                    os.system(cmd)
                    self.refresh()
                except OsError, error:
                    self.view.message(str(error),
                            config.attribute('error_message'))
            else:
                self.refresh()
        elif cmd and self.contents:
            if not self.selected:
                self.selected.append(self.view.y)
            for i in self.selected[:]:
                item = self.contents[i]
                name = item.dir+os.sep+item.name
                execute = '%s "%s"' % (cmd, name)
                stat, out = commands.getstatusoutput(execute)
                self.selected.remove(i)
            self.refresh()
        else:
            self.refresh()
        os.chdir(current_dir)

    def help(self):
        show_help_screen(self.win)
        self.win.clear()
        self.setContents()
        self.showContents(self.view.y)

