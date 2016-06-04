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

import os
import b3
import b3.events
import b3.plugin
import b3.cron
import string
from b3 import functions
from b3.functions import getModule
from b3 import clients




#--------------------------------------------------------------------------------------------------
class ArmasteamidPlugin(b3.plugin.Plugin):
    _server_log_name = ''
    _server_log_path = ''
    _latest_log = ''
    _latest_size = 0
    _log_ptr = 0
    _crontab = None
    _last_log_read = ''

    def onLoadConfig(self):
        if self.config.has_option('settings', 'server_log_name'):
            self._server_log_name = self.config.get('settings', 'server_log_name')
            self.debug("Using %s for server log filename pattern" % self._server_log_name)
            if self._server_log_name.endswith('.log'):
                self._server_log_name = self._server_log_name[0:-4]
        else:
            self.debug("No server log given, Arma IDs will not be saved")

        if self.config.has_option('settings', 'server_log_path'):
            self._server_log_path = self.config.getpath('settings', 'server_log_path')
            self._server_log_path = self._server_log_path.lower()
            self.debug("Using %s for server log path" % self._server_log_path)
        else:
            self.debug("No server log path given, Arma IDs will not be saved")

    def onStartup(self):
        # get the plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
            
        self._cronTab = b3.cron.PluginCronTab(self, self.get_arma_ids,  minute='*/1')
        self.console.cron + self._cronTab

    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        return
        
    def get_arma_ids(self):
        """
        9:00:55 BattlEye Server: Player #1 playername (68.46.21.245:2304) connected
        9:00:55 Player playername connecting.
        9:00:57 BattlEye Server: Player #1 playername - GUID: 79f4f7f1b8ca86afe3d5c1df11111111 (unverified)
        9:00:57 Player playername connected (id=76561198011111111).
        9:00:57 BattlEye Server: Verified GUID (79f4f7f1b8ca86afe3d5c1df11111111) of player #1 playername
        
        """
        self.debug("Starting Arma ID search")
        players = {}
        self._latest_log, latest_size = self.get_latest_logname()
        if (self._last_log_read != self._latest_log):
            self._log_ptr = 0
            self._last_log_read = self._latest_log
        if latest_size == 0:
            # self.debug('No data to read')
            return
        self.debug('Latest log file is %s which is %s bytes'  % (self._latest_log, latest_size))
        # Check file exists
        if os.path.isfile(self._latest_log):
            try:
                f = file(self._latest_log, 'r')
                loglines = f.readlines()
            except:
                self.error('Error reading server log file: %s', f)
                return
        else:
            self.error('Server log file not found: %s', f)
            return
        f.close()
        logline = 0
        for line in loglines:
            logline += 1
            if logline >= self._log_ptr:
                line = line.strip()
                time, sep, lineinfo = line.partition(' ')
                if lineinfo.endswith('connected'):
                    playername, slot_no = self.get_name(lineinfo)
                    players[slot_no] = {'Playername': playername}
                    # self.debug('Player connected: %s in slot %s' % (playername, slot_no))
                elif lineinfo.endswith('(unverified)'):
                    slot_no, playername, playerguid = self.get_guid(lineinfo)
                    if players[slot_no]['Playername'] == playername:
                        players[slot_no]['GUID'] = playerguid
                        # self.debug('Player %s in slot %s has unverified guid %s' % (playername, slot_no, playerguid))
                elif 'connected (id=' in lineinfo:
                    playername, playerarmaid = self.get_arma_id(lineinfo)
                    # self.debug('Player %s has Arma id %s' % (playername, playerarmaid))
                    # self.debug(players)
                    for p in players.keys():
                        if players[p]['Playername'] == playername:
                            players[p]['Arma_id'] = playerarmaid
                            
                elif lineinfo.startswith('BattlEye Server: Verified GUID ('):
                    slot_no, playername, checkguid = self.check_guid(lineinfo)
                    if checkguid != '':
                        # self.debug('Player %s in slot %s has confirmed guid %s' % (playername, slot_no, checkguid))
                        if players[slot_no]['Playername'] == playername and players[slot_no]['GUID'] == checkguid:
                            self.debug('%s has guid %s and Arma id %s' % (players[slot_no]['Playername'], players[slot_no]['GUID'], players[slot_no]['Arma_id']))
                            self.update_arma_id(checkguid, players[slot_no]['Arma_id'], playername)
                            del players[slot_no]
                    else:
                        # Player is an HC, or no verified GUID
                        del players[slot_no]
        self._log_ptr = logline
                
    def get_name(self, data):
        data = data.partition('#')[2]
        slot, sep, data = data.partition(' ')
        slot = str(slot)
        name = data.rpartition(' (')[0]
        return name, slot

    def get_guid(self, data):
        data = data.partition('#')[2]
        slot, sep, data = data.partition(' ')
        slot = str(slot)
        name, sep, data = data.rpartition(' - GUID: ')
        guid = data.rpartition(' ')[0]
        return slot, name, guid
        
    def get_arma_id(self, data):
        data = data.partition(' ')[2]
        name, sep, data = data.partition(' connected (id=')
        armaid = data.rpartition(')')[0]
        return name, armaid
        
    def check_guid(self, data):
        data = data.partition('(')[2]
        guid, sep, data = data.partition(') of player #')
        slot, sep, name = data.partition(' ')
        slot = str(slot)
        return slot, name, guid
        
    

    def get_latest_logname(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self._server_log_path):
            files.extend(filenames)
            break
        latesttime = 0
        latestlog = ''
        latestsize = 0
        for file in files:
            filelower = file.lower()
            if filelower.endswith('.log') and filelower.startswith(self._server_log_name):
                fullfilename = self._server_log_path + '/' + file
                self.debug('Checking file %s' % fullfilename)
                filestats = os.stat(fullfilename)
                if filestats.st_ctime > latesttime:
                    latestlog = file
                    latesttime = filestats.st_ctime
                    latestsize = filestats.st_size
        if latestlog == '':
            self.error('No valid log file found')
        latestlog = self._server_log_path + '/' + latestlog
        # self.debug('Latest log file is %s' % latestlog)
        return latestlog, latestsize
                    
                
    def update_arma_id(self, guid, armaid, name):
        try:
            q = ('SELECT * FROM clients WHERE guid = "%s"' % guid)
            cursor = self.console.storage.query(q)
            if (cursor.rowcount == 1):
                if not cursor.EOF:
                    r = cursor.getRow()
                    # self.debug('client found %s' % r['name'])
                    if (r['name'] == name):
                        if (r['pbid'] != armaid):
                            q = ('UPDATE clients SET pbid = "%s" WHERE guid = "%s"' % (armaid, guid))
                            cursor2 = self.console.storage.query(q)
                            self.debug('Arma Steam id updated for %s' % name)
                        else:
                            self.debug('Arma Steam id does not need updating for %s' % name)
                    else:
                        self.error('Error, player %s clients name has changed' % name)
                else:
                    self.error('Error, player %s not found in clients table' % name)
            elif  (cursor.rowcount > 1):
                self.error('Too many clints with same guid')
            else:
                self.error('No results returned from Clients table for guid %s' % guid)
        except Exception:
            # self.debug('Error getting client info')
            raise
