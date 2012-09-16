#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import urllib, urllib2, sys
import HTMLParser
import CommonFunctions
import simplejson as json

common = CommonFunctions


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def construct_url(mode, url=False, title=False, category=False):
    uri = sys.argv[0] + '?mode=' + mode
    if url: uri += '&url=' + urllib.quote_plus(url)
    if category: uri += '&category=' + category
    if title: uri += '&title=' + title
    return uri

def construct_mp3_url(aid):
    if len(aid) > 0:
        url = "https://api.vk.com/method/audio.getById.json"
        url += "?access_token=cccbeac0c9bf906fc9bf906ff6c991a752cc9bfc9be906709d6d3b8b2d7606d"
        url += "&audios=" + aid        
        return url
    else:
        return ''

def get_mp3_url(aid):
    page = common.fetchPage({"link":  construct_mp3_url(aid)})
    
    if page["status"] == 200:
        song = json.loads(page["content"])["response"][0]
        return song
    else:
        return False
    
def check_url(url):
    if not url.find("rtsp") == -1: # skip rtsp check
        print "*** Skip rtsp check for " + url
        return True
    try:
        response = urllib2.urlopen(url, None, 1)
    except urllib2.HTTPError, e:
        print "***** Oops, HTTPError ", str(e.code)
        return False
    except urllib2.URLError, e:
        print "***** Oops, URLError", str(e.args)
        return False
    except socket.timeout, e:
        print "***** Oops timed out! ", str(e.args)
        return False
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False
    else:
        return True   

# *** Python helpers ***
def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return chr(int(text[3:-1], 16))
				else:
					return chr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			if text[1:-1] == "mdash":
				entity = " - "
			elif text[1:-1] == "ndash":
				entity = "-"
			elif text[1:-1] == "hellip":
				entity = "-"
			else:
				entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return chr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return entity
		return text
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)

#
# def remove(sub, s):  # replace first sub with empty string
#     return s.replace(sub, "", 1)
#
# def remove_all(sub, s):  # replace all sub with empty string
#     return s.replace(sub, "", -1)

def remove_extra_spaces(data):  # Remove more than one consecutive white space
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def uniq(alist):    # Fastest order preserving
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set]

def duration_in_sec(duration):
  time = duration.split(':')
  return int(time[0]) * 60 + int(time[1])

# def uniq(alist):    # Fastest without order preserving
#     set = {}
#     map(set.__setitem__, alist, [])
#     return set.keys()


# def uniq(input):
#   output = []
#   for x in input:
#     if x not in output:
#       output.append(x)
#   return output
