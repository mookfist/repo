#!/usr/bin/env python
###
# Simple tool to turn any pypi module into a kodi addon
#
# by mookfist
###
import os
import sys
import urllib2
import tarfile
import json
import shutil
import zipfile
from xml.sax.saxutils import escape
# https://pypi.python.org/packages/source/p/pybuilder-nose/pybuilder-nose-0.0.5.tar.gz#md5=f8794d709967d109c3e1ffb86096196b

PROVIDER_NAME = "Mookfist"
XBMC_PYTHON_VER = "2.14.0"

ADDON_XML = """<?xml version="1.0" encoding="utf-8"?>
<addon id="script.module.python-%(modname)s" version="%(version)s" name="python-%(modname)s" provider-name="%(modauthor)s">
  <requires>
    <import addon="xbmc.python" version="%(xbmc_python_ver)s" />
  </requires>
  <extension point="xbmc.python.module" library="lib" />
  <extension point="xbmc.addon.metadata">
    <summary lang="en">%(summary)s</summary>
    <description lang="en">%(description)s</description>
    <disclaimer>This addon is just a wrapper around the original module found at PyPI</disclaimer>
    <language>en</language>
    <platform>all</platform> 
    <source>%(source_url)s</source>
    <email>%(author_email)s</email>
    <website>%(website)s</website>
  </extension>
</addon>"""

BASE_PATH = os.path.realpath(sys.argv[1])

mod = sys.argv[2]

metadata_url = "https://pypi.python.org/pypi/%s/json" % (mod)

tmp_dir = 'tmp/%s' % mod

if not os.path.exists(tmp_dir):
  os.makedirs(tmp_dir)

os.chdir(tmp_dir)

print "Getting metadata from %s" % metadata_url
req = urllib2.Request(metadata_url)
res = urllib2.urlopen(req)
metadata = json.loads(res.read())

ver = metadata['info']['version']

release = metadata['releases'][ver][0]

url = release['url']

ext = url.split('.')[-1]
filename = os.path.basename(url)

print "Downloading %s" % (url)

req = urllib2.Request(url)
res = urllib2.urlopen(req)

f = open(filename, 'w')
f.write(res.read())
f.close()

print "Unpacking"

if ext == "whl" or ext == "egg":
  archive = zipfile.ZipFile(filename)
elif ext == "gz" or ext == "tar" or ext == "tgz":
  archive = tarfile.open(filename)

archive.extractall()
archive.close()

if ext == "whl" or ext == "egg":
  src_dir = tmp_dir + "/" + mod
else:
  src_dir = tmp_dir + "/%s-%s/%s" % (mod, ver, mod)



addon = ADDON_XML % {
  'modname': mod,
  'version': ver,
  'modauthor': escape(metadata['info']['author']),
  'xbmc_python_ver': XBMC_PYTHON_VER,
  'summary': escape(metadata['info']['summary']),
  'description': escape(metadata['info']['description']),
  'source_url': escape(metadata['info']['package_url']),
  'author_email': escape(metadata['info']['author_email']),
  'website': escape(metadata['info']['package_url'])
}

os.chdir(BASE_PATH)

plugin_dir = 'script.module.python-%s' % mod

if not os.path.exists(plugin_dir + "/lib"):
  os.makedirs(plugin_dir + "/lib")

shutil.copyfile('python-icon.png', plugin_dir + '/icon.png')
shutil.move(src_dir, plugin_dir + "/lib")

f = open(plugin_dir + '/addon.xml','w')
f.write(addon)

shutil.rmtree(tmp_dir)
