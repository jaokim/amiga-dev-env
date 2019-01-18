#!/usr/bin/python
#
# Install SDK dependencies
#
#
# The <dependecies.json file> is a JSON file in its simples form looking like this:
# [
#  {"Url": "http://os4depot.net/share/library/misc/unilibdev.lha"},
#  {"Url": "http://os4depot.net/share/development/library/misc/expat.lha"}
# ]
# The JSON file can be expanded with SdkInstall instructions as below.
#
# $ver 1.2 (2019-01-19)
# 
# Author: Joakim Nordstrom
#



import sys
import json
import tempfile
import urllib
import argparse
import os.path
from subprocess import call


parser = argparse.ArgumentParser()
parser.add_argument('-f','--file', default="./dependencies.json")
parser.add_argument('-d', '--dependencies', nargs='*')
parser.add_argument('--test', help='only test what would happen', action="store_true")
parser.add_argument('--verbose', help='be verbose', action="store_true")

args = parser.parse_args()

if args.file:
	dependency_file = args.file



if args.dependencies:
	deps_urls = args.dependencies
	deps_dict = []
	for url in deps_urls:
		deps_dict.append({'Url': url})

if os.path.isfile(dependency_file):
	with open(dependency_file, 'r') as f:
		deps_dict = json.load(f)

if args.verbose:
	print("Dependency URLs:"+ deps_dict)

CROSS_ROOT = "/usr/"

# Open JSON file listing and describing download URL and installation procedure.
# "Url" contains the URL to download
# "SdkInstall" is a list of From/To objects, where From is the path in the archive, and To is
# the target path in the SDK.
# [
#   {
#     "Url": "http://os4depot.net/share/library/misc/superduperlib.lha",
#     "SdkInstall": 
#        [
#            { "From": "SuperDuper/Dev/include/amigaos4/inline4/superduper.h",    "To": "include/include_h/inline4/superduper.h"},
#            { "From": "SuperDuper/Dev/include/amigaos4/interfaces/superduper.h", "To": "include/include_h/interfaces/superduper.h"},
#        ]
#   }
# ]


if args.test:
	print("Should: download global dependecies-file")
else:
	urllib.urlretrieve("https://sourceforge.net/p/vagrant-amigaos4-crosscompiler/code/HEAD/tree/trunk/support-files/conf/dependencies.json?format=raw", "/etc/amiga-dependecies.json")

# Open default dependencies files. If the "local" dependency file doesnt contain
# an SdkInstall instructions, the global will be used.
if os.path.isfile('/etc/amiga-dependencies.json'):
	with open('/etc/amiga-dependencies.json', 'r') as f:
		global_deps_dict = json.load(f)
else:
	global_deps_dict = {}

for dep in deps_dict:
	url = dep['Url']
	archive_name = url.rsplit('/', 1)[-1]
	
	# Download archve and extract
	tempdir = tempfile.mkdtemp()
	if args.test:
		print("Should: download: "+archive_name+" to "+tempdir)
	else:
		urllib.urlretrieve(url, tempdir+"/"+archive_name)
		call("lha xw="+tempdir+" "+tempdir+"/"+archive_name, shell=True)
		call("chmod -R a+r "+tempdir, shell=True)

	# Find SdkInstall instructions
	if 'SdkInstall' in dep:
		sdk_install = dep['SdkInstall']
	else:
		for global_dep in global_deps_dict:
			if global_dep["Url"] == url:
				sdk_install = global_dep["SdkInstall"]

	if 'sdk_install' in locals():
		# Perform install
		for instruction in sdk_install:
			if args.test:
				print("Should: cp --verbose -rp "+tempdir+"/"+instruction['From']+" "+CROSS_ROOT+"ppc-amigaos/SDK/"+instruction['To'])
			else:
				call("cp --verbose -rp "+tempdir+"/"+instruction['From']+" "+CROSS_ROOT+"ppc-amigaos/SDK/"+instruction['To'], shell=True)
			
	else:
		print("No SdkInstall instruction defined for URL: "+url)


