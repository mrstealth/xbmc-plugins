#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import xbmc,xbmcaddon
from channel import Channel

__addon__    = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
__language__ = __addon__.getLocalizedString
addon_icon    =__addon__.getAddonInfo('icon')

args = sys.argv[1].split("|")
        
if(args[0] == "add"):
    channel = Channel().addToFav(args[1])

    title = __language__(1000).encode('utf-8')
    message = __language__(1003).encode('utf-8')
        
    xbmc.executebuiltin("XBMC.Notification("+ title +","+ message +","+ str(3*1000) +","+ addon_icon +")")

elif(args[0] == "remove"):
    channel = Channel().removeFromFav(args[1])

    title = __language__(1000).encode('utf-8')
    message = __language__(1004).encode('utf-8')

    xbmc.executebuiltin("XBMC.Notification("+ title +","+ message +","+ str(3*1000) +","+ addon_icon +")")
    xbmc.executebuiltin("Container.Refresh")

else:
    print sys.argv[0]
    print "INVALID ARG PASSED IN (sys.argv[1]=" + sys.argv[1]
