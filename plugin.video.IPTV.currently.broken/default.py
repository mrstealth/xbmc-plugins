#!/usr/bin/python
# -*- coding: utf-8 -*-

# *      Copyright (C) 2011 TDW
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */

import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib, xbmcaddon
def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
	
handle = int(sys.argv[1])

PLUGIN_NAME   = 'IPTV'

addon = xbmcaddon.Addon(id='plugin.video.IPTV')

dc={"1 канал" : "001", "1+1" : "002"}
try:
	from canal_list import*
except:
	pass

thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
LstDir = os.path.join( addon.getAddonInfo('path'), "playlists" )
ImgPath = os.path.join( addon.getAddonInfo('path'), "logo" )
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

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

def ShowRoot():
	RootList=os.listdir(LstDir)
	for tTitle in RootList:
		row_url = "row_url"
		Title = os.path.splitext(tTitle)[0]#' Title '
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		if 1 == 1:
			purl = sys.argv[0] + '?mode=OpenCat'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def open_pl(pl_name):
	line=""
	Lurl=[]
	Ltitle=[]
	Lnum=[]
	tvlist = os.path.join(LstDir, pl_name+'.m3u')
	fl = open(tvlist, "r")
	n=0
	for line in fl.xreadlines():
		n+=1
		if len(line)>5:
			pref=line[:5]
			if pref=="#EXTI":
				lpr=line.find(',')+1
				tmp=line[lpr:]
				if tmp[:1]==" ":Ltitle.append(line[lpr+1:])
				else: Ltitle.append(line[lpr:])
			#if pref=="MMS:" or pref=="HTTP:" or pref=="http:" or pref=="mms:/" : Lurl.append(line)
			#if pref[0]<> "#"and n>1: Lurl.append(line[:-1])
			if pref[0]<> "#"and n>1: 
				Lurl.append(ru(line).replace(u'\n','').replace(u'\r',''))
				Lnum.append(len(Lurl)-1)
	fl.close()
	return (Ltitle, Lurl, Lnum)

def formating(str):
	str=str.strip()
	str=str.replace('\n','').replace('\r','')
	str=str.replace(' +1','').replace(' +2','').replace(' +3','').replace(' +4','').replace(' +5','').replace(' +6','').replace(' +7','').replace(' -1','').replace(' -2','').replace(' -3','').replace(' -4','').replace(' -5','').replace(' -6','').replace(' -7','')
	str=str.replace('-',' ').replace('  ',' ')
	str=xt(str).lower()
	str=str.replace('Й','й')
	str=str.replace('Ц','ц')
	str=str.replace('У','у')
	str=str.replace('К','к')
	str=str.replace('Е','е')
	str=str.replace('Н','н')
	str=str.replace('Г','г')
	str=str.replace('Ш','ш')
	str=str.replace('Щ','щ')
	str=str.replace('З','з')
	str=str.replace('Х','х')
	str=str.replace('Ъ','ъ')
	str=str.replace('Ф','ф')
	str=str.replace('Ы','ы')
	str=str.replace('В','в')
	str=str.replace('А','а')
	str=str.replace('П','п')
	str=str.replace('Р','р')
	str=str.replace('О','о')
	str=str.replace('Л','л')
	str=str.replace('Д','д')
	str=str.replace('Ж','ж')
	str=str.replace('Э','э')
	str=str.replace('Я','я')
	str=str.replace('Ч','ч')
	str=str.replace('С','с')
	str=str.replace('М','м')
	str=str.replace('И','и')
	str=str.replace('Т','т')
	str=str.replace('Ь','ь')
	str=str.replace('Б','б')
	str=str.replace('Ю','ю')
	return str

def gettbn(Title):
		thumb2 = xbmc.translatePath(os.path.join(ImgPath, Title[:-2]+'.png'))
		if os.path.isfile(thumb2)==0:
			thumb2 = os.path.join(ImgPath, Title[:-1]+'.png')
			if os.path.isfile(thumb2)==0:thumb2=thumb
			thumb3 = ru(os.path.join(ImgPath, Title[:-1]+'.png'))
			if os.path.isfile(thumb3)==1:thumb2=thumb3
			thumb4 = os.path.join(ImgPath, dc.get(xt(Title), ' ')+'.png')
			if os.path.isfile(thumb4)==1:thumb2=thumb4
		return thumb2


def OpenCat(url, name):
	Ltitle, Lurl, Lnum = open_pl(name)
	lgl=(Ltitle, Lurl, Lnum)
	for i in range (len(Ltitle)):
		Title = formating(Ltitle[i])
		thumb2 = gettbn(Title)
		row_name = Ltitle[i]
		#row_name = str(Lnum[i])+". "+Ltitle[i]
		row_url = Lurl[i]
		Plot  = ' Plot: '
		Genre = ' Genre: '
		listitem = xbmcgui.ListItem(row_name, thumbnailImage=thumb2 )
		#listitem.setInfo(type = "Video", infoLabels = {
		#	"Title": 	row_name,
		#	"Studio": 	row_url,
		#	"Plot": 	Plot,
		#	"Genre": 	Genre })
		listitem.setProperty('fanart_image',fanart)
		purl = sys.argv[0] + '?mode=OpenPage'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&fanart_image=' + urllib.quote_plus(fanart)\
			+ '&num=' + urllib.quote_plus(str(Lnum[i]))\
			+ '&lgl=' + urllib.quote_plus(repr(lgl))\
			+ '&title=' + urllib.quote_plus(Ltitle[i])
		xbmcplugin.addDirectoryItem(handle, purl, listitem, False)



def OpenPage(url, name, num, Lgl):
	Ltitle, Lurl, Lnum = Lgl
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	for i in range(num,len(Lnum)):
		thumb2 = gettbn(formating(Ltitle[i]))
		item = xbmcgui.ListItem(Ltitle[i], iconImage = fanart, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels={"Title": Ltitle[i]})
		playlist.add(url=Lurl[i], listitem=item, index=-1)
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)#(url, item) 

	for i in range(0,num):
		thumb2 = gettbn(formating(Ltitle[i]))
		item = xbmcgui.ListItem(Ltitle[i], iconImage = fanart, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels={"Title": Ltitle[i]})
		playlist.add(url=Lurl[i], listitem=item, index=-1)



params = get_params()
mode  = None
url   = ''
title = ''
ref   = ''
img   = ''
num   = 0
Lgl   = ()
try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass

try:
	url  = urllib.unquote_plus(params["url"])
except:
	pass

try:
	title  = urllib.unquote_plus(params["title"])
except:
	pass
try:
	img  = urllib.unquote_plus(params["img"])
except:
	pass
try:
	num  = int(urllib.unquote_plus(params["num"]))
except:
	pass
try:
	Lgl  = eval(urllib.unquote_plus(params["lgl"]))
except:
	pass


if mode == None:
	ShowRoot()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenCat':
	OpenCat(url, title)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenPage':
	OpenPage(url, title, num, Lgl)


try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass