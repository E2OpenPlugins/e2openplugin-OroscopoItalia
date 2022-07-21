# -*- coding: iso-8859-1 -*-

##############################################################################
#                          <<< Oroscopo Italia >>>                           
#                                                                            
#                     (2011) meo <lupomeo@hotmail.com>          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################

#
# Oroscopo Italia da
# www.horoscopofree.com
#
# Author: meo
# Graphics: Army
#

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap

from six.moves.urllib.request import Request, urlopen
from xml.dom import minidom, Node
from enigma import eTimer

from six.moves.urllib.error import URLError, HTTPError


OROSCOPOITALIA_ABOUT_TXT = "Oroscopo Italia v 0.1\n\nAuthor: meo\nGraphics: Army\nRss Oroscopo: www.horoscopofree.com\n\n\nNota dell'autore: Ho fatto questo plugin su richiesta ma secondo me l'oroscopo e' una gran pirlata!"

class oroscopoMain(Screen):
	skin = """
	<screen position="center,center" size="700,550" flags="wfNoBorder">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OroscopoItalia/backg.png" position="0,0" size="700,550" alphatest="on" />
		<widget name="lab1" position="10,110" halign="center" size="680,30" zPosition="1" font="Regular;24" valign="top" transparent="1" />
		<widget name="lab2" position="10,140" halign="center" size="680,30" zPosition="1" font="Regular;26" valign="top" transparent="1" />
		<widget name="lab3" position="319,180" size="62,62" zPosition="1" />
		<widget name="lab4" position="50,280" halign="center" size="600,270" zPosition="1" font="Regular;22" valign="top" transparent="1" />
		
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self["lab1"] = Label("Attendere prego, connessione al server in corso...")
		self["lab2"] = Label("")
		self["lab3"] = Pixmap()
		self["lab4"] = Label("")

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.key_red,
			"green": self.key_green,
			"back": self.close,
			"ok": self.close
		})

		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.startConnection)
		self.onShow.append(self.startShow)
		self.onClose.append(self.delTimer)


#We use a timer to show the Window in the meanwhile we are connecting to Server
	def startShow(self):
		self["lab1"].setText("Attendere prego, connessione al server in corso...")
		self.activityTimer.start(10)
		
	def startConnection(self):
		self.activityTimer.stop()
		self.updateInfo()

#We will use this for callbacks too
	def updateInfo(self):
		myurl = "http://www.horoscopofree.com/it/misc/partnership/Oroscopo.xml"
		req = Request(myurl)
		try:
			handler = urlopen(req)
		except HTTPError as e:
			maintext = "Error: connection failed !"
		except URLError as e:
			maintext = "Error: Page not available !"
		else:
			xml_response = handler.read()
			#xml_response = handler.read().decode('iso-8859-1').encode('utf-8')
			xml_response = self.checkXmlSanity(xml_response.decode('utf-8'))
			dom = minidom.parseString(xml_response)
			handler.close()
			
			maintext = ""
			if (dom):

				zsign_items = ('title', 'description', 'pubDate')
				zodiac = []

				for zsign in dom.getElementsByTagName('item'):
					tmp_zsign = {}
					for tag in zsign_items:
						tmp_zsign[tag] = zsign.getElementsByTagName(tag)[0].firstChild.nodeValue
					zodiac.append(tmp_zsign)

				dom.unlink()

				idx = self.get_Idx()

				mytime =  str(zodiac[idx]['pubDate'])
				parts = mytime.strip().split(" ")
				mytime = parts[1] + " " + parts[2] + " " + parts[3]

				maintext = "Oroscopo di oggi " + mytime
				title = str(zodiac[idx]['title'])
				self["lab2"].setText(title)

				icon = title.lower()
				icon = pluginpath + "/" + "icons/" + icon[0:3] + ".png"
				png = LoadPixmap(icon)
				self["lab3"].instance.setPixmap(png)

				description = str(zodiac[idx]['description'])
				pos = description.find('<a')
				description = description[0:pos]

				self["lab4"].setText(description)

			else:
				maintext = "Error getting XML document!"

		self["lab1"].setText(maintext)

# Make text safe for xml parser (Google old xml format without the character set declaration)
	def checkXmlSanity(self, content):
		content = content.replace('à', 'a')
		content = content.replace('è', 'e')
		content = content.replace('é', 'e')
		content = content.replace('i', 'i')
		content = content.replace('o', 'o')
		content = content.replace('u', 'u')
		return content

	def get_Idx(self):
		idx = 0
		cfgfile = pluginpath + "/" + "oroscopoitalia.cfg"
		if fileExists(cfgfile):
			f = open(cfgfile, 'r')
			line = f.readline()
			idx = int(line.strip())
			f.close()
		return idx

	def delTimer(self):
		del self.activityTimer

	def key_green(self):
		box = self.session.open(MessageBox, OROSCOPOITALIA_ABOUT_TXT, MessageBox.TYPE_INFO)
		box.setTitle(_("Informazioni"))
		
	def key_red(self):
		self.session.openWithCallback(self.updateInfo, oroscopoSelectsign)

class oroscopoSelectsign(Screen):
	skin = """
	<screen position="center,center" size="700,550" flags="wfNoBorder">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OroscopoItalia/backg.png" position="0,0" size="700,550" alphatest="on" />
		<widget source="list" render="Listbox" position="50,110" zPosition="1" size="600,300" scrollbarMode="showOnDemand" transparent="1" >
			<convert type="StringList" />
		</widget>
		<widget name="lab1" position="50,500" halign="center" size="600,30" zPosition="1" font="Regular;24" valign="top" foregroundColor="#639ACB" transparent="1" />
	</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = [("ARIETE", 0), ("TORO", 1), ("GEMELLI", 2), ("CANCRO", 3), ("LEONE", 4), ("VERGINE", 5),
			("BILANCIA", 6), ("SCORPIONE", 7), ("SAGITTARIO", 8), ("CAPRICORNO", 9), ("ACQUARIO", 10), ("PESCI", 11)]

		self["list"] = List(self.list)
		self["lab1"] = Label("Ok per confermare")

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"ok": self.saveCfg,
			"green": self.key_green
		})

	def key_green(self):
		box = self.session.open(MessageBox, OROSCOPOITALIA_ABOUT_TXT, MessageBox.TYPE_INFO)
		box.setTitle(_("Informazioni"))

	def saveCfg(self):
		sign = self["list"].getCurrent()
		if sign:
			cfgfile = pluginpath + "/" + "oroscopoitalia.cfg"
			out = open(cfgfile, "w")
			out.write(str(sign[1]))
		self.close()

def main(session, **kwargs):
	session.open(oroscopoMain)	

def Plugins(path,**kwargs):
	global pluginpath
	pluginpath = path
	return PluginDescriptor(name="Oroscopo Italia", description="Oroscopo di oggi", icon="oroscopoitalia.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
