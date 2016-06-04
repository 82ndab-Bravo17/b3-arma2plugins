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
# 09/12/2015    0.1     82ndab-Bravo17 Initial release

__version__ = '0.1'
__author__  = 'ThorN, Courgette, 82ndab-Bravo17'

import sys
import time
import b3
import random
import b3.events
import b3.plugin
import b3.cron
import string
import re
import zlib
from b3 import functions
from b3.functions import getModule




#--------------------------------------------------------------------------------------------------
class ArmaremoveautobansPlugin(b3.plugin.Plugin):

    def onStartup(self):
      
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        self._cronTab = b3.cron.PluginCronTab(self, self.remove_auto_bans, minute='*/5')
        self.console.cron + self._cronTab
        self.info('Automatic Bans Removal update has been enabled')

    def onLoadConfig(self):
        if self.config is None:
            return

    def remove_auto_bans(self):
        self.debug('Retrieving Ban List from Server')
        banlist = self.console.getBanlist()
        if len(banlist) == 0:
            return
        self.debug('Banlist is %s' % banlist)
        for ban_entry in banlist.keys():
            if 'EpochMod.com Autoban' in banlist[ban_entry]['reason']:
                self.debug('Epoch Auto Ban for %s has been removed' % banlist[ban_entry]['guid'])
                self.console.write(self.console.getCommand('unban', ban_no=banlist[ban_entry]['ban_index'], reason='Remove Epoch Autoban'))
        self.console.write(('writeBans',))