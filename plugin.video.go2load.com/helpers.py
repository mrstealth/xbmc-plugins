#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import urllib, sys
import HTMLParser

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
