import xbmc
import xbmcgui
import xbmcvfs
import resources.lib.utils as utils
from resources.lib.authorizers import DropboxAuthorizer,GoogleDriveAuthorizer

#drobpox
if(utils.getSetting('remote_selection') == '2'):
    authorizer = DropboxAuthorizer()

    if(authorizer.authorize()):
        xbmcgui.Dialog().ok("Backup",utils.getString(30027) + ' ' + utils.getString(30106))
    else:
        xbmcgui.Dialog().ok("Backup",utils.getString(30107) + ' ' + utils.getString(30027))

#google drive
elif(utils.getSetting('remote_selection') == '3'):
    authorizer = GoogleDriveAuthorizer()

    if(authorizer.authorize()):
        xbmcgui.Dialog().ok("Backup",utils.getString(30098) + ' ' + utils.getString(30106))
    else:
        xbmcgui.Dialog().ok("Backup",utils.getString(30107) + ' ' + utils.getString(30098))
