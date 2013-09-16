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

from results_db import ResultsDB


class UnifiedSearch():
    def __init__(self):
        self.id = 'plugin.video.unified.search'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.xpath = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.language = self.addon.getLocalizedString
        self.supported_addons = self.get_supported_addons()
        self.database = ResultsDB()

        self.counter = self.addon.getSetting("counter")
        #self.search_id = self.addon.getSetting("search_id")

        self.debug = True

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)
        mode = params['mode'] if 'mode' in params else None
        keyword = params['keyword'] if 'keyword' in params else None

        url = params['url'] if 'url' in params else None
        plugin = params['plugin'] if 'plugin' in params else None

        if mode == 'search':
            self.search(keyword)
        if mode == 'show':
            self.show_search_results()
        if mode == 'reset':
            self.reset()
        if mode == 'activatewindow':
            self.activatewindow(plugin, url)
        elif mode is None:
            self.menu()

    # === XBMC VIEWS
    def menu(self):
        self.log("Supported add-ons: %s" % self.supported_addons)

        uri = self.xpath + '?mode=%s' % "search"
        item = xbmcgui.ListItem("[COLOR=FF00FF00]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        item = xbmcgui.ListItem("%s" % self.language(1003), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, "%s?mode=show" % self.xpath, item, True)

        item = xbmcgui.ListItem("[COLOR=FFFF4000]%s[/COLOR]" % self.language(1001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, self.xpath + '?mode=reset', item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def search(self, keyword):
        keyword = self.get_user_input()
        # keyword = "Princ"

        if keyword:
            # self.log("Search ID: %s" % self.search_id)

            # Generate search ID
            # self.generate_search_id()

            # Reset search results
            self.reset()

            self.log("Call other add-ons and pass keyword: %s" % keyword)
            keyword = translit.eng(keyword) if self.isCyrillic(keyword) else keyword

            for i, plugin in enumerate(self.supported_addons):
                script = "special://home/addons/%s/default.py" % plugin
                xbmc.executebuiltin("XBMC.RunScript(%s, %d, mode=search&keyword=%s&unified=True)" % (script, self.handle, keyword), True)

    def show_search_results(self):
        self.log("Show results on separate page")

        results = self.database.find_all()

        if results:
            for i, item in enumerate(results):
                uri = '%s?mode=activatewindow&plugin=%s&url=%s' % (self.xpath, item['plugin'], item['url'])
                item = xbmcgui.ListItem("%s (%s)" % (item['title'], item['plugin'].replace('plugin.video.', '')), thumbnailImage=item['image'])
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        else:
            item = xbmcgui.ListItem("[COLOR=FFFF4000]%s[/COLOR]" % self.language(1002))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(self.handle, '', item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def previous_searches(self):
        self.log("Show search result")

        results = self.database.find_all()

        if results:
            for i, item in enumerate(results):
                uri = '%s?mode=activatewindow&plugin=%s&url=%s' % (self.xpath, item['plugin'], item['url'])
                item = xbmcgui.ListItem("%s (%s)" % (item['title'], item['plugin'].replace('plugin.video.', '')), thumbnailImage=item['image'])
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
        else:
            item = xbmcgui.ListItem("[COLOR=FFFF4000]%s[/COLOR]" % self.language(1002))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(self.handle, '', item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def activatewindow(self, plugin, url):
        self.log("%s => %s" % (plugin, url))

        window = "plugin://%s/?mode=show&url=%s" % (plugin, url)
        xbmc.executebuiltin('activatewindow(video, %s)' % window)

    # === DATA HANDLING
    def collect(self, results):
        self.log("*** Collect results and activate window")

        self.increase_counter()

        if results:
            for result in results:
                self.database.save(result['title'], result['url'], result['image'], result['plugin'])

        xbmc.sleep(300)

        if len(self.supported_addons) == self.counter:
            self.log("ALL DONE => %s of %d done" % (self.counter, len(self.supported_addons)))
            self.log("Activate show results window")

            xbmc.executebuiltin('XBMC.ReplaceWindow(10025, %s, return)' % "plugin://%s/?mode=show" % (self.id))
        else:
            self.log("Wait and do nothing => %s of %d done" % (self.counter, len(self.supported_addons)))
            return True

    def reset(self):
        self.addon.setSetting("counter", '0')
        self.database.drop()
        xbmc.executebuiltin("Container.refresh()")

    # === HELPERS
    def get_user_input(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            keyword = kbd.getText()

        return keyword

    def get_supported_addons(self):
        request = '{"jsonrpc": "2.0", "method": "Addons.GetAddons", "params": {"properties": ["summary"]}, "id": 1}'

        api_response = json.loads(xbmc.executeJSONRPC(request))
        addons = api_response["result"]["addons"]
        supported_addons = []

        for i, addon in enumerate(addons):
            try:
                if not 'pvr' in addon["addonid"] and xbmcaddon.Addon(addon["addonid"]).getSetting('unified_search') == 'true':
                    supported_addons.append(addon["addonid"])
            except RuntimeError:
                pass

        return supported_addons

    def increase_counter(self):
        self.counter = int(self.counter) + 1 if self.counter else 1
        self.addon.setSetting("counter", str(self.counter))

    def generate_search_id(self):
        self.search_id = int(self.search_id) + 1 if self.search_id else 0
        self.addon.setSetting("search_id", str(self.search_id))

    def log(self, message):
        if self.debug:
            print "=== %s: %s" % ("UnifiedSearch", message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def isCyrillic(self, keyword):
        if not re.findall(u"[\u0400-\u0500]+", keyword):
            return False
        else:
            return True
