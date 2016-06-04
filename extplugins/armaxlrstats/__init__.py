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
import re
from b3 import functions
from b3.functions import getModule
from b3 import clients
from time import strftime
from b3.clients import Group


#--------------------------------------------------------------------------------------------------
class ArmaxlrstatsPlugin(b3.plugin.Plugin):
    _server_rpt_name = ''
    _server_rpt_path = ''
    _latest_rpt = ''
    _latest_size = 0
    _rpt_ptr = 0
    _crontab = None
    _last_rpt_read = ''
    _aitypes = {}
     # "[xlrstats] victim: '%1' killer: '%2' weapon: '%3' distance: '%4'", _victimName, _killerName, _weapon, _distance]
     # "[xlrstats] victim: 'COL.Bravo17' killer: 'AI' weapon: 'l85a2_epoch' distance: '80.4631'"
    _killFormat = re.compile(   r'^"\[xlrstats\] victim: \''
                                r'(?P<victim>.*)'
                                r'\' killer: \''
                                r'(?P<killer>.*)'
                                r'\' weapon: \''
                                r'(?P<weapon>.*)'
                                r'\' distance: \''
                                r'(?P<distance>.*)\'"', re.IGNORECASE)
                                
                                

    def onLoadConfig(self):
        if self.config.has_option('settings', 'server_rpt_name'):
            self._server_rpt_name = self.config.get('settings', 'server_rpt_name')
            self.debug("Using %s for server rpt filename pattern" % self._server_rpt_name)
            if self._server_rpt_name.endswith('.rpt'):
                self._server_rpt_name = self._server_rpt_name[0:-4]
        else:
            self.debug("No server rpt given, xlrstats stats will not be saved")

        if self.config.has_option('settings', 'server_rpt_path'):
            self._server_rpt_path = self.config.getpath('settings', 'server_rpt_path')
            self.debug("Using %s for server rpt path" % self._server_rpt_path)
        else:
            self.debug("No server rpt path given, Arma IDs will not be saved")
            
        try:
            if 'xlr_ai_types' in self.config.sections():
                for ai in self.config.options('xlr_ai_types'):
                    self._aitypes[ai] = self.config.get('xlr_ai_types', ai)
                    self.debug('AI type %s : %s' % (ai, self._aitypes[ai]))
        except Exception, err:
            self.error('Error getting AI types "%s" : %s' % (Exception, err))

    def onStartup(self):
        # get the plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False

        self.console.game.mapName = self.getMissionName()

        self._cronTab = b3.cron.PluginCronTab(self, self.get_xlrstats,  minute='*/1')
        self.console.cron + self._cronTab
        try:
            group = Group(keyword='user')
            group = self.console.storage.getGroup(group)
        except Exception, e:
            self.error('could not get user group: %s', e)

        self.console.clients.newClient('Arma3_AI', guid='Arma3_AI', name='Arma3_AI', hide=True, pbid='Arma3_AI', team=b3.TEAM_UNKNOWN, squad=None)
        self.debug('Setting Group %s for AI', group)
        client = self.console.getClient('Arma3_AI')
        client.setGroup(group)
        client.save()
        if len(self._aitypes) > 0:
            for ai in self._aitypes.keys():
                ai_name = self._aitypes[ai]
                self.console.clients.newClient(ai_name, guid=ai_name, name=ai_name, hide=True, pbid=ai_name, team=b3.TEAM_UNKNOWN, squad=None)
                client = self.console.getClient(ai_name)
                client.setGroup(group)
                client.save()

        _im = int(strftime('%M')) + 2
        if _im >= 60:
            _im -= 60
        self._cronTab = b3.cron.OneTimeCronTab(self.send_round_start, 0, _im, '*', '*', '*', '*')
        self.console.cron + self._cronTab
        self._cronTab = b3.cron.OneTimeCronTab(self.set_AITypesHidden, 0, _im, '*', '*', '*', '*')
        self.console.cron + self._cronTab
            
        
    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        return
        
    def set_AITypesHidden(self):
        xlrstats_Plugin = self.console.getPlugin('xlrstats')
        client = self.console.getClient('Arma3_AI')
        player = xlrstats_Plugin.get_PlayerStats(client)
        player.hide = 1
        xlrstats_Plugin.save_Stat(player)

    def send_round_start(self):
        self.console.queueEvent(self.console.getEvent('EVT_GAME_ROUND_START', self.console.game.mapName))
        
    def get_xlrstats(self):
        """
        9:00:55 BattlEye Server: Player #1 playername (68.46.21.245:2304) connected
        9:00:55 Player playername connecting.
        9:00:57 BattlEye Server: Player #1 playername - GUID: 79f4f7f1b8ca86afe3d5c1df11111111 (unverified)
        9:00:57 Player playername connected (id=76561198011111111).
        9:00:57 BattlEye Server: Verified GUID (79f4f7f1b8ca86afe3d5c1df11111111) of player #1 playername
        
        """
        self.debug("Starting [xlrstats] search")
        self._latest_rpt, latest_size = self.get_latest_rptname()
        if (self._last_rpt_read != self._latest_rpt):
            self._rpt_ptr = 0
            self._last_rpt_read = self._latest_rpt
            self.console.game.mapName = 'Arma3'
            self.console.game.mapName = self.getMissionName()
        if latest_size == 0:
            # self.debug('No data to read')
            return
        if (self.console.game.mapName == 'Arma3'):
            self.console.game.mapName = self.getMissionName()
            return
        self.debug('Latest rpt file is %s which is %s bytes'  % (self._latest_rpt, latest_size))
        self._rpt_ptr, rptlines = self.read_rpt_to_end(self._latest_rpt, self._rpt_ptr)
        if rptlines:  
            for line in rptlines:
                line = line.strip()
                time, sep, lineinfo = line.partition(' ')
                if lineinfo.startswith('"[xlrstats]'):
                    # self.debug('XLRSTATS INFO %s', lineinfo)
                    m = re.match(self._killFormat, lineinfo)
                    if m:
                        self.debug('killer was %s, Victim was %s, Weapon was %s' % (m.group('killer'), m.group('victim'), m.group('weapon')))
                        if m.group('killer') == "AI":
                            _killer = self.console.getClient('Arma3_AI')
                        else:
                            _killer = self.console.getClient(m.group('killer'))
                        if m.group('victim') == "AI":
                            _victim = self.console.getClient('Arma3_AI')
                        else:
                            _victim = self.console.getClient(m.group('victim'))
                        self.console.queueEvent(self.console.getEvent('EVT_CLIENT_KILL', (100, m.group('weapon'), 'Unknown'), _killer, _victim))
        # register the events we're interested in.
        # self.registerEvent('EVT_CLIENT_JOIN', self.onJoin)
        # self.registerEvent('EVT_CLIENT_KILL', self.onKill)
        # self.registerEvent('EVT_CLIENT_KILL_TEAM', self.onTeamKill)
        # self.registerEvent('EVT_CLIENT_SUICIDE', self.onSuicide)
        # self.registerEvent('EVT_GAME_ROUND_START', self.onRoundStart)
        # self.registerEvent('EVT_CLIENT_ACTION', self.onAction)       # for game-events/actions
        # self.registerEvent('EVT_CLIENT_DAMAGE', self.onDamage)       # for assist recognition

    def getMissionName(self):
        self._latest_rpt, latest_size = self.get_latest_rptname()
        self._rpt_ptr = 0
        self._last_rpt_read = self._latest_rpt

        self.debug('Latest rpt file is %s which is %s bytes'  % (self._latest_rpt, latest_size))
        self._rpt_ptr, data = self.read_rpt_to_end(self._latest_rpt, self._rpt_ptr)
        _map_name = ''
        if data:
            for line in data:
                line = line.strip()
                time, sep, lineinfo = line.partition(' ')
                lineinfo = lineinfo.strip()
                # 16:22:07  Mission file: epoch82ndtestxlr (__cur_mp)
                # 16:22:07  Mission world: Altis
                if lineinfo.startswith('Mission file:'):
                    # self.debug('XLRSTATS INFO %s', lineinfo)
                    _mission = lineinfo[14:-11].strip()
                    self.debug('XLRSTATS INFO Mission %s', _mission)
                if lineinfo.startswith('Mission world: '):
                    _world = lineinfo[15:].strip()
                    self.debug('XLRSTATS INFO World %s', _world)
            _map_name = _mission + '.' + _world
        if (_map_name == ''):
            _map_name = 'Arma3'
        return _map_name

    def read_rpt_to_end(self, filename, ptr):
        new_data = ''
        if os.path.isfile(self._latest_rpt):
            try:
                f = file(self._latest_rpt, 'r')
                f.seek(ptr, 0)
                new_data = f.read()
                ptr = f.tell()
                f.close()
            except:
                self.error('Error reading server rpt file: %s', f)
                return
        else:
            self.error('Server rpt file not found: %s', f)
            return
        return ptr, new_data.splitlines(True)
        
        
    def get_latest_rptname(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self._server_rpt_path):
            files.extend(filenames)
            break
        latesttime = 0
        latestrpt = ''
        latestsize = 0
        for file in files:
            if file.endswith('.rpt') and file.startswith(self._server_rpt_name):
                fullfilename = self._server_rpt_path + '/' + file
                self.debug('Checking file %s' % fullfilename)
                filestats = os.stat(fullfilename)
                if filestats.st_ctime > latesttime:
                    latestrpt = file
                    latesttime = filestats.st_ctime
                    latestsize = filestats.st_size
        if latestrpt == '':
            self.error('No valid rpt file found')
        latestrpt = self._server_rpt_path + '/' + latestrpt
        # self.debug('Latest rpt file is %s' % latestrpt)
        return latestrpt, latestsize
                    
