arma2plugins
============

Here are 3 completed Arma 2 & 3 plugins:

1.  arma2admin - allows you to perform many admin functions that would otherwisw require you to log in within Arma

    loadbattleyescripts runs the loadscripts and loadevents commands
    
    loadbattleevents runs the loadevents command
    
    mission starts the named mission, or optionally can run a mission by a number obtained from the !listmissions command.
    
    listmissions lists all the available missions
    
    restartmission restarts the current mission without forcing the re-assigning of roles.
    
    reasignroles restarts the current mission including assignment of roles.
    
    servermonitor turns server monitor on or off. Note: have to be logged in on server as admin to see the output, so not really much use but included for completeness.
    
    missionlike returns a list of missions that match a pattern, and can run the mission if the mission number is given.
    
    captureframe runs the captureframe command
    
    
    loadbans runs the loadbans command

    Note - you need to set the battleye folder in bepath in order to get feedback as to whether the specified ban file exists or not


    
    
2.  arma2lobbykick - kicks players who are in the lobby too long, with option to exempt admins


3.  arma2restarts - allows you to perform planned or unplanned restarts of the server



Place the plugins in the extplugins folder and the xmls in the extplugins/conf folder, then add:

<plugin name="arma2admin" config="@b3/extplugins/conf/arma2admin.xml"/>
<plugin name="arma2lobbykick" config="@b3/extplugins/conf/arma2lobbykick.xml"/>
<plugin name="arma2restarts" config="@b3/extplugins/conf/arma2restarts.xml"/>

to your b3 xml plugin section (you only need to add the ones that you wish to use)