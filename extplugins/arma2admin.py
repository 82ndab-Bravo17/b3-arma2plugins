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
# $Id: publist.py 43 2005-12-06 02:17:55Z thorn $
#
# CHANGELOG
# 07/25/2012    0.1     82ndab-Bravo17 Initial release
# 02/12/2013    0.2     loadbattleyescripts mow loads all scripts files, including those considered to be event files
# 21/12/2013    0.3     Added mission changing/Server restart commands

__version__ = '0.3'
__author__  = 'ThorN, Courgette, 82ndab-Bravo17'

import sys
import time
import b3
import os
import random
import b3.events
import b3.plugin
import string
import re
from b3 import functions
from b3.functions import getModule




#--------------------------------------------------------------------------------------------------
class Arma2AdminPlugin(b3.plugin.Plugin):
    
    _mission_list = {}
    _be_path = None
    
    def onStartup(self):
      
        # get the plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
                else:
                    self.error('Could not find method %s' % cmd)
                    
        if self.config.has_option('settings','bepath'):
            self._be_path = self.config.get('settings','bepath')
            if self._be_path == "":
                self._be_path = None
                self.error('Config error: bepath is empty')
            else:
                if not os.path.isdir(self._be_path):
                    self._be_path = None
                    self.error('Config error: bepath is not a directory')
            
    
    def onEvent(self, event):
        pass
        
    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
      


    def onEvent(self, event):
        """\
        Handle intercepted events.
        """
   
    def cmd_loadbattleyescripts(self, data, client=None, cmd=None):
        """\
        Reloads all battleye script and event files.
        """
        self.console.write(('loadscripts', ))
        self.console.write(('loadevents', ))
        client.message('All Script files have been reloaded')
            
    def cmd_loadbattleyeevents(self, data, client=None, cmd=None):
        """\
        Reloads all battleye event files.
        """
        self.console.write(('loadevents', ))
        client.message('All Event Script files have been reloaded')
            
    def cmd_mission(self, data, client=None, cmd=None):
        """\
        Starts the named mission, or optionally can run a mission by a number obtained from the !listmissions command.
        """
        if not data:
            client.message('You Need to give the name or number of the mission that you want to run')
            return
            
        self._mission_list = self.get_missionlist()
        
        if data in self._mission_list.values():
            self.console.write(self.console.getCommand('mission', missionname=data))
        elif data in self._mission_list.keys():
            missionname = self._mission_list[data]
            self.console.write(self.console.getCommand('mission', missionname=missionname))
        
        else:
            client.message('Mission %s does not exist' % data)
            
    def cmd_missionsscreen(self, data, client=None, cmd=None):
        """\
        send the server back to the mission selection screen.
        """
        self.console.write(self.console.getCommand('missionsscreen', ))
            
    def cmd_restartmission(self, data, client=None, cmd=None):
        """\
        Restarts the current mission without forcing the re-assigning of roles.
        """
        self.console.write(self.console.getCommand('restartmission', ))
            
    def cmd_reassignroles(self, data, client=None, cmd=None):
        """\
        Restarts the current mission including assignment of roles.
        """
        self.console.write(self.console.getCommand('reassignroles', ))
            
    def cmd_servermonitor(self, data, client=None, cmd=None):
        """\
        turns server monitor on or off. Note: have to be logged in on server as admin to see the output, so not really much use but included for completeness.
        """
        if data.lower() == "off":
            self.console.write(self.console.getCommand('servermonitor', onoff='0'))
        else:
            self.console.write(self.console.getCommand('servermonitor', onoff='1'))
            
    def cmd_captureframe(self, data, client=None, cmd=None):
        self.console.write(('#captureFrame', ))
        
        
    def cmd_listmissions(self, data, client=None, cmd=None):
        """\
        Lists all the missions on the server. Will only list .pbo files, not folders. Gives each mission a number that can be used by !mission.
        """
        self._mission_list = self.get_missionlist()
        for x in xrange (1, len(self._mission_list)+1):
            try:
                msg = ('%s - %s' % (x, self._mission_list[str(x)]))
                client.message(msg)
            except KeyError, err:
                pass
            except:
                raise
            
    def cmd_missionlike(self, data, client=None, cmd=None):
        """\
        Returns a list of missions that match a pattern, and can run the mission if the mission number is given.
        """
        if not data:
            client.message('You Need to give a part of the name of the mission that you want to run')
            return
            
        match = re.search(r'^(?P<partial_name>.+)\s(?P<partial_mission_no>[0-9]+)$', data)
        if match:
            c = match.groupdict()
            partial_name = c['partial_name'].lower()
            partial_mission_no = c['partial_mission_no']
        else:
            partial_name = data.lower()
            partial_mission_no = ''

        mission_partial_list = {}
        self._mission_list = self.get_missionlist()
        i = 1
        for mission_name in self._mission_list.values():

            if mission_name.lower().find(partial_name) != -1:
                mission_partial_list[str(i)] = mission_name
                i += 1
                
        if len(mission_partial_list) < 1:
            client.message('No missions match that partial name')
            return
            
        if partial_mission_no != '':
            if partial_mission_no in mission_partial_list.keys():
                missionname = mission_partial_list[partial_mission_no]
                self.console.write(self.console.getCommand('mission', missionname=missionname))
            else:
                client.message('That is not a valid number for the mission selection')
        else:
            for x in xrange (1, len(mission_partial_list)+1):
                try:
                    msg = ('%s - %s' % (x, mission_partial_list[str(x)]))
                    client.message(msg)
                except KeyError, err:
                    pass
                except:
                    raise
            
    def get_missionlist(self):
        """\
        Retrieves the list of missions on the server.
        """
        mission_dict = {}
        missions = None
        try:
            missions = self.console.write(self.console.getCommand('listmissions', )).splitlines()
        except AttributeError, err:
            if missions is None:
                return mission_dict
            else:
                raise
        except:
            raise
            
        i = 1
        mission_dict = {}
        for mission in missions:
            if mission.strip().endswith('.pbo'):
                mission_dict[str(i)] = mission.rpartition('.pbo')[0]
                i += 1
        
        return mission_dict

    def cmd_loadbans(self, data, client=None, cmd=None):
        """\
        Reloads the ban lists.
        """
        if not data:
            data = 'bans'
        banfiles = data.split()
        for banfile in banfiles:
            banfilename = banfile + '.txt'
            if self._be_path:
                if os.path.isfile(os.path.join(self._be_path, banfilename)):
                    client.message('Loading bans from %s' % banfilename)
                    self.console.write(('loadbans', banfilename))
                else:
                    client.message('Banfile does not exist: %s' % banfilename)
            else:
                client.message('Attempting to load bans from %s, but unable to confirm that it exists since bepath is not set' % banfilename)
                self.console.write(('loadbans', banfilename))

        
if __name__ == '__main__':
    from b3.fake import fakeConsole
    import time
    
    from b3.config import XmlConfigParser
    
    conf = XmlConfigParser()
    conf.setXml("""
    <configuration plugin="publist">
        <settings name="settings">
            <set name="urlsqdf">http://test.somewhere.com/serverping.php</set>
            <set name="url">http://localhost/b3publist/serverping.php</set>
            <set name="delay">30</set>
        </settings>
    </configuration>
    """)

    
    
    def test_startup():
        p._initial_heartbeat_delay = 10
        p.onStartup()
        time.sleep(5)
        print "_heartbeat_sent : %s" % p._heartbeat_sent
        time.sleep(20)
        print "_heartbeat_sent : %s" % p._heartbeat_sent
        fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_STOP, None, None))
        #p.update()
    
    def test_crontab():
        def myUpdate():
            p.sendInfo({'version': '1.4.1b', 
                'os': 'nt', 
                'action': 'fake', 
                'ip': '212.7.205.31', 
                'parser': 'bfbc2', 
                'plugins': 'censorurt/0.1.2,admin/1.8.2,publist/1.7.1,poweradminurt/1.5.7,tk/1.2.4,adv/1.2.2', 
                'port': 19567, 
                'parserversion': 'x.x.x', 
                'rconPort': 48888,
                'python_version': 'publist test',
                'serverDescription': 'publist plugin test|from admin: Courgette|email: courgette@bigbrotherbot.net| visit our web site : www.bigbrotherbot.net',
                'bannerUrl': 'http://www.lowpinggameservers.com/i/bc2.jpg',
                'default_encoding': sys.getdefaultencoding()
                })
        p._cronTab = b3.cron.PluginCronTab(p, myUpdate, second='*/10')
        p.console.cron + p._cronTab
        
    
    #fakeConsole._publicIp = '127.0.0.1'
    fakeConsole._publicIp = '11.22.33.44'
    p = PublistPlugin(fakeConsole, conf)
    p.onLoadConfig()
    
    #test_heartbeat()
    #test_heartbeat_local_urt()
    #test_heartbeat_b3_bfbc2()
    test_heartbeat_homefront()
    #test_crontab()
    
    time.sleep(120) # so we can see thread working

    #p.sendInfo({'action' : 'shutdown', 'ip' : '91.121.95.52', 'port' : 27960, 'rconPort' : None })
    