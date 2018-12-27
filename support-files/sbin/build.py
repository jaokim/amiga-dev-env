#!/usr/bin/python
#
# Start a build inside a Docker container.
#
# $ver 1.0
# 
# Author: Joakim Nordstrom
#


import os

import sys
import json
import tempfile
import urllib
from subprocess import call
from shutil import copyfile


if len(sys.argv) > 1:
	dependency_file = sys.argv[1]
else:
	dependency_file = "./dependencies.json"

ade_fetch_files_cmd 	= os.environ['ADE_FETCH_FILES_CMD']
ade_make_dir		= os.environ['ADE_MAKE_DIR']
ade_make_cmd 		= os.environ['ADE_MAKE_CMD']
ade_fetch_files_cmd 	= os.environ['ADE_FETCH_FILES_CMD']


os.chdir(ade_make_dir)


print(ade_fetch_files_cmd)
call(ade_fetch_files_cmd)

os.chdir(ade_make_dir)

call("/usr/sbin/install-sdk-dependency.py")

call(ade_make_cmd)

if ade_fetch_files_cmd:
	call(ade_fetch_files_cmd)

copyfile("ArexxXml", "/workdir")
