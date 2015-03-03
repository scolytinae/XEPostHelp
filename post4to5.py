#!/usr/sbin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

svnAddCmd = '"C:\\Program Files\\SlikSvn\\bin\\svn.exe" add %s'
svnRenameCmd = '"C:\\Program Files\\SlikSvn\\bin\\svn.exe" rename %s %s'

PROJ4_DIR = "C:/work/ProjV4"
PROJ5_DIR = "C:/work/ProjV5"

changeSett = [
    ('.dproj', '.bdsproj'),
    ('.ico', ''),
    ('.dpk', '.dpk'),
    ('.groupproj', '.bdsgroup')
]

def fileCopy(source, dest):
    try:
        if (os.path.exists(dest)):
            raise Exception("File exists", dest)
        shutil.copyfile(source, dest)
        if (svnAddCmd != ''):
            subprocess.call(svnAddCmd % dest.replace('/', os.sep), shell=True)
    except Exception, e:
        print "Error %s" % e

def fileRename(source, dest):
    try:
        if (svnRenameCmd != ''):
            print svnRenameCmd % (source.replace('/', os.sep), dest.replace('/', os.sep))
            print subprocess.call(svnRenameCmd % (source.replace('/', os.sep), dest.replace('/', os.sep)), shell=True)
        else:
            os.rename(source, dest)
    except Exception, e:
        print "Can't rename %s to %s. %s" % (source, dest, e)


def fileReplace(source, dest):
    try:
        shutil.copyfile(source, dest)
        if os.path.exists(dest) == '':
            print "No such file %s. Just copy file" % dest

    except Exception, e:
        print "Can't replace %s with %s. %s" % (dest, source, e)


def copyRenameFiles(fileNew, fileOld):
    """Copy fileNew to fileOld or replace fileOld if it exists"""
    cs = findChangeSett(fileNew)
    if (os.path.exists(fileOld) and (cs[0] != cs[1])):
        print "File %s already exists" % fileOld
    elif cs[1] == "":
        print "Try to copy file %s to %s" % (fileNew, fileOld)
        fileCopy(fileNew, fileOld)
    else:
        fileDest = os.path.splitext(fileOld)[0] + cs[1]
        if os.path.exists(fileDest):
            print "Try to replace file %s with %s" % (fileDest, fileNew)
            fileReplace(fileNew, fileDest)
            if (cs[0] != cs[1]):
                print "Try to rename file %s to %s" % (fileDest, fileOld)
                fileRename(fileDest, fileOld)
        else:
            print "No dest file %s. Try to copy file %s to %s" % (fileDest, fileNew, fileOld)
            fileCopy(fileNew, fileOld)


def findChangeSett(fileName):
    """Find change settings for file name by file extension"""
    fileExt = os.path.splitext(fileName)[1]
    for i in changeSett:
        if fileExt == i[0]:
            return i
    return ('', '')


def replace_recurs(dirNew, dirOld):
    """Find and replace files with same names but with ext dependency from changeSett"""

    try:
        for f in os.listdir(dirNew):
            fileNew, fileOld = dirNew + '/' + f, dirOld + '/' + f
            if os.path.isdir(fileNew) and os.path.isdir(fileOld):
                replace_recurs(fileNew, fileOld)
            elif findChangeSett(fileNew)[0] != '':
                print "Find file %s" % fileNew
                copyRenameFiles(fileNew, fileOld)
    except Exception, e:
        print "Error listing %s. %s" % (dirNew, e.message)


if __name__ == "__main__":
    replace_recurs(PROJ5_DIR, PROJ4_DIR)
