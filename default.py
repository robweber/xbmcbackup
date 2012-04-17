import xbmc
import xbmcaddon
import xbmcvfs
import shutil

#get the addon class
__addon_id__ = 'script.xbmcbackup'
Addon = xbmcaddon.Addon(__addon_id__)

def syncFiles():
    xbmc.log(xbmc.translatePath("special://profile"))
    xbmc.log(Addon.getSetting("remote_path"))

    if(xbmcvfs.exists(Addon.getSetting("remote_path") + "profile")):
        shutil.rmtree(Addon.getSetting("remote_path") + "profile")

    shutil.copytree(xbmc.translatePath("special://profile"),Addon.getSetting("remote_path") + "profile")

syncFiles()
