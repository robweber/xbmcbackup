import xbmcgui
import resources.lib.utils as utils
from resources.lib.backup import XbmcBackup

#figure out if this is a backup or a restore
mode = xbmcgui.Dialog().select(utils.getString(30010) + " - " + utils.getString(30023),[utils.getString(30016),utils.getString(30017)])

if(mode != -1):
    #run the profile backup
    backup = XbmcBackup()
    backup.run(mode)
