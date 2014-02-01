import os
import sys
import urllib2


sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import XbmcHelpers
common = XbmcHelpers

from pytube import YouTube
yt = YouTube()


# <openSearch:totalResults>25</openSearch:totalResults>

class YouTubeParser():
    # def parse(self, url):
    #     print "Youtube URL %s" % url

    #     if 'list=' in url:
    #       print "Youtube playlist link found"
    #       self.watch_urls(url)
    #     elif 'watch' in url:
    #       print "Youtube media link found"

    # def watch_urls(self, url):
    #     # "http://www.youtube.com/list_ajax?action_get_list=1&style=xml&list=%s" % vids[i]

    #     playlist_id = url.split('list=')[-1]
    #     max_count = 5

    #     playlist_url = "http://gdata.youtube.com/feeds/api/playlists/%s?max-results=%d" % (playlist_id, max_count)
    #     #response = common.fetchPage(playlist_url)
    #     response = urllib2.urlopen(playlist_url).read()
    #     entries = common.parseDOM(response, 'entry')

    #     titles = common.parseDOM(entries, 'media:title')
    #     links = common.parseDOM(entries, 'media:player', ret='url')

    #     print len(titles)
    #     print len(links)

    #     print titles
    #     print links

    #     self.play_url(links[0])

    # def play_url(self, url):
    #     url = "http://www.youtube.com/embed/A-UgPsiNdMI%3Ffeature=player_detailpage"
    #     # url = "http://www.youtube.com/watch?v=A-UgPsiNdMI&amp;feature=youtube_gdata_player"
    #     yt.url = url
    #     video_url = yt.videos[-1].url

    #     print "VIDEO LINK FOUND %s" % video_url
    #     print video_url
    #     # return links

    def playlist_links(self, pid):
        max_count = 50

        playlist_url = "http://gdata.youtube.com/feeds/api/playlists/%s?max-results=%d" % (pid, max_count)
        print "Playlist: %s" % playlist_url

        response = urllib2.urlopen(playlist_url).read()
        entries = common.parseDOM(response, 'entry')

        videos = {}

        titles = common.parseDOM(entries, 'media:title')
        links = common.parseDOM(entries, 'media:player', ret='url')

        for i, link in enumerate(links):
            title = titles[i].split(' : ')[-1]
            videos[title] = link

        return videos




    def video_links(self, vid):
        print "Get links for YouTube url %s" % vid
        yt.url = "http://www.youtube.com/watch?v=%s" % vid
        video_url = yt.videos[-1].url
        return video_url

    def playable_link(self, url):
        yt.url = url
        return yt.videos[-1].url
