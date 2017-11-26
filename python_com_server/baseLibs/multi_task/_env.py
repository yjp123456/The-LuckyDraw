#!/usr/bin/python2.7
#coding=utf8

__all__ = []

import sys
import os
libs_path =  ["../../",
              ]

Home_Path = os.environ.get('PY_DEV_HOME')
if Home_Path is None:
    Home_Path = '.'

for _path in libs_path:
    sys.path.append(Home_Path+'/'+_path)

def addPaths(top_dir = None):
    if top_dir is None or top_dir == '':
        top_dir = Home_Path
    for _path in libs_path:
        sys.path.append(top_dir+'/'+_path)