#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2005 Michael "ThorN" Thornton
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# CHANGELOG
# 07/25/2012    0.1     82ndab-Bravo17 Initial release

__version__ = '0.1'
__author__  = 'ThorN, Courgette, 82ndab-Bravo17'

import sys
import time
import b3
import os
import random
import b3.events
import b3.plugin
import string
from b3 import functions
from b3.functions import getModule




#--------------------------------------------------------------------------------------------------
class ArmalobbykickPlugin(b3.plugin.Plugin):
    _maxlobbytime = 300
    _adminlobbyignore = 40
    _playersinlobby = {}
    _kick_message = 'AFK too long in the Lobby.'
    
    
    def onLoadConfig(self):
        try:
            self._maxlobbytime = self.config.getint('settings', 'max_lobby_time')
            self.debug('Max time in lobby : %s' % self._maxlobbytime)
        except:
            pass
        try:
            self._adminlobbyignore = self.config.getint('settings', 'admin_ignore_lobby')
            self.debug('Ignore admin in lobby if level at least: %s' % self._adminlobbyignore)
        except:
            pass
        try:
            self._kick_message = self.config.get('settings', 'kick_message')
            self.debug('Give this message when kicked: %s' % self._kick_message)
        except:
            pass
            
    def onStartup(self):
      
        # get the plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False

        self.registerEvent(b3.events.EVT_PLAYER_SYNC_COMPLETED)
    
    def onEvent(self, event):
        if event.type == b3.events.EVT_PLAYER_SYNC_COMPLETED:
            self.checkplayersinlobby()

    def checkplayersinlobby(self):
        currenttime = time.time()
        for cid,cl in self.console.clients.items():
            if cl.team == b3.TEAM_SPEC:
                lobby_details = self._playersinlobby.get(cid)
                if lobby_details:
                    if lobby_details[0] == cl.name:
                        #if it is the same player check entry time
                        enteredlobby = lobby_details[1]
                        lobbytime = currenttime - enteredlobby
                        self.debug('Player %s has been in the lobby for %s seconds' % (cl.name, lobbytime))
                        if lobbytime >= self._maxlobbytime and cl.maxLevel < self._adminlobbyignore:
                            self.debug('Kick player %s' % cl.name)
                            cl.kick(self._kick_message, 'afk', None)
                            del self._playersinlobby[cid]

                    else:
                        # Different player with same cid
                        self._playersinlobby[cid] = (cl.name, currenttime)
                else:
                    #New player in lobby
                    self._playersinlobby[cid] = (cl.name, currenttime)
            else:
                lobby_details = self._playersinlobby.get(cid)
                if lobby_details:
                    del self._playersinlobby[cid]

        
