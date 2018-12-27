#!/usr/bin/python
#
# Install SDK dependencies
#
# Usage: python /vagrant/install-sdk-dependency.py <dependecies.json file>
#
# The <dependecies.json file> is a JSON file in its simples form looking like this:
# [
#  {"Url": "http://os4depot.net/share/library/misc/unilibdev.lha"},
#  {"Url": "http://os4depot.net/share/development/library/misc/expat.lha"}
# ]
# The JSON file can be expanded with SdkInstall instructions as below.
#
# $ver 1.1 (2018-11-18)
# 
# Author: Joakim Nordstrom
#



import sys
import json
import tempfile
import urllib
from subprocess import call


if len(sys.argv) > 1:
	dependency_file = sys.argv[1]
else:
	dependency_file = "./dependencies.json"


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
with open(dependency_file, 'r') as f:
    deps_dict = json.load(f)

urllib.urlretrieve("https://sourceforge.net/p/vagrant-amigaos4-crosscompiler/code/HEAD/tree/trunk/support-files/conf/dependencies.json?format=raw", "/etc/amiga-dependecies.json")

# Open default dependencies files. If the "local" dependency file doesnt contain
# an SdkInstall instructions, the global will be used.
with open('/etc/amiga-dependencies.json', 'r') as f:
    global_deps_dict = json.load(f)


for dep in deps_dict:
	url = dep['Url']
	archive_name = url.rsplit('/', 1)[-1]
	
	# Download archve and extract
	tempdir = tempfile.mkdtemp()
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
			call("cp --verbose -rp "+tempdir+"/"+instruction['From']+" "+CROSS_ROOT+"ppc-amigaos/SDK/"+instruction['To'], shell=True)
	else:
		print("No SdkInstall instruction defined for URL: "+url)
