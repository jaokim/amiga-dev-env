#!/usr/bin/python
#
# Install SDK dependencies
#
#
# The <dependecies.json file> is a JSON file in its simplest form looking like this:
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
# The JSON file can be expanded with SdkInstall instructions as below.
#
# $ver 1.4 (2019-02-25)
# 
# Author: Joakim Nordstrom
#



import sys
import json
import tempfile
import urllib
import argparse
import os.path
import re
from subprocess import call


# SDK location -- always end with slash
SDK_LOCATION = os.getenv('DEPGET_SDK_LOCATION', "/SDK/");
GLOBAL_DEPENDENCIES_FILE = os.getenv('DEPGET_GLOBAL_DEPENDENCIES_FILE', "./etc/amiga-dependencies.json");
GLOBAL_DEPENDENCIES_URL = "https://sourceforge.net/p/vagrant-amigaos4-crosscompiler/code/HEAD/tree/trunk/support-files/conf/dependencies.json?format=raw"

parser = argparse.ArgumentParser(
     description='Install SDK dependencies',
     epilog='''\
dep-get uses a JSON file which contains install instructions for archives with SDK-material in them.
 [
   {
     "Url": "http://os4depot.net/share/library/misc/superduperlib.lha",
     "SdkInstall": 
        [
            { "From": "SuperDuper/Dev/include/amigaos4/inline4/superduper.h",    "To": "include/include_h/inline4/superduper.h"},
            { "From": "SuperDuper/Dev/include/amigaos4/interfaces/superduper.h", "To": "include/include_h/interfaces/superduper.h"},
        ]
   }
 ]
Examples:
  dep-get --install libxml2 "pthreads 2005"       Install libxml2, libicu, and Pthreads		
  dep-get --search icu                            Search for dependency "icu"
  dep-get -f myown-dependecies.json               Install dependecies listed in the JSON file
''')
parser.add_argument('-i', '--install', nargs='*', help="list of dependencies to install" )
parser.add_argument('-g', '--generate-dep-file', action="store_true",  help="for each installed package, update the local dependency file (see -f option)")
parser.add_argument('-f','--file', default="./dependencies.json", help="JSON file with dependecies to install")
parser.add_argument('-s', '--search', help="search for a dependency")
parser.add_argument('--update', help='download a new global dependencies file', action="store_true")
parser.add_argument('--test', help='only test what would happen', action="store_true")
parser.add_argument('--verbose', help='be verbose', action="store_true")
parser.add_argument('--silent', help='be silent', action="store_true")

args = parser.parse_args()

if args.verbose:
	COPY_COMMAND = "cp --verbose -rp {install_from} {install_to}";
else: 
	COPY_COMMAND = "cp -rp {install_from} {install_to}";
UNPACK_CMD = {}
UNPACK_CMD['lha'] = "lha xw={tempdir} {archive}"
CHMOD_CMD = "chmod -R a+r {tempdir}"
				
#+tempdir+"/"+instruction['From']+" "+SDK_LOCATION+instruction['To'];

#######################################################################
# Update dependencies files
#######################################################################
if args.update:
	if not args.silent : 
		print("Updating dependencies file from: "+GLOBAL_DEPENDENCIES_URL)

	if args.test:
		print("Downloading from {}, storing to: {}".format(GLOBAL_DEPENDENCIES_URL, GLOBAL_DEPENDENCIES_FILE))
	else:
		urllib.urlretrieve(GLOBAL_DEPENDENCIES_URL, GLOBAL_DEPENDENCIES_FILE)
		
	sys.exit(0)


# Open default dependencies files. If the "local" dependency file doesnt contain
# an SdkInstall instructions, the global will be used.
if os.path.isfile(GLOBAL_DEPENDENCIES_FILE):
	with open(GLOBAL_DEPENDENCIES_FILE, 'r') as f:
		global_deps_dict = json.load(f)
else:
	if not args.silent:
		print("Global dependencies file couldn't be opened: {}", GLOBAL_DEPENDENCIES_FILE)
	global_deps_dict = {}

nothingFound = True
found = False;	

#######################################################################
# Search
#######################################################################
if args.search:
	for global_dep in global_deps_dict:
 		name = ""
		url = ""
		if "Url" in global_dep:
			url = global_dep["Url"]
		else: 
			continue

		if "Name" in global_dep:
			name = global_dep["Name"]
		else:
			idx = url.rfind("/")
			if idx <> -1:
				name = url[idx+1:len(url)]

		if url.lower() == args.search.lower():
			found = True;
		elif re.match(".*"+args.search.lower()+".*$", url.lower()):
			found = True;
		elif re.match(args.search.lower(), name.lower()):
			found = True;
		elif args.verbose :
			print("Doesnt match: "+name + " " + global_dep["Url"])

		if found : 
			print(name.ljust(32)+" "+url)
			nothingFound = False
		found = False;
	if nothingFound:
		if not args.silent: 		
			print("No archives found matching \""+args.search+"\".")
		sys.exit(5)
	sys.exit(0)

#######################################################################
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

if args.file:
	dependency_file = args.file

#######################################################################
# Read from already existing dep file, and then append stuff to it,
# adn then in the end, write to file.
#######################################################################
local_dependency_file_content = []
if args.generate_dep_file:
	if os.path.isfile(dependency_file) and os.path.getsize(dependency_file) > 0:
		with open(dependency_file, 'r') as f:
			local_dependency_file_content = json.load(f)
			if args.verbose:
				print("Read {} dependencies from {}", len(local_dependency_file_content), dependency_file)
	elif args.verbose:
		print("No existing, or empty dependency file found {}, will create new", dependency_file)

#######################################################################
# Install
#######################################################################
if args.install is not None:
	failure = False
	deps_to_install = []
	# Install from dependency file
	if len(args.install) == 0:
		dependencies = []
		if os.path.isfile(dependency_file) and os.path.getsize(dependency_file) > 0:
			if args.verbose:
				print("Loading dependencies from file {}".format(dependency_file))
			with open(dependency_file, 'r') as f:
				local_dep_file = json.load(f)
				if args.verbose:
					print("Found {} dependencies to possibly install".format(len(local_dep_file)))
				for local_dep in local_dep_file:
					# If we find the URL and isntall instructions in the local file,
					# we can download and install, otherwise, we have to find it in global
					if "Url" in local_dep and "SdkInstall" in local_dep:
						deps_to_install.append(dep)
					else:
						for global_dep in global_deps_dict:
							if ( ("Url" in global_dep and "Url" in local_dep and global_dep['Url'] == local_dep['Url']) or 
									("Name" in global_dep and "Name" in local_dep and global_dep['Name'] == local_dep['Name']) ):
								if "SdkInstall" in global_dep:
									deps_to_install.append(global_dep)
								else:
									print("No SDK installation instruction found for: {}, {}".format(dependency, url))
									failure = True
							else: 
								continue
		elif args.verbose:
			failure = True
			print("Is not a file: {}".format(dependency_file))
	# Install from command line list
	else:
	 	dependencies = args.install

		if args.verbose:
			print("Loading dependencies from command-line {}".format(dependencies))
		for dependency in dependencies:
			deps_candidates = []
			# Find dependency to install
	 		for global_dep in global_deps_dict:
				name = ""
				url = ""
				if "Url" in global_dep:
					url = global_dep["Url"]
				else: 
					continue

				archive_name = url.rsplit('/', 1)[-1]

				if "Name" in global_dep:
					name = global_dep["Name"]
				if dependency == name or dependency.lower() == url or dependency.lower() == archive_name:
					if "SdkInstall" in global_dep:
						deps_candidates.append(global_dep)
					else:
						print("No SDK installation instruction found for: {}, {}".format(dependency, url))
						failure = True

			# Make sure we have only matched one dependency
			if len(deps_candidates) == 0:
				failure = True
				if not args.silent :
					print("Found no dependency for \"{}\"".format(dependency))
			elif len(deps_candidates) > 1:
				failure = True
				print("Found {} matching dependencies for \"{}\":".format(len(deps_candidates), dependency))
				for too_many_deps in deps_candidates :
					print("   {}".format(too_many_deps['Url']))
				print("Please install using entire URL.")
			else:
				deps_to_install.append(deps_candidates[0])

	if failure: 
		print("One or more errors occured, aborting")
		sys.exit(10)
	else:
		for dep_to_install in deps_to_install:
			url = dep_to_install['Url']
			archive_name = url.rsplit('/', 1)[-1]
			if "SdkInstall" in dep_to_install:
				sdk_install = dep_to_install['SdkInstall']
			else : 
				# This should be impossible, check is done above ^
				print("No SDK install instruction for {}".format(url))
				sys.exit(10)

			# Download archive and extract	
			if args.test:
				tempdir = "tmp"
			else:
				tempdir = tempfile.mkdtemp()
	
			unpack_cmd = UNPACK_CMD['lha'].format(tempdir=tempdir, archive=tempdir+"/"+archive_name)
			chmod_cmd = CHMOD_CMD.format(tempdir=tempdir)

			if args.test:
				print("Should download {} to {}/{}".format(url,tempdir,archive_name))
				print("call: "+unpack_cmd)
				print("call: "+chmod_cmd)
			else:
				if args.verbose:
					print("Downloading {} to {}/{}".format(url,tempdir,archive_name))
				urllib.urlretrieve(url, tempdir+"/"+archive_name)
				if args.verbose:
					print("call: "+unpack_cmd)
				call(unpack_cmd, shell=True)
				if args.verbose:
					print("call: "+chmod_cmd)
				call(chmod_cmd, shell=True)

			for instruction in sdk_install:
				copy_cmd = COPY_COMMAND.format(install_from=tempdir+"/"+instruction['From'], install_to=SDK_LOCATION+instruction['To'])
				if args.test:
					print("call: "+copy_cmd)
				else:
					if args.verbose:
						print("call: "+copy_cmd)
					call(copy_cmd, shell=True)

			if not args.silent:
				print("Installed "+archive_name+" successfully.")

			if not dep_to_install in local_dependency_file_content:
				local_dependency_file_content.append({'Url':dep_to_install['Url']})
			elif args.verbose and args.generate_dep_file:
				print("Dependecy {} already in file, not adding".format(dep_to_install['Url']))
	if not args.silent:
		print("Installed {} dependencies".format(len(deps_to_install)))
if args.generate_dep_file:
	if args.verbose:
		print("Adding dependencies to {}".format(dependency_file))
	with open(dependency_file, 'w') as outfile:
		json.dump(local_dependency_file_content, outfile)


sys.exit(0)


