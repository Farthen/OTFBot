#!/bin/bash
# You need:
#  * pydoctor: - get latest svn from http://codespeak.net/~mwh/pydoctor/
#              - sudo python setup.py install
#  * Nevow: - latest stable from http://www.divmod.org/trac/wiki/DivmodNevow#Download
#           - unpack, sudo python setup.py install
# Just upload the whole directory "apidocs" (which this script creates) to /home/groups/otfbot/htdocs/pages

curdir=`pwd`
dir=`dirname $0`
cd $dir/..
touch __init__.py
touch modules/__init__.py
pydoctor 	--add-package=. \
		--project-name="OtfBot" \
		--project-url="http://otfbot.berlios.de/" \
		--make-html
rm __init__.py modules/__init__.py
cd $curdir