import xbmc
import xbmcgui
import xbmcvfs
import resources.lib.utils as utils
from resources.lib.authorizers import DropboxAuthorizer,GoogleDriveAuthorizer

#drobpox
if(utils.getSetting('remote_selection') == '2'):
    authorizer = DropboxAuthorizer()

    if(authorizer.authorize()):
        xbmcgui.Dialog().ok("Backup","Dropbox is authorized")
    else:
        xbmcgui.Dialog().ok("Backup","Error Authorizing Dropbox")

#google drive
elif(utils.getSetting('remote_selection') == '3'):
    authorizer = GoogleDriveAuthorizer()

    if(authorizer.authorize()):
        xbmcgui.Dialog().ok("Backup","Google Drive is authorized")
    else:
        xbmcgui.Dialog().ok("Backup","Error Authorizing Google Drive")
