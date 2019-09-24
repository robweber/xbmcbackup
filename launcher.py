import sys
import urlparse
import xbmc
import xbmcgui
import xbmcvfs
import resources.lib.utils as utils
from resources.lib.authorizers import DropboxAuthorizer,GoogleDriveAuthorizer
from resources.lib.advanced_editor import AdvancedBackupEditor


#launcher for various helpful functions found in the settings.xml area

def authorize_cloud(cloudProvider):
    #drobpox
    if(cloudProvider == 'dropbox'):
        authorizer = DropboxAuthorizer()

        if(authorizer.authorize()):
            xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30027) + ' ' + utils.getString(30106))
        else:
            xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30107) + ' ' + utils.getString(30027))

    #google drive
    elif(cloudProvider == 'google_drive'):
        authorizer = GoogleDriveAuthorizer()

        if(authorizer.authorize()):
            xbmcgui.Dialog().ok("Backup",utils.getString(30098) + ' ' + utils.getString(30106))
        else:
            xbmcgui.Dialog().ok("Backup",utils.getString(30107) + ' ' + utils.getString(30098))

def remove_auth():
    #triggered from settings.xml - asks if user wants to delete OAuth token information
    shouldDelete = xbmcgui.Dialog().yesno(utils.getString(30093),utils.getString(30094),utils.getString(30095),autoclose=7000)

    if(shouldDelete):
        #delete any of the known token file types
        xbmcvfs.delete(xbmc.translatePath(utils.data_dir() + "tokens.txt")) #dropbox
        xbmcvfs.delete(xbmc.translatePath(utils.data_dir() + "google_drive.dat")) #google drive
    
def get_params():
    param = {}
    try:
        for i in sys.argv:
            args = i
            if(args.startswith('?')):
                args = args[1:]
            param.update(dict(urlparse.parse_qsl(args)))
    except:
        pass
    return param

params = get_params()

if(params['action'] == 'authorize_cloud'):
    authorize_cloud(params['provider'])
elif(params['action'] == 'remove_auth'):
    remove_auth()
elif(params['action'] == 'advanced_editor'):
    editor = AdvancedBackupEditor()
    editor.showMainScreen()
elif(params['action'] == 'advanced_copy_config'):
    editor = AdvancedBackupEditor()
    editor.copySimpleConfig()
