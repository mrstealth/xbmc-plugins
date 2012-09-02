#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie
import platform
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon
import httplib
import urllib
import urllib2

import re
try:
	from hashlib import md5
except:
	from md5 import md5

import sys
import os
import Cookie
import subprocess
import keyboardint
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
from urllib import unquote, quote

VERSION = '4.3as'
DOMAIN = '131896016'
UATRACK = 'UA-31027962-1'
conf_file = os.path.join(xbmc.translatePath('special://temp/'), 'settings.stepashka.dat')

__addon__ = xbmcaddon.Addon( id = 'plugin.video.stepashka.com' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

PLUGIN_ID = 'plugin.video.stepashka.com'
PLUGIN_NAME='stepashka.com'

# if not __addon__.getSetting('ga_uid'):
# 	from random import randint
# 	from ga import get_visitor_id
# 	ga_uid = get_visitor_id(str(randint(0, 0x7fffffff)) + PLUGIN_NAME + PLUGIN_ID, None)
# 	__addon__.setSetting('ga_uid', ga_uid)
# 	xbmc.log('[%s] GA uid set to %s' % (PLUGIN_NAME, __addon__.getSetting('ga_uid')))
# 
# if not __addon__.getSetting('GAcookie'):
# 	from random import randint
# 	from ga import get_visitor_id
# 	GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
# 	uniq_id=random.random()*time.time()
# 	__addon__.setSetting('GAcookie', GAcookie)
# if not __addon__.getSetting('uniq_id'):
# 	uniq_id=random.random()*time.time()
# 	print uniq_id
# 	__addon__.setSetting('uniq_id', str(uniq_id))
# 
# GAcookie =__addon__.getSetting('GAcookie')
# uniq_id=__addon__.getSetting('uniq_id')
# ga_uid=__addon__.getSetting('ga_uid')

hos = int(sys.argv[1])
show_len=50


# try:
# 	ver = sys.version_info
# 	ver1 = '%s.%s.%s' % (ver[0], ver[1], ver[2])
# 	osname = '%s %s; %s' % (os.name, sys.platform, ver1)
# 	pyver = platform.python_version()
# 	isXBMC = 'XBMC'
# 	if getattr(xbmc, "nonXBMC", None) is not None:
# 		isXBMC = 'nonXBMC'
# 	UA = '%s/%s (%s; %s) %s/%s stepashka.com/%s user/%s' % (isXBMC, xbmc.getInfoLabel('System.BuildVersion').split(" ")[0], xbmc.getInfoLabel('System.BuildVersion'), osname, __addon__.getAddonInfo('id'), __addon__.getAddonInfo('version'), '0.0.1', str(uniq_id))
# 	xbmc.log('UA: %s' % UA)
# except:
# 	UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))
# 

#print GAcookie
#print uniq_id


# def track_page_view(path,nevent='', tevent=''):
# 	from ga import track_page_view_a
# 	extras = {}
# 	extras['screen'] = xbmc.getInfoLabel('System.ScreenMode')
	#try:
		#track_page_view_a(__addon__.getSetting('ga_uid'), path, UA, extras,tevent) 
	#except:
		#xbmc.log('problems tracking GA')

try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

Addon = xbmcaddon.Addon(id='plugin.video.stepashka.com')
icon    = Addon.getAddonInfo('icon')
siteUrl = 'online.stepashka.com'
httpSiteUrl = 'http://' + siteUrl+'/'
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.stepashka.com.cookies.sid')


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )



def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		#req.add_header('Host',	'online.stepashka.com')
		req.add_header('Accept', '*/*')
		req.add_header('Accept-Language', 'ru-RU')
		req.add_header('Referer',	'http://www.stepashka.com')
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)

def mainScreen(params):
	li = xbmcgui.ListItem('[Поиск]', addon_fanart, addon_icon)
	li.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'func': 'doSearch'
		})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[Последние добавления]', addon_fanart, addon_icon)
	li.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'href': 'http://online.stepashka.com/',
		'func': 'readCategory'
		})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	http = GET(httpSiteUrl)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('ul', attrs={'class': 'lmenu reset'})
	cats=content.findAll('a')
	#print content
	#dat_file = os.path.join(addon_path, 'categories.txt')
	#f = open(dat_file, 'r')
	for line in cats:
		title=None
		if line.string:	title = str(line.string)
		else: title = str(line.find('b').string)
		if title!='None':
			li = xbmcgui.ListItem(title, addon_fanart, addon_icon)
			li.setProperty('IsPlayable', 'false')
			href = line['href']
			uri = construct_request({
				'href': href,
				'func': 'readCategory'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

def doSearch(params):
	li = xbmcgui.ListItem('Искать далее', addon_fanart, addon_icon)
	uri = construct_request({
		'func': 'search2'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)
	
	#track_page_view('search')
	#kbd = xbmc.Keyboard()
	#kbd.setDefault('')
	#kbd.setHeading('Поиск')
	#kbd.doModal()
	out=keyboardint.getRuText()
	xbmc.sleep(1000)
	__addon__.setSetting('querry',str(out))
	#out=quote(out)
	#print out
	#ins='http://online.stepashka.com/?do=search&subaction=search&story='
	#print ins+out
	#params['href'] = ins+out
	#print params
#	readCategory(params)	
	#if kbd.isConfirmed():
	#	sts=kbd.getText();
	#	params['href'] = 'http://online.stepashka.com/?do=search&subaction=search&story=' + sts
	#readCategory(params)	
def search2(params):
	print params
	print __addon__.getSetting('querry')
	params['href'] = 'http://online.stepashka.com/?do=search&subaction=search&story=%s'% quote(__addon__.getSetting('querry'))
	print params['href']
	readCategory(params)	
def readCategory(params, postParams = None):
	#track_page_view(params['href'])
	fimg=None
	try:
		hlink=params['href']+params['page']
		hlink=params['href']
	except:
		hlink=params['href']
	#print hlink
	http = GET(hlink)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
 	content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
	dataRows = beautifulSoup.findAll('div', attrs={'class': 'base shortstory'})
	#print dataRows
	if len(dataRows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in dataRows:
			sec=0
			if link != None:
				title = link.find('a').string
				if sec==1:
					sec=0
				else:
					sec=1
					href = link.find('a')['href']

					#print link
					fimg=link.find('img')
					try:
						li = xbmcgui.ListItem('[%s]' % title, addon_icon, fimg['pagespeed_lazy_src'])
					except: pass
					try:	
						li = xbmcgui.ListItem('[%s]' % title, addon_icon, fimg['src'])
					except: li = xbmcgui.ListItem('[%s]' % title, addon_icon, addon_icon)	
					li.setProperty('IsPlayable', 'false')
					uri = construct_request({
						'title': title,
						'href': href,
						'func': 'readFile',
						'page': href,
						'src': fimg['src']
						})
					xbmcplugin.addDirectoryItem(hos, uri, li, True)
	try:
		dataRows1 = beautifulSoup.find('div', attrs={'class': 'navigation'})
		dataRows = dataRows1.findAll('a')
	#print dataRows
		if len(dataRows) == 0:
			showMessage('ОШИБКА', 'Неверная страница', 3000)
			return False
		else:
			for link in dataRows:
				href = link['href']
				title = link.string
				li = xbmcgui.ListItem('[%s]' % title, addon_icon, addon_icon)
				li.setProperty('IsPlayable', 'false')
				uri = construct_request({
					'title': title,
					'href': href,
					'page': link['href'],
					'func': 'readCategory',
					})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)
	except: pass
	xbmcplugin.endOfDirectory(hos)

def readFile(params):
	http = GET(params['href'])
	#print params['href']
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('param', attrs={'name': 'flashvars'})
	#print content
	findfile=str(content)
	#print findfile
	pat=re.compile('http://[a-zA-Z0-9-_.!/]+.flv', re.S)
	pat_pl=re.compile('pl=http://[a-zA-Z0-9-_.!/]+.flv', re.S)
	mfil = pat.findall(findfile)
	pfil = pat_pl.findall(findfile)
	if mfil: print mfil
	if pfil: print pfil
	vurl=findfile.split('&')
	for ur in vurl:	findfile=ur
	vurl=findfile.split('"')
	lurl=vurl[0]
	if mfil: 
		#print 'play file ' + mfil[0]
		li = xbmcgui.ListItem(params['title'], addon_icon, params['src'])
		li.setProperty('IsPlayable', 'true')
		uri = construct_request({
			'func': 'play',
			'file': mfil[0]
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, False)
	else: 
		#print 'playlist in ' + lurl.split('=')[1]
		http = GET(lurl.split('=')[1])
		#print http
		f=http.find('{')
		http=http[f:len(http)]
		try:
			jsdata=json.loads(http)
		except:
			f1=http.rfind(']}')
			http=http[0:f1-1]
			jsdata=json.loads(http)
		#print jsdata
		has_sesons=False
		playlist = jsdata['playlist']
		#print playlist
		for file in playlist:
			#print file
			try:
				li = xbmcgui.ListItem(file['comment'], addon_icon, params['src'])
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'func': 'play',
					'file': file['file']
					})
				xbmcplugin.addDirectoryItem(hos, uri, li, False)
			except: pass
			try:
				for t in file['playlist']:
				#print t
					li = xbmcgui.ListItem(t['comment'], addon_icon, params['src'])
					li.setProperty('IsPlayable', 'true')
					uri = construct_request({
						'func': 'play',
						'file': t['file']
						})
					has_sesons=True
					xbmcplugin.addDirectoryItem(hos, uri, li, False)
				if has_sesons==False:
					li = xbmcgui.ListItem(file['comment'], addon_icon, params['src'])
					li.setProperty('IsPlayable', 'true')
					uri = construct_request({
						'func': 'play',
						'file': file['file']
						})
					xbmcplugin.addDirectoryItem(hos, uri, li, False)
			except: pass
	xbmcplugin.endOfDirectory(hos)

	
def geturl(url):
	f = None
	url=url[1:len(url)]
	myhttp = 'http://fcsd.tv/ru/xmlinfo/?idv=%s' % url
	http = GET('http://fcsd.tv/ru/xmlinfo/?idv=%s' % url)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	furl=beautifulSoup.find('video')
	f=furl.find('hq')
	if not f: f=furl.find('rq')
	return f['url']

def play(params):
	#track_page_view('','event','5(Video*Videostart)')
	i = xbmcgui.ListItem(path = params['file'])
	xbmcplugin.setResolvedUrl(hos, True, i)
	
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		mainScreen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
