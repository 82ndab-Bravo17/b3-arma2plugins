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
# 12/08/2014    0.2     82ndab-Bravo17 
#                       Allow for * wildcard character in log file names, for Arma 3 .rpt and server log files
#                       Allow for zero planned restarts
# 12/14/2014    0.3     Give first restart warning at 15 minutes prior

__version__ = '0.3'
__author__  = 'ThorN, Courgette, 82ndab-Bravo17'

import sys
import time
import b3
import os
import datetime
import random
import b3.events
import b3.plugin
import string
from b3 import functions
from b3.functions import getModule




#--------------------------------------------------------------------------------------------------
class ArmarestartsPlugin(b3.plugin.Plugin):
    _cronTab = []
    _shortcronTab = None
    _restarttimes = {}
    _sched = False
    _folders = {}
    _logfiles = {}
    _folders_count = 0
    _logfiles_count = 0
    _restartb3 = True
    _lockserver = False
    
    def onLoadConfig(self):
        try:
            if 'timers' in self.config.sections():
                for rs in self.config.options('timers'):
                    self._restarttimes[rs] = self.config.get('timers', rs)
                    self.debug('Restart %s : %s' % (rs, self._restarttimes[rs]))
                self.debug('No of restarts : %s' % len(self._restarttimes))
        except Exception, err:
            self.error('Error getting restart times "%s" : %s' % (Exception, err))
        
        try:
            self._msgSched15 = self.config.get('messages', 'sched15min')
            self._msgSched10 = self.config.get('messages', 'sched10min')
            self._msgSched5 = self.config.get('messages', 'sched5min')
            self._msgSched2 = self.config.get('messages', 'sched2min')
            self._msgSched1 = self.config.get('messages', 'sched1min')
            self._msg15 = self.config.get('messages', '15min')
            self._msg10 = self.config.get('messages', '10min')
            self._msg5 = self.config.get('messages', '5min')
            self._msg2 = self.config.get('messages', '2min')
            self._msg1 = self.config.get('messages', '1min')
        except Exception, err:
            self.error('Error getting restart messages "%s" : %s' % (Exception, err))

        try:
            self._restartb3 = self.config.getboolean('settings', 'restart_b3')
        except Exception, err:
            self.debug('Error getting Restart B3 setting, using default "$s" : %s' % (Exception, err))
        self.debug('B3 will restart server automatically: %s' % self._restartb3)

        try:
            self._lockserver = self.config.getboolean('settings', 'lock_server')
        except Exception, err:
            self.debug('Error gettingLock Server setting, using default "$s" : %s' % (Exception, err))
        self.debug('B3 will lock server before restart: %s' %  self._lockserver)

        try:
            if 'logfolders' in self.config.sections():
                for fol in self.config.options('logfolders'):
                    self._folders[fol] = self.config.getpath('logfolders', fol)

                if 'logfiles' in self.config.sections():
                    for fil_no in self.config.options('logfiles'):
                        file, folder = self.config.get('logfiles', fil_no).split(',')
                        self._logfiles[fil_no] = (file, folder)

        except Exception, err:
            self.error('Error getting log folder/file names "%s" : %s' % (Exception, err))

        if self._restartb3:
            self.debug('B3 will be restarted 3 minutes after each server restart')
        else:
            self.debug('B3 will NOT be restarted after each server restart')

        self.debug('Log folders %s' % self._folders)
        self.debug('Log files %s' % self._logfiles)


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

        if len(self._restarttimes) > 0:
            self.setuptimers()

    def onEvent(self, event):
        pass
        
    def setuptimers(self):

        current_time = time.time()
        local_time = time.localtime(current_time)
        self.debug('local time is %s' % local_time)
        gmt_time = time.gmtime(current_time)
        self.debug('GMT time is %s' % gmt_time)

        time_diff = gmt_time.tm_hour - local_time.tm_hour

        self.debug('Time diff is %s' % time_diff)
        rs_number = -1
        for rs in self._restarttimes.keys():
            rs_number += 1
            rhour, sep, rmin = self._restarttimes[rs].partition(':')
            rshour = int(rhour) + time_diff
            if rshour >= 24:
                rshour -= 24
            if rshour < 0:
                rshour += 24
            rsmin = int(rmin)
            rsmin -= 15
            if rsmin < 0:
                rsmin += 60 
                rshour -= 1
                if rshour < 0:
                    rshour += 24
            self.debug("Server restart process will start at %02d:%02d GMT every day" % (rshour,rsmin))
            self._cronTab.append(b3.cron.PluginCronTab(self, self.schedule_restart, 0, rsmin, rshour, '*', '*', '*'))
            self.console.cron + self._cronTab[rs_number]
        # This is needed in case the server doesn't restart after it has been locked for the restart
        self.setUpcrontab(2, 'unlock_server')

    def schedule_restart(self):
        self.debug("Starting shutdown sequence")
        self._sched = True
        self.sendRestartmessage_15()

    def sendRestartmessage_15(self):
        if self._sched:
            self.console.say(self._msgSched15)
        else:
            self.console.say(self._msg15)
        self.setUpcrontab(5, 'sendRestartmessage_10')

    def sendRestartmessage_10(self):
        if self._sched:
            self.console.say(self._msgSched10)
        else:
            self.console.say(self._msg10)
        self.setUpcrontab(5, 'sendRestartmessage_5')

    def sendRestartmessage_5(self):
        if self._sched:
            self.console.say(self._msgSched5)
        else:
            self.console.say(self._msg5)
        self.setUpcrontab(3, 'sendRestartmessage_2')
        if self._lockserver:
            self.console.write(self.console.getCommand('lockserver',))
            self.console.say('Server is locked until after the restart. If you leave you will not be able to rejoin until then.')
            
    def sendRestartmessage_2(self):
        if self._sched:
            self.console.say(self._msgSched2)
        else:
            self.console.say(self._msg2)
        self.setUpcrontab(1, 'sendRestartmessage_1')
            
    def sendRestartmessage_1(self):
        if self._sched:
            self.console.say(self._msgSched1)
        else:
            self.console.say(self._msg1)
        self.setUpcrontab(1, 'sendRestartserver')

    def sendRestartserver(self):
        self.console.say('Server is shutting down immediately')
        self.console.write(self.console.getCommand('shutdown', ))
        if self._restartb3:
            self.setUpcrontab(3, 'sendRestart_bot')
        self._sched = False
        time.sleep(10)
        self.renamelogs()

    def sendRestart_bot(self):
        self.console.restart()

    def setUpcrontab(self, delay_in_min, func):
        current_min = time.localtime().tm_min
        current_sec = time.localtime().tm_sec
        dlmin = current_min + delay_in_min
        if dlmin >= 60:
            dlmin -= 60
            
        func = getattr(self, func)
        self._shortcronTab = b3.cron.OneTimeCronTab(func, current_sec, dlmin, '*', '*', '*', '*')
        self.debug("Setting up crontab for %s" % dlmin)
        self.console.cron + self._shortcronTab
        

    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
      
    def unlock_server(self):
        self.console.write(self.console.getCommand('unlockserver',))
        self.debug('Server has been unlocked.')

    def onEvent(self, event):
        """\
        Handle intercepted events
        """
   
    def cmd_shutdown(self, data, client=None, cmd=None):
        if not data:
            self.sendRestartserver()
        else:
            if data == '15':
                self._sched = False
                self.sendRestartmessage_15()
            elif data == '10':
                self._sched = False
                self.sendRestartmessage_10()
            elif data == '5':
                self._sched = False
                self.sendRestartmessage_5()
            elif data == '2':
                self._sched = False
                self.sendRestartmessage_2()
            elif data == '1':
                self._sched = False
                self.sendRestartmessage_1()
            elif data == '0':
                self.sendRestartserver()
            else:
                client.message('Invalid parameters, you must supply a valid time, 0, 1, 2 , 5, 10 or 15')

    def renamelogs(self):
        if len(self._folders) <= 0:
            self.info('No files to rename')
            return
            
        now = datetime.datetime.today()
        str_now = '_' + now.strftime("%Y%m%d-%H%M%S")
            
        new_logdir = self._folders['logs'] + '/logs/' + str_now +'/'
        try:
            os.mkdir(new_logdir)
        except Exception, err:
            print('Error creating folder "%s" : %s' % (Exception, err))
            return
            
        for fil in self._logfiles.keys():
            self.debug('Renaming %s in %s' % (self._logfiles[fil][0],self._logfiles[fil][1] ))
            org_folder = self._folders[self._logfiles[fil][1]]
            org_file = self._logfiles[fil][0]
            if '*' in org_file:
                self.rename_wildcard_files(org_file, org_folder, str_now, new_logdir)
            else:
                self.rename_single_file(org_file, org_folder, str_now, new_logdir)
                
                
    def rename_wildcard_files(self, org_file, org_folder, str_now, new_logdir):
        filename, extension = org_file.split('.')
        if filename == '*':
            file_list = os.listdir(org_folder)
            for file in file_list:
                if file.endswith(extension):
                    self.rename_single_file(file, org_folder, str_now, new_logdir)
        else:
            filename = filename.split('*')[0]
            file_list = os.listdir(org_folder)
            for file in file_list:
                if file.startswith(filename) and file.endswith(extension):
                    self.rename_single_file(file, org_folder, str_now, new_logdir)

    def rename_single_file(self, org_file, org_folder, str_now, new_logdir):
        org_log =  os.path.normpath(org_folder + '/' + org_file)
        self.debug('Original log file %s' % org_log)
        filename, extension = org_file.split('.')
        new_log = os.path.normpath(new_logdir + filename + str_now + '.' + extension)
        try:
            self.debug('Renameing %s to %s' % (org_log, new_log))
            os.rename(org_log, new_log)
        except Exception, err:
            self.error('Error renamimg log %s to %s :"%s" : %s' % (org_log, new_log, Exception, err))
        

    
                
                
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
    