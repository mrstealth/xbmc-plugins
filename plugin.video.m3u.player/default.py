#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.5
# -*- coding: utf-8 -*-

import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import urllib, urllib2, httplib, socket
import os, sys, glob, shutil
import XbmcHelpers

common = XbmcHelpers
timeout = 5
socket.setdefaulttimeout(timeout)

class M3UPlayer():
    def __init__(self):
        self.id = 'plugin.video.m3u.player'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')

        self.playlists = os.path.join(self.path,'playlists')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])

    def main(self):
        print self.path

        params = common.getParameters(sys.argv[2])
        mode = url = category = None

        mode = params['mode'] if params.has_key('mode') else None
        url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
        playlist = params['playlist'] if params.has_key('playlist') else None

        if mode == 'play':
            self.play(url)
        elif mode == 'import':
            self.importPlaylists()
        elif mode == 'remove':
            self.removePlaylist(playlist)
        elif mode == 'remove_all':
            self.removeAllPlaylists()
        elif mode == 'playlist':
            self.listChannels(playlist)
        elif mode == None:
            self.menu()


    # Common functions
    def menu(self):
        #item = xbmcgui.ListItem("[COLOR=FF00FF00]Favorites[/COLOR]", iconImage = self.icon, thumbnailImage = self.icon)
        #uri = sys.argv[0] + '?mode=import'
        #xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        item = xbmcgui.ListItem("[COLOR=FF00FFF0]Import playlists[/COLOR]", iconImage = self.icon, thumbnailImage = self.icon)
        uri = sys.argv[0] + '?mode=import'
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.listPlaylists()


    def play(self, url):
        print "\n *** URL %s"%url

        try:
            response = urllib2.urlopen(url, None, 5)
            print "*** Got server response"
            print response.info()

            item = xbmcgui.ListItem(path = response.geturl())
            item.setProperty('mimetype', response.info()['Content-type'])
            xbmcplugin.setResolvedUrl(self.handle, True, item)

        except urllib2.HTTPError, e:
            print "***** Oops, HTTPError ", str(e.code)
            if e.code == 401:
                print "401 Unauthorized"
            return False
        except urllib2.URLError, e:
            print "***** Oops, URLError", str(e.args)

            # skip rtsp:// and mmsh:// protocols
            if not str(e.args).find("rtsp") == -1 or not str(e.args).find("mmsh") == -1:
                item = xbmcgui.ListItem(path = url)
                xbmcplugin.setResolvedUrl(self.handle, True, item)
            else:
                try:
                    print "*** Authenticated URL detected? (get URL after redirect)"
                    request = urllib2.Request(url)
                    opener = urllib2.build_opener(SmartRedirectHandler())
                    auth_url = opener.open(request)

                    item = xbmcgui.ListItem(path = auth_url)
                    xbmcplugin.setResolvedUrl(self.handle, True, item)
                except:
                    print "*** Unable to play this URL %s"%url

        except httplib.InvalidURL, e:
            try:
                request = urllib2.Request(url)
                opener = urllib2.build_opener(SmartRedirectHandler())
                auth_url = opener.open(request)

                item = xbmcgui.ListItem(path = auth_url)
                xbmcplugin.setResolvedUrl(self.handle, True, item)

            except:
                print "*** Unable to play this URL %s"%url
        except socket.timeout, e:
            print "***** Oops timed out! ", str(e.args)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return []


    def showErrorMessage(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))


    # Playlist functions
    def listPlaylists(self):
      os.chdir(self.playlists)

      for playlist in sorted(glob.glob("*.m3u")):
        uri = sys.argv[0] + '?mode=playlist&playlist=%s'%playlist
        item = xbmcgui.ListItem(playlist, iconImage = self.icon, thumbnailImage = self.icon)

        runner1 = "XBMC.RunPlugin(plugin://plugin.video.m3u.player/" + "?mode=remove&playlist=" + playlist + ")"
        runner2 = "XBMC.RunPlugin(plugin://plugin.video.m3u.player/" + "?mode=remove_all" + ")"

        item.addContextMenuItems([(self.language(1000), runner1), (self.language(1001), runner2)])
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

      xbmcplugin.endOfDirectory(self.handle, True)


    def importPlaylists(self):
      print "**** import playlists"
      path = self.addon.getSetting('playlist_folder')

      if not path:
         dialog = xbmcgui.Dialog()
         path = dialog.browse(0, 'Choose m3u playlists directory', 'video', '', False, False)

      print "**** Find playlists in %s dir"%path

      if path:
        os.chdir(path)

        for f in glob.glob("*.m3u"):
          print "**** Playlist %s found"%f

          try:
            shutil.copy2(f, self.playlists)
            print('**** File ' + f + ' copied.')
          except IOError:
            print('file "' + f + '" already exists')

          xbmcplugin.endOfDirectory(self.handle, False)


    def removePlaylist(self, playlist):
      print "**** remove %s"%playlist
      f = os.path.join(self.playlists, playlist)
      os.remove(f)

      xbmc.executebuiltin("Container.Refresh")
      xbmcplugin.endOfDirectory(self.handle, True)


    def removeAllPlaylists(self):
      print "**** remove all playlists"
      for f in glob.glob("*.m3u"):
        print "**** Playlist %s found"%f

        try:
          os.remove(f)
          print('**** File ' + f + ' removed')
        except Exception, e:
          print e

      xbmc.executebuiltin("Container.Refresh")
      xbmcplugin.endOfDirectory(self.handle, True)

    # Channel functions
    def listChannels(self, playlist):
        print "*** ListChannels %s"%playlist
        channels = self.m3u_to_dict(playlist)

        if channels:
          for key in sorted(channels.iterkeys()):
            uri = sys.argv[0] + '?mode=play&url=%s'%urllib.quote_plus(channels[key])
            item = xbmcgui.ListItem(key, iconImage = self.icon, thumbnailImage = self.icon)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        else:
          self.showErrorMessage("Wrong file format %s"%playlist)

        xbmcplugin.endOfDirectory(self.handle, True)


    # Helper functions
    def m3u_to_dict(self, playlist):
      channels = {}
      names = []
      streams = []

      f = playlist.replace('%20', ' ')

      for line in file(os.path.join(self.playlists, f)):
        if line.startswith('#EXTM3U'):
          continue

        if line.startswith('#EXTINF'): names.append(line.split(",")[-1].replace("#EXTINF:", "").strip())
        if not line.startswith('#EXTINF'): streams.append(line.strip())

      # correct playlist
      if len(names) == len(streams):
        for i, name in enumerate(names):
          channels[name] = streams[i]

        return channels

      # correct playlist
      else:

        try:
          print len(names)
          print len(streams)
          for i, name in enumerate(names):
            channels[name] = streams[i]
        except:
          print "*** Exception %d %s"%(i, name)

        return channels


    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        print "*** Stream location: " + headers['Location']
        return headers['Location']

player = M3UPlayer()
player.main()
