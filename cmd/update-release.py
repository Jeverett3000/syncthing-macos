#!/usr/bin/env python3
#
# Update the Syncthing bundle based on the latest github release
# 1. Loads the latest tag name from github api
# 2. Parses the tag
# 3. Writes the syncthing/Info.plist
# 4. Update the syncthing/Scripts/syncthing-resource.sh
#
###
import sys
import json
import semver
import fileinput
from urllib.request import urlopen
from string import Template

distVersion   = 1
latest_url    = "https://api.github.com/repos/syncthing/syncthing/releases/latest"
infoPlist     = 'syncthing/Info.plist'
infoPlistTmpl = 'syncthing/Info.plist.tmpl'
syncthingResourceScript = "syncthing/Scripts/syncthing-resource.sh"

###
# Download latest tag from github
###
response = urlopen(latest_url)
body = response.read().decode("utf-8")
data = json.loads(body)

if 'tag_name' not in data:
	raise ValueError("tag_name not present in latest_url")

###
# Parse the tag version and generate CFBundleShortVersionString and CFBundleVersion
###

# Ugly hack because of https://github.com/python-semver/python-semver/issues/137
tag_name = data['tag_name'].replace('v', '')
version = semver.VersionInfo.parse(tag_name)

CFBundleShortVersionString = "{}-{:d}".format(
	str(version),
	distVersion)
CFBundleVersion = "{:d}{:03d}{:03d}{:02d}".format(
	version.major,
	version.minor,
	version.patch,
	distVersion)

###
# Update Info.plist from template
###
infoPlistTmplVars = {
	'CFBundleShortVersionString' : CFBundleShortVersionString,
	'CFBundleVersion' : CFBundleVersion
}

with open(infoPlistTmpl, 'r') as f:
	tmpl = Template(f.read())
result = tmpl.substitute(infoPlistTmplVars)

with open(infoPlist, 'w') as f:
	f.write(result)
linePrefix = 'SYNCTHING_VERSION='
###
# Update syncthing/Scripts/syncthing-resource.sh
###
for line in fileinput.input(syncthingResourceScript, inplace=True):
	if line.startswith(linePrefix):
		line = f'{linePrefix}"{str(version)}"\n'
	sys.stdout.write(line)
