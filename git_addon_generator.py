#!/usr/bin/env python
################################################3
# Adds an addon from a git repoi
#
# Assumes root folder of git repo is the addon folder
################################################
import os, shutil
import sys
import subprocess
from xml.dom import minidom

def setup_addon(repo, branch=None):

  tmp_dir = '%s/tmp/cloned_addon' % (os.path.expanduser('~'))
  cur_dir = os.getcwd()

  print "--- Checkout of Repository"

  p = subprocess.Popen(['git','clone','--verbose', repo, tmp_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  for line in p.stdout:
    print line

  os.chdir(tmp_dir)

  if branch != None:

    print "--- Switching branches"

    p = subprocess.Popen(['git','checkout',branch], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout:
      print line

  os.chdir(cur_dir)

  addon = open(tmp_dir + '/addon.xml')

  doc = minidom.parse('%s/addon.xml' % tmp_dir)
  addon = doc.getElementsByTagName('addon')[0]

  addon_id = addon.getAttribute('id')
  addon_version = addon.getAttribute('version')

  print '--- Kodi Addon: %s v%s' % (addon_id, addon_version)

  # os.makedirs(addon_id)

  addon_dir = cur_dir + '/' + addon_id

  print '--- Target Addon Directory: %s' % addon_dir

  if os.path.exists(addon_dir):
    print '--- Deleting previous addon'
    shutil.rmtree(addon_dir)

  print '--- Copying cloned repository to addon path'
  shutil.copytree(tmp_dir, addon_dir)

  print '--- Deleting .git folder from addon path'
  shutil.rmtree(addon_dir + '/.git')

  print '--- Deleting temporary folder'
  shutil.rmtree(tmp_dir)

repos = open('./repos.txt')

for line in repos:
  parts = line.strip().split(' ')
  if len(parts) == 2:
    repo = parts[0]
    branch = parts[1]
  elif len(parts) == 1:
    repo = parts[0]
    branch = None
  else:
    print 'bad repo line: %s' % line
    continue

  setup_addon(repo, branch)

