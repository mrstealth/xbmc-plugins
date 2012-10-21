#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import xbmcgui, xbmcaddon, xbmcvfs
import os,errno
import simplejson as json
import HTMLParser, CommonFunctions

common = CommonFunctions

Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon = Addon.getAddonInfo('icon')
addon_path = Addon.getAddonInfo('path')
language = Addon.getLocalizedString

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getDownloadFolder():
    folder = Addon.getSetting('folder')
    return False if folder == 'None' else folder

def download(url, path):
    response = common.fetchPage({"link": url})
    if response['status'] == 200:
      song = json.loads(response["content"])["response"][0]
      sting = song['artist'] + '-%s'%song['title'] + '.mp3'
      title = HTMLParser.HTMLParser().unescape(sting).encode('utf-8')

      source = song['url']
      destination = path+title

      try:
          dialog = xbmcgui.DialogProgress()
          dialog.create("MP3 Downloader","Downloading file to play")
          xbmcvfs.copy(source, destination)

      except:
          print "Uncatch exception"
      else:
          dialog.close()
    else:
        print "Show notification: Can't get MP3 url"


# ***** MAIN *****
args = sys.argv[1]

if sys.argv[1]:
  folder = getDownloadFolder()
  if folder:
    download(sys.argv[1], folder)
  else:
    dialog = xbmcgui.Dialog()
    path = dialog.browse(0, 'Choose download directory', 'music', '', False, False)

    if path:
      download(sys.argv[1], path)
    else:
      print "Please select a path"
else:
  print "Error: show XBMC notification"
