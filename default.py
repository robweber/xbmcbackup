import xbmcgui
import resources.lib.utils as utils
from resources.lib.backup import XbmcBackup

#the program mode
mode = -1

#check if mode was passed in as an argument
if(len(sys.argv) > 1):
    if(sys.argv[1].lower() == 'backup'):
        mode = 0
    elif(sys.argv[1].lower() == 'restore'):
        mode = 1

if(mode == -1):
    #figure out if this is a backup or a restore from the user
    mode = xbmcgui.Dialog().select(utils.getString(30010) + " - " + utils.getString(30023),[utils.getString(30016),utils.getString(30017)])

if(mode != -1):
    #run the profile backup
    backup = XbmcBackup()

    if(mode == backup.Restore):
        #allow user to select the backup to restore from
        restorePoints = backup.listBackups()

        selectedRestore = xbmcgui.Dialog().select(utils.getString(30010) + " - " + utils.getString(30021),restorePoints)

        if(selectedRestore != -1):
            backup.selectRestore(restorePoints[selectedRestore])
                    
    backup.run(mode)
