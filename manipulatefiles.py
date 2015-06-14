#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import re
import stat
import time
import pwd
import grp
import math


class FileInfo(object):

    def __init__(self, path):
        '''path is the complete file system path to file or directory.'''
        self.dir = os.path.dirname(path)
        self.name = os.path.basename(path)
        x, ext = os.path.splitext(self.name)
        self.extension = ext.strip('.')
        data = os.lstat(path)
        self.mode = data[0]
        self.uid = data[4]
        self.gid = data[5]
        self.size = data[6] 
        self.atime = data[7]
        self.mtime = data[8]
        self.ctime = data[9]

    def __repr__(self):
        return "%s %s" % self.repr()

    def __str__(self):
        return "%s %s" % self.repr()
    
    def __cmp__(self, other):
        return cmp(other.mtime, self.mtime) or \
               cmp(self.name.lower(), other.name.lower())

    def repr(self):
        return ( '%s%s %8s %8s %7s %s' % (
                 self.type(),self.perm(),self.owner(),self.group(),
                 self.hsize(),self.modified() 
                 ), self.name 
               )

    def perm(self):
        '''Return a string representing the permissions.'''
        out = ''
        for who in ('USR', 'GRP', 'OTH'):
            for perm in ('R', 'W', 'X'):
                if self.mode & getattr(stat, 'S_I' + perm + who, 0):
                    out += perm.lower()
                else:
                    out += '-'
        return out

    def type(self):
        '''Return a char representing the type of the file.'''
        map = { 'd': stat.S_ISDIR,  'b': stat.S_ISBLK,  'c': stat.S_ISCHR, 
                'p': stat.S_ISFIFO, 's': stat.S_ISSOCK, 'l': stat.S_ISLNK,
                '-': stat.S_ISREG }
        out = '?'
        for char, func in map.items():
            if func(self.mode):
                out = char
                break
        return out

    def owner(self):
        '''Return owner name.'''
        return pwd.getpwuid(self.uid)[0]

    def group(self):
        '''Return group name.'''
        return grp.getgrgid(self.gid)[0]

    def modified(self):
        '''Return last modified time.'''
        return self.time_format(self.mtime)

    def created(self):
        '''Return created time.'''
        return self.time_format(self.ctime)

    def accessed(self):
        '''Return last accessed time.'''
        return self.time_format(self.atime)

    def hsize(self):
        '''Return the file size in human format.'''
        if not self.size:
            return '0'
        unit = ",K,M,G,T,P,E,Z,Y".split(',')
        base = math.floor(math.log(self.size, 1024))
        value = float(self.size) / math.pow(1024, base)
        return '%.1f%s' % (value, unit[int(base)])

    def time_format(self, seconds):
        '''Transform time from seconds to formatted time.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(seconds))
    
    def canRead(self):
        '''Return True if we can read file.'''
        return os.access(self.dir+os.sep+self.name, os.R_OK)

    def canWrite(self):
        '''Return True if we can write to file.'''
        return os.access(self.dir+os.sep+self.name, os.W_OK)

    def canExecute(self):
        '''Return True if file is executable.'''
        return os.access(self.dir+os.sep+self.name, os.X_OK)

    def isBinary(self):
        '''Return True if file is binary.'''
        return (self.type() == '-' and self.canExecute())


class ManipulateDirContents(object):

    def __init__(self, dirpath):
        # current working directory
        self.cwd = dirpath.rstrip(os.sep)
        # list of FileInfo objects
        self.contents = []
        # list of file names only
        self.file_names = []
        # selected items in current directory
        self.selected = []
        # option to show file information, can be a combination of [latr]
        self.option = 'l'
        # regular expression
        self.regex = ''
        # compiled regular expression
        self.pattern = ''

    def reFilter(self, list):
        return [name for name in list if self.pattern.match(name)]

    def setContents(self):
        if 'a' not in self.option:
            entries = [a for a in os.listdir(self.cwd+os.sep) if a[0] != '.']
        else:
            entries = os.listdir(self.cwd+os.sep)

        if self.regex:
            entries = self.reFilter(entries)
        
        if 't' not in self.option:
            entries.sort(lambda a,b: cmp(a.lower(), b.lower()))
            self.file_names = entries
            
        self.contents = []
        for entry in entries:
            path = '%s%s%s' % (self.cwd, os.sep, entry)
            self.contents.append( FileInfo(path) )
        
        if 't' in self.option:
            self.contents.sort()
            self.file_names = [f.name for f in self.contents]
        
        if 'r' in self.option:
            self.contents.reverse()
            self.file_names.reverse()

    def getContents(self):
        return [a.repr() for a in self.contents]

    def select(self, j):
        if j not in self.selected:
            self.selected.append(j)
        else:
            self.selected.remove(j)

    def selectAll(self):
        if len(self.selected) == len(self.contents):
            self.selected = []
        else:
            self.selected = []
            for j in range(len(self.contents)):
                self.selected.append(j)

    def deleteSelected(self):
        for j in self.selected[:]:
            f = self.contents[j]
            path = self.cwd + os.sep + f.name
            if f.type() == 'd':
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.selected.remove(j)

    def copySelected(self, dst):
        dst = dst.rstrip(os.sep)
        if dst[0] != os.sep:
            dst = self.cwd + os.sep + dst
        if os.access(dst, os.F_OK):
            if os.path.isdir(dst):
                type = 'dir'
            else:
                type = 'file'
        else:
            type = ''
        for j in self.selected[:]:
            f = self.contents[j]
            src = self.cwd + os.sep + f.name
            to = dst
            if type == 'dir':
                to = dst + os.sep + f.name
            elif type == 'file':
                os.remove(dst)

            if f.type() == 'd':
                shutil.copytree(src, to, symlinks=True)
            else:
                shutil.copy(src, to)
            self.selected.remove(j)

    def makeDir(self, dirname):
        dirname = dirname.rstrip(os.sep)
        if dirname[0] != os.sep:
            dirname = self.cwd + os.sep + dirname
        os.mkdir(dirname)

    def moveSelected(self, newname):
        newname = newname.rstrip(os.sep)
        if newname[0] != os.sep:
            newname = self.cwd + os.sep + newname
        for j in self.selected[:]:
            f = self.contents[j]
            oldname = self.cwd + os.sep + f.name
            shutil.move(oldname, newname)
            self.selected.remove(j)

