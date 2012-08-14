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
class Arma2AdminPlugin(b3.plugin.Plugin):
    
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
        Handle intercepted events
        """
   
    def cmd_loadscripts(self, data, client=None, cmd=None):
            self.console.write(('loadscripts', ))
            
    def cmd_loadevents(self, data, client=None, cmd=None):
            self.console.write(('loadevents', ))

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
    