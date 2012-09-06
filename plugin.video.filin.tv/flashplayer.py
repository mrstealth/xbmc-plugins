#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-

import os, json
import xbmc, xbmcaddon

from traceback import print_exc
#from threading import Timer


Addon = xbmcaddon.Addon(id='plugin.video.filin.tv')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

def setWatched(url):
    #print "******* Filin.tv: mark item as watched"
    data = getWatched()
        
    if not data == None and not url in getWatched():
        data.append(url)
    
        try:
            file_path = os.path.join( addon_cache , "watched.db" )            
            with open(file_path, 'wb') as outfile:
                json.dump(data, outfile)
        except:
            print_exc()

def getWatched():
    try:
        file_path = os.path.join( addon_cache , "watched.db" )
        with open(file_path) as infile:
            data = json.load(infile)
        return data
        
    except IOError, e:
        data = []
        return data
        
class FlashPlayer( xbmc.Player ):

    def __init__( self, core=None ):
        xbmc.Player.__init__(self)
        self.url = None

    def play( self, url, item ):
        # TODO: get start offset and resume playback
        self.url = url        
        xbmc.Player().play( url, item )
    
    def onPlayBackEnded( self ):
        setWatched(self.url)

    #def onPlayBackStarted( self ):
        #print "******* FlashPlayer: onPlayBackStarted"
        
    #def onPlayBackStopped( self ):
        #print "******* FlashPlayer: onPlayBackStopped"
        #setWatched(self.url)
        #xbmc.Player().stop()
        # TODO: get player.getTime() = start offset and save in file