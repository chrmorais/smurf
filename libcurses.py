#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses

def debug(*args):
    open('debug', 'a').write(', '.join([str(a) for a in args])+'\n')


class ScreenList(object):

    def __init__(self, stdscr):
        self.main_win = stdscr
        self.max_y, self.max_x = self.main_win.getmaxyx()
        # two lines in the bottom
        self.max_y -= 2
        self.win = self.main_win.subwin(self.max_y, self.max_x, 0, 0)
        self.win.keypad(1)
        # current line in self.text
        self.y = 0
        # previous position in self.text
        self.oldy = 0
        # current line in self.win
        self.Y = 0
        # list of text: [ [f0, f1, ..], .. [f0, f1, ..] ]
        self.text = []
        self.len_text = 0
        # attributes in the list { (l0, f0) : attr, .. }
        self.attr = {}
        # movement keys
        self.keys = {
                        curses.KEY_UP     : self.move_up,
                        curses.KEY_DOWN   : self.move_down,
                        curses.KEY_NPAGE  : self.page_down,
                        curses.KEY_PPAGE  : self.page_up,
                        curses.KEY_END    : self.move_end,
                        ord('G')          : self.move_end,
                        curses.KEY_HOME   : self.move_top,
                        curses.KEY_RESIZE : self.resize
                    }
        # bottom of the screen text
        self.info1 = []
        self.info2 = []
        # colors
        self.attr_input = 0
        self.attr_message = 0
        self.attr_line = 0
        self.attr_brktext = 0
        self.attr_empty = 0

    def setText(self, text, attr={}):
        #text must be like [ [f0, f1, ..], .. [f0, f1, ..] ]
        self.text = text
        #attr must be like { (l0, f0) : attr, .. }
        self.attr = attr
        self.len_text = len(text)
    
    def setInfo(self, info, text_attr_list):
        # info must be: 1 or 2
        # text_attr_list: [ [text, attr], [text, attr], ... ]
        if info == 1:
            self.info1 = text_attr_list
        elif info == 2:
            self.info2 = text_attr_list

    def write(self, y=0):
        self.win.clear()
        if y > self.len_text-1:
            y = self.len_text-1
        if self.len_text > 0:
            if y == 0:
                self.y = self.Y = self.oldy = 0
            else:
                self.y = self.oldy = y
                if self.Y > self.max_y-1:
                    self.Y = self.max_y-1
            begin = self.y - self.Y
            end = min(self.y+self.max_y-1-self.Y, self.len_text-1)
            for i in range(begin, end+1):
                self.writeLine(i)
            self.win.move(self.Y, 0)
            self.cursor(True)
        else:
            self.y = self.Y = self.oldy = 0
            self.win.addstr('empty', self.attr_empty)
        self.showInfo()
        self.win.noutrefresh()
        curses.doupdate()
    
    def writeLine(self, y=None):
        if y == None: 
            y = self.y
        j, x = self.win.getyx()
        size = self.max_x-2
        num_fields = len(self.text[y])
        for i in range(num_fields):
            if size > 0:
                text = self.text[y][i]
                brktext = ''
                if len(text) > size:
                    text = text[:size]
                    brktext = '>'
                size -= len(text+brktext)
                attr = self.attr.get((y, i), 0)
                if i == 0: # we don't want cursor in the selected field
                    self.win.addstr(text, attr)
                else:
                    self.win.attron(attr)
                    self.win.addstr(text)
                    if brktext:
                        self.win.addstr(brktext, self.attr_brktext)
                    self.win.attroff(attr)
                # separate by space, except first and last
                if i < num_fields-1 and size > 0:
                    if i == 0: # don't want cursor here
                        self.win.addstr(' ', 0)
                    else:
                        self.win.addch(' ')
                    size -= 1
            else:
                break
        if j != self.max_y - 1:
            self.win.addstr('\n')

    def cursor(self, on=True):
        self.win.clrtoeol()
        if on:
            self.win.attron(curses.A_STANDOUT)
        else:
            self.win.attroff(curses.A_STANDOUT)
        self.writeLine()
        self.win.move(self.Y, 0)
        if on:
            self.win.attroff(curses.A_STANDOUT)
        self.win.noutrefresh()

    def loop(self, quit=[ord('q')]):
        while True:
            if self.y != self.oldy:
                self.cursor(True)
                self.showInfo()
                curses.doupdate()
            self.oldy = self.y
            c = self.win.getch()
            if c in self.keys:
                self.keys[c]()
            elif c in quit:
                break
            else:
                continue
            self.win.move(self.Y, 0)

    def move_down(self):
        if self.y < self.len_text - 1:
            self.cursor(False)
            self.oldy = self.y
            self.y += 1
            if self.Y == self.max_y - 1:
                self.win.move(0, 0)
                self.win.deleteln()
                self.win.move(self.Y, 0)
                self.writeLine()
                self.win.noutrefresh()
            else:
                self.Y += 1

    def move_up(self):
        if self.y > 0:
            self.cursor(False)
            self.oldy = self.y
            self.y -= 1
            if self.Y == 0:
                self.win.move(self.max_y - 1, 0)
                self.win.deleteln()
                self.win.move(0, 0)
                self.win.insertln()
                self.writeLine()
                self.win.noutrefresh()
            else:
                self.Y -= 1

    def move_top(self):
        if self.y > 0:
            self.cursor(False)
            self.oldy = self.y
            self.y = self.Y = 0
            self.write()

    def move_end(self):
        if self.y < self.len_text - 1:
            self.cursor(False)
            self.oldy = self.y
            self.y = self.len_text-1
            self.Y = min(self.max_y - 1, self.len_text - 1)
            self.write(self.y)

    def page_down(self):
        if self.y < self.len_text - 1:
            self.cursor(False)
            self.oldy = self.y
            self.y = min(self.y + self.max_y - 1, self.len_text - 1)
            if self.y >= self.max_y - 1:
                self.win.clear()
                self.win.move(0, 0)
                for i in range(self.y - (self.max_y - 1), self.y + 1):
                    self.writeLine(i)
                self.Y = self.max_y - 1
            else:
                self.Y = self.len_text - 1
            self.win.noutrefresh()

    def page_up(self):
        if self.y > 0:
            self.cursor(False)
            self.oldy = self.y
            self.y = max(self.y - (self.max_y - 1), 0)
            self.win.clear()
            self.win.move(0,0)
            end = min(self.max_y - 1, self.len_text - 1)
            for i in range(self.y, self.y + end + 1):
                self.writeLine(i)
            self.Y = 0
            self.win.move(self.Y, 0)
            self.win.noutrefresh()

    def resize(self):
        self.max_y, self.max_x = self.main_win.getmaxyx()
        self.max_y -= 2
        self.main_win.clear()
        self.win = self.main_win.subwin(self.max_y, self.max_x, 0, 0)
        self.win.keypad(1)
        self.write(self.y)

    def addKey(self, dict):
        for key, func in dict.items():
            if not (key in self.keys or key == ord('q')):
                self.keys[key] = func

    def showInfo(self):
        self.main_win.move(self.max_y, 0)
        self.main_win.deleteln()
        self.main_win.deleteln()
        # first line of the bottom
        size = self.max_x-1
        for text, attr in self.info1:
            if size == 0:
                break
            if len(text) > size:
                text = text[:size]
            size -= len(text)
            self.main_win.addstr(text, attr)
        else:
            self.main_win.addstr(' '*size, attr)
        # second line of the bottom
        self.main_win.move(self.max_y+1, 0)
        if self.len_text > 0:
            line = '%i-%i' % (self.y+1, self.len_text)
        else:
            line = ''
        size = self.max_x-1-len(line)-1
        for text, attr in self.info2:
            if size == 0:
                break
            if len(text) > size:
                text = text[:size]
            size -= len(text)
            self.main_win.addstr(text, attr)
        else:
            self.main_win.addstr(' '*size, attr)
        self.main_win.addch(' ', attr)
        self.main_win.addstr(line, self.attr_line)
        self.main_win.noutrefresh()

    def input(self, text, attr=0):
        if not attr:
            attr = self.attr_input
        self.main_win.move(self.max_y, 0)
        self.main_win.deleteln()
        self.main_win.deleteln()
        self.main_win.move(self.max_y+1,0)
        self.main_win.addstr(text[:self.max_x-1], attr)
        self.main_win.keypad(1)
        self.main_win.idlok(1)
        curses.echo()
        curses.curs_set(1)
        self.main_win.refresh()
        input = self.main_win.getstr()
        curses.curs_set(0)
        curses.noecho()
        self.main_win.keypad(0)
        self.main_win.idlok(0)
        return input
    
    def message(self, text, attr=0):
        if not attr: 
            attr = self.attr_message
        self.main_win.move(self.max_y, 0)
        self.main_win.deleteln()
        self.main_win.deleteln()
        self.main_win.move(self.max_y+1, 0)
        self.main_win.addstr(text[:self.max_x-1], attr)
        self.main_win.refresh()


class ScreenText(object):

    def __init__(self, stdscr):
        self.main_win = stdscr
        self.max_y, self.max_x = stdscr.getmaxyx()
        # one line in the bottom only
        self.max_y -=1
        # max lines in the pad. Can be a large number.
        self.lines = 5000
        # pad where text will be printed
        self.win = curses.newpad(self.lines, self.max_x)
        self.win.keypad(1)
        # bottom of the page
        self.footer = self.main_win.subwin(1, self.max_x, self.max_y, 0)
        # current position
        self.y = 0
        self.oldy = 0
        # text to be displayed, [ [text, attr], [text, attr], ..]
        self.data = []
        self.len_text = 0
        # bottom screen information
        self.info_data = []
        self.keys = {
                        curses.KEY_UP       : self.move_up,
                        curses.KEY_DOWN     : self.move_down,
                        curses.KEY_NPAGE    : self.page_down,
                        curses.KEY_PPAGE    : self.page_up,
                        ord('g')            : self.move_top,
                        curses.KEY_HOME     : self.move_top,
                        ord('G')            : self.move_end,
                        curses.KEY_END      : self.move_end,
                        curses.KEY_RESIZE   : self.resize    
                    }
        # attributes
        self.attr_input = 0
        self.attr_message = 0
        self.attr_line = 0

    def addText(self, text, attr=0):
        self.data.append( [text, attr] )

    def addInfo(self, text, attr=0):
        self.info_data.append( [text, attr] )

    def write(self):
        self.win.move(0, 0)
        for text, attr in self.data:
            self.win.addstr(text, attr)
        self.len_text, i = self.win.getyx()
        if self.y == 0:
            self.y = min(self.max_y-1, self.len_text-1)
        self.oldy = self.y
        smaxrow = min(self.max_y - 1, self.len_text)
        smaxcol = self.max_x - 1
        pminrow = self.y - smaxrow
        self.win.noutrefresh(pminrow, 0, 0, 0, smaxrow, smaxcol)
        self.showInfo()
        curses.doupdate()

    def loop(self, quit=[ord('q')]):
        while True:
            if self.y != self.oldy:
                pminrow = self.y - (self.max_y - 1)
                smaxrow = self.max_y - 1
                self.showInfo()
                self.win.noutrefresh(pminrow, 0, 0, 0, smaxrow, self.max_x-1)
                curses.doupdate()
            self.oldy = self.y
            c = self.win.getch()
            if c in self.keys:
                self.keys[c]()
            elif c in quit:
                curses.curs_set(0)
                return c
    
    def move_down(self):
        if self.y < self.len_text - 1:
            self.y += 1

    def move_up(self):
        if self.y > self.max_y - 1:
            self.y -= 1

    def page_down(self):
        if self.y < self.len_text - 1:
            self.y = min(self.y + self.max_y - 1, self.len_text - 1)

    def page_up(self):
        if self.y > self.max_y - 1:
            self.y = max(self.y - (self.max_y - 1), self.max_y - 1)

    def move_top(self):
        self.y = min(self.max_y - 1, self.len_text - 1)

    def move_end(self):
        self.y = self.len_text - 1
    
    def resize(self):
        top = self.y - min(self.max_y-1, self.len_text-1)
        self.main_win.clear()
        self.main_win.refresh()
        # new screen size
        self.max_y, self.max_x = self.main_win.getmaxyx()
        self.max_y -= 1
        self.win = curses.newpad(self.lines, self.max_x)
        self.win.keypad(1)
        self.win.idlok(1)
        self.footer = self.main_win.subwin(1, self.max_x, self.max_y, 0)
        self.y = min(top+self.max_y-1, self.len_text-1)
        self.write()

    def addKey(self, dict):
        for key, func in dict.items():
            if not (key in self.keys or key == ord('q')):
                self.keys[key] = func

    def showInfo(self):
        self.footer.deleteln()
        self.footer.move(0, 0)
        if self.len_text > 0:
            percent = float(self.y+1)/float(self.len_text)*100
            line = '%i%%' % percent
        else:
            line = ''
        size = self.max_x-1-len(line)-1
        for text, attr in self.info_data:
            if size == 0:
                break
            if len(text) >= size:
                text = text[:size]
            size -= len(text)
            self.footer.addstr(text, attr)
            y, x = self.footer.getyx()
        else:
            self.footer.addstr(' '*size)
        self.footer.addch(' ')
        self.footer.addstr(line, self.attr_line)
        self.footer.move(0, x)
        curses.curs_set(1)
        self.footer.noutrefresh()

    def input(self, text, attr=0):
        if not attr:
            attr = self.attr_input
        self.footer.clear()
        self.footer.addstr(text[:self.max_x-1], attr)
        curses.curs_set(1)
        curses.echo()
        self.footer.keypad(1)
        self.footer.idlok(1)
        self.footer.refresh()
        input = self.footer.getstr()
        curses.noecho()
        self.footer.keypad(0)
        self.footer.idlok(0)
        return input

    def message(self, text, attr=0):
        if not attr: 
            attr = self.attr_message
        self.footer.clear()
        self.footer.addstr(text[:self.max_x-1], attr)
        self.footer.refresh()


def begin_curses():
    win = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.curs_set(0)
    curses.meta(1)
    curses.start_color()
    curses.use_default_colors()
    return win

def end_curses():
    curses.echo()
    curses.curs_set(1)
    curses.nocbreak()
    curses.endwin()

