import sys
import json
import urllib
import re

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import XbmcHelpers
common = XbmcHelpers

import Translit as translit
translit = translit.Translit()



class UnifiedSearch():
    def __init__(self):
        self.id = 'plugin.video.unified.search'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.xpath = sys.argv[0]
        self.handle = int(sys.argv[1])

        self.language = self.addon.getLocalizedString
        self.supported_addons = self.get_supported_addons()
        self.debug = False

    def main(self):
        self.log("\nAddon: %s \nHandle: %s\nParams: %s " % (sys.argv[0], sys.argv[1], sys.argv[2]))

        params = common.getParameters(sys.argv[2])
        mode = params['mode'] if 'mode' in params else None
        keyword = params['keyword'] if 'keyword' in params else None

        url = params['url'] if 'url' in params else None
        plugin = params['plugin'] if 'plugin' in params else None

        if mode == 'search':
            self.search(keyword)
        if mode == 'reset':
            self.resetResults()
        if mode == 'activatewindow':
            self.activatewindow(plugin, url)
        elif mode is None:
            self.menu()

    def menu(self):
        self.log("Supported add-ons: %s" % self.supported_addons)

        uri = self.xpath + '?mode=%s' % "search"
        item = xbmcgui.ListItem("[COLOR=FF00FF00]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, self.xpath + '?mode=reset', item, False)

        for i, item in enumerate(self.getSearchResults()):
            uri = '%s?mode=activatewindow&plugin=%s&url=%s' % (self.xpath, item['plugin'], item['url'])

            item = xbmcgui.ListItem("%s (%s)" % (item['title'], item['plugin'].replace('plugin.video.', '')), thumbnailImage=item['image'])
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
                keyword = kbd.getText()

                # reset results
                self.addon.setSetting("results", "")

        return keyword

    def search(self, keyword):
        keyword = self.getUserInput()

        if keyword:
            self.log("Call other add-ons and pass keyword: %s" % keyword)

            item = xbmcgui.ListItem("Please wait ...", thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, sys.argv[0], item, False)

            # Check if keyword is cyrillic
            keyword = translit.eng(keyword) if self.isCyrillic(keyword) else keyword

            # Send keyword to supported add-ons
            for i, plugin in enumerate(self.supported_addons):
                script = "special://home/addons/%s/default.py" % plugin
                xbmc.executebuiltin("XBMC.RunScript(%s, %d, mode=unified_search&keyword=%s)" % (script, self.handle, keyword))

        # xbmcplugin.endOfDirectory(self.handle, True)

    def activatewindow(self, plugin, url):
        self.log("%s => %s" % (plugin, url))

        window = "plugin://%s/?mode=show&url=%s" % (plugin, url)
        xbmc.executebuiltin('activatewindow(video, %s)' % window)
        # xbmcplugin.endOfDirectory(self.handle, True)

    # === RESULTS handling
    def collect(self, results):
        self.log("Save results to DB %s" % results)
        
        if results:
            self.saveSearchResults(results)            
        
        xbmc.executebuiltin("Container.Update(plugin://%s,replace)" % self.id)
        xbmcplugin.endOfDirectory(self.handle, True)
    
    def getSearchResults(self):
        self.log("Get search results from storage")

        try:
            results = json.loads(self.addon.getSetting("results"))
            return results
        except ValueError:
            return []

    def saveSearchResults(self, results):
        self.log("Save search rsults in settings %s" % (results))

        for result in results:
            try:
                saved = self.getSearchResults()


                if not result['url'] in map(lambda item: item['url'], saved):
                    saved.append(result)
                    self.addon.setSetting("results", json.dumps(saved))
            except Exception, e:
                self.error(e)

    def resetResults(self):
        self.addon.setSetting("results", "")
        xbmc.executebuiltin("Container.refresh()")

    # === HELPERS
    def get_supported_addons(self):
        request = '{"jsonrpc": "2.0", "method": "Addons.GetAddons", "params": {"properties": ["summary"]}, "id": 1}'

        response = json.loads(xbmc.executeJSONRPC(request))["result"]["addons"]
        supported = []

        for i, addon in enumerate(response):
            try:
                if not 'pvr' in addon["addonid"] and xbmcaddon.Addon(addon["addonid"]).getSetting('unified_search') == 'true':
                    supported.append(addon["addonid"])
            except RuntimeError:
                pass

        return supported

    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def isCyrillic(self, keyword):
        if not re.findall(u"[\u0400-\u0500]+", keyword):
            return False
        else:
            return True
