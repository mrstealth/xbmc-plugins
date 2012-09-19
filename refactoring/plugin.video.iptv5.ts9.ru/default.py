#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-


import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib
import HTMLParser, CommonFunctions
import socket
import simplejson as json

common = CommonFunctions
common.plugin = "plugin.video.iptv5.ts9.ru"
common.dbg = True # Default
common.dbglevel = 3 # Default

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

from helpers import *
from category import Category
from channel import Channel

category_db = Category()
channel_db = Channel()

def getCategories(url):
    url=urllib.unquote_plus(url)
    page = common.fetchPage({"link": url})


    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")
        try:
            for index in range(len(optgroups)):
                optgroup = optgroups[index]
                option = options[optgroups.index(optgroup)]
                name = unescape(optgroup, 'cp1251')

                if category_db.exists(name) == 1:
                    print "### CATEGORY already in DB, skip save"
                else:
                    print "### Save category %s in DB"%name
                    category_db.save(name, index, True)

                titles = common.parseDOM(option, "option")
                links = common.parseDOM(option, "option", ret="value")

                for i, title in enumerate(titles):
                    if links[i] != 'http://u.to/rJc0Ag':
                        print "save channel " + unescape(title, 'cp1251')
                        channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
            return True

        except:
           print "Unexpected error:", sys.exc_info()[0]
           print "Unexpected error:", sys.exc_info()[1]
           print "Unexpected error:", sys.exc_info()[2]


    else:
        print page["status"]
        return False


def getChannels(name, index):
    print "*** get channels from URL for " + name + " and id " + index
    page = common.fetchPage({"link": BASE_URL})
    index = int(index)

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        print "### Save category %s in DB and update timestamp "%name
        category_db.save(name, index, False)

        for i in range(len(optgroups)):
            optgroup = optgroups[i]
            if i == index:
                option = options[optgroups.index(optgroup)]
                titles = common.parseDOM(option, "option")
                links = common.parseDOM(option, "option", ret="value")

                for i, title in enumerate(titles):
                    if links[i] != 'http://u.to/rJc0Ag':
                        if __addon__.getSetting('availability_check') == 'true':
                            if check_url(links[i]):
                                print "*** save channel: " + unescape(title, 'cp1251')
                                channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
                            else:
                                print "*** mark as unavailable: " + unescape(title, 'cp1251')
                                channel_db.save(unescape(title, 'cp1251'), links[i], index, 1)
                        else:
                            print "*** save channel without availability check: " + unescape(title, 'cp1251')
                            channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
        return True
    else:
        return False

def listFavorites():
    label = __language__(1004)

    channels = channel_db.favorites()
    print channels

    for channel in channels:
      for title,url in channel.items():
        item = xbmcPlayableItem('PLAY', title, url, 'remove')

    xbmcplugin.endOfDirectory(handle, True)


def listCategories(url):
    xbmcItem('FAVORITES', '', "[COLOR FF00FFF0]" + __language__(1000).encode('utf-8') + "[/COLOR]")
    xbmcItem('ADDCHANNEL', '', "[COLOR FF00FF00]" + __language__(2000).encode('utf-8') + "[/COLOR]")

    categories = category_db.find_all()
    if not categories:
        getCategories(url) # initial import
        categories = category_db.find_all()

    for category in categories:
        print category

        for name,optgroupid in category.items():
            if int(optgroupid) != 8:
                xbmcItem('CHANNELS', '', name, False, optgroupid)
            else:
                print optgroupid
                if __addon__.getSetting('parent_control') == 'false':
                    xbmcItem('CHANNELS', '', name, False, optgroupid)

    xbmcplugin.endOfDirectory(handle, True)

def listChannels(name, optgroupid):
    print "*** list channels " + name + ' '+ optgroupid

    outdated = category_db.find_outdated()
    print "*** detect outdated categories "
    print outdated
    #outdated = [1,2]

    if optgroupid in outdated:
        print "*** check " + name
        getChannels(name, optgroupid)

    channels = channel_db.find_by_category_id(optgroupid)

    for channel in channels:
      for title,url in channel.items():
        xbmcPlayableItem('PLAY', title, url, 'add')

    xbmcplugin.endOfDirectory(handle, True)


def addChannel():
    channel = common.getUserInput("Name", "")
    xbmcplugin.endOfDirectory(handle, True)


######################################
#import xbmc, xbmcgui

##get actioncodes from keymap.xml
#ACTION_PREVIOUS_MENU = 10
#ACTION_SELECT_ITEM = 7

#class MainClass(xbmcgui.Window):
#  def __init__(self):
#    self.strActionInfo = xbmcgui.ControlLabel(180, 60, 200, 200, '', 'font14', '0xFFBBBBFF')
#    self.addControl(self.strActionInfo)
#    self.strActionInfo.setLabel('Push BACK to quit - A to open another window')
#    self.strActionInfo = xbmcgui.ControlLabel(240, 250, 200, 200, '', 'font13', '0xFFFFFFFF')
#    self.addControl(self.strActionInfo)
#    self.strActionInfo.setLabel('This is the first window')

#  def onAction(self, action):
#    if action == ACTION_PREVIOUS_MENU:
#      self.close()
#    if action == ACTION_SELECT_ITEM:
#      popup = ChildClass()
#      popup .doModal()
#      del popup

#class ChildClass(xbmcgui.Window):
#  def __init__(self):
#    self.addControl(xbmcgui.ControlImage(0,0,800,600, 'background.png'))
#    self.strActionInfo = xbmcgui.ControlLabel(200, 60, 200, 200, '', 'font14', '0xFFBBFFBB')
#    self.addControl(self.strActionInfo)
#    self.strActionInfo.setLabel('Push BACK to return to the first window')
#    self.strActionInfo = xbmcgui.ControlLabel(240, 200, 200, 200, '', 'font13', '0xFFFFFF99')
#    self.addControl(self.strActionInfo)
#    self.strActionInfo.setLabel('This is the child window')

#  def onAction(self, action):
#    if action == ACTION_PREVIOUS_MENU:
#      self.close()

#######################################

def play_url(url):
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


params = common.getParameters(sys.argv[2])

url=None
mode=None
category=None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    title=params['title']
except: pass
try:
    category=params['category']
except: pass


if mode == 'PLAY':
    play_url(url)
elif mode == 'CHANNELS':
    listChannels(title, category)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == 'ADDCHANNEL':
    addChannel()
elif mode == None:
    listCategories(BASE_URL)
    #mydisplay = MainClass()
    #mydisplay.doModal()
    #del mydisplay
