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

import b3
import b3.events
import b3.plugin
import string
from b3 import functions
from b3.functions import getModule




#--------------------------------------------------------------------------------------------------
class ArmabecharkickPlugin(b3.plugin.Plugin):
    _kick_message = 'Please remove all %s characters from your name.'
    _badbenamechars = "|%^&*#@!"
    
    def onLoadConfig(self):
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

        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
    
    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if not event.client:
            return
        elif event.client.cid is None:
            return
        elif not event.client.connected:
            return

        if event.type == self.console.getEventID('EVT_CLIENT_AUTH'):
            self.checkplayername(event.client)
            
    def checkplayername(self, client):
        if not client.connected:
            self.debug('Client not connected?')
            return
        self.info("Checking '%s' for badchars" % client.name)
        
        for c in self._badbenamechars:
            if c in client.name:
                self.debug('Kick player %s for bad char %s in name' % (client.name, c))
                kick_message = self._kick_message % self._badbenamechars
                client.kick(kick_message, ' ' , None)

