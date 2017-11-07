import xbmc
import xbmcgui
import xbmcvfs
import resources.lib.tinyurl as tinyurl
import resources.lib.utils as utils
from resources.lib.dropbox import client, rest, session
from resources.lib.pydrive.auth import GoogleAuth
from resources.lib.pydrive.drive import GoogleDrive

class DropboxAuthorizer:
    APP_KEY = ""
    APP_SECRET = ""
    
    def __init__(self):
        self.APP_KEY = utils.getSetting('dropbox_key')
        self.APP_SECRET = utils.getSetting('dropbox_secret')

    def setup(self):
        result = True
        
        if(self.APP_KEY == '' and self.APP_SECRET == ''):
            #we can't go any farther, need these for sure
            xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30027) + ' ' + utils.getString(30058),utils.getString(30059))

            result = False
            
        return result    

    def isAuthorized(self):
        user_token_key,user_token_secret = self._getToken()

        return user_token_key != '' and user_token_secret != ''        

    def authorize(self):
        result = True

        if(not self.setup()):
            return False
        
        if(self.isAuthorized()):
            #delete the token to start over
            self._deleteToken()

        sess = session.DropboxSession(self.APP_KEY,self.APP_SECRET,"app_folder")

        token = sess.obtain_request_token()
        url = sess.build_authorize_url(token)

        #print url in log
        utils.log("Authorize URL: " + url)
        xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30056),utils.getString(30057),tinyurl.shorten(url))
            
        #if user authorized this will work
        user_token = sess.obtain_access_token(token)
        self._setToken(user_token.key,user_token.secret)

        return result;

    #return the DropboxClient, or None if can't be created
    def getClient(self):
        result = None
        sess = session.DropboxSession(self.APP_KEY,self.APP_SECRET,"app_folder")
        user_token_key,user_token_secret = self._getToken()

        if(user_token_key != '' and user_token_secret != ''):
            #create the client
            sess.set_token(user_token_key,user_token_secret)
            result = client.DropboxClient(sess)

            try:
                utils.log(str(result.account_info()))
            except:
                #this didn't work, delete the token file
                self._deleteToken()
                
        return result

    def _setToken(self,key,secret):
        #write the token files
        token_file = open(xbmc.translatePath(utils.data_dir() + "tokens.txt"),'w')
        token_file.write("%s|%s" % (key,secret))
        token_file.close()

    def _getToken(self):
        #get tokens, if they exist
        if(xbmcvfs.exists(xbmc.translatePath(utils.data_dir() + "tokens.txt"))):
            token_file = open(xbmc.translatePath(utils.data_dir() + "tokens.txt"))
            key,secret = token_file.read().split('|')
            token_file.close()

            return [key,secret]
        else:
            return ["",""]
        
    def _deleteToken(self):
        if(xbmcvfs.exists(xbmc.translatePath(utils.data_dir() + "tokens.txt"))):
            xbmcvfs.delete(xbmc.translatePath(utils.data_dir() + "tokens.txt"))

class GoogleDriveAuthorizer:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    
    def __init__(self):
        self.CLIENT_ID = utils.getSetting('google_drive_id')
        self.CLIENT_SECRET = utils.getSetting('google_drive_secret')

    def setup(self):
        result = True
        
        if(self.CLIENT_ID == '' and self.CLIENT_SECRET == ''):
            #we can't go any farther, need these for sure
            xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30098) + ' ' + utils.getString(30058),utils.getString(30108))
            result = False

        return result
        
    def isAuthorized(self):
        return xbmcvfs.exists(xbmc.translatePath(utils.data_dir() + "google_drive.dat"))
    
    def authorize(self):
        result = True

        if(not self.setup()):
            return False

        #create authorization helper and load default settings
        gauth = GoogleAuth(xbmc.validatePath(xbmc.translatePath(utils.addon_dir() + '/resources/lib/pydrive/settings.yaml')))
        gauth.LoadClientConfigSettings()

        settings = {"client_id":self.CLIENT_ID,'client_secret':self.CLIENT_SECRET}
    
        drive_url = gauth.GetAuthUrl(settings)
    
        utils.log("Google Drive Authorize URL: " + drive_url)

        xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30056),utils.getString(30102),tinyurl.shorten(drive_url))
        code = xbmcgui.Dialog().input(utils.getString(30103))

        gauth.Auth(code)
        gauth.SaveCredentialsFile(xbmc.validatePath(xbmc.translatePath(utils.data_dir() + 'google_drive.dat')))

        return result

    def getClient(self):
        #create authorization helper and load default settings
        gauth = GoogleAuth(xbmc.validatePath(xbmc.translatePath(utils.addon_dir() + '/resources/lib/pydrive/settings.yaml')))
        gauth.LoadClientConfigSettings()

        gauth.LoadCredentialsFile(xbmc.validatePath(xbmc.translatePath(utils.data_dir() + 'google_drive.dat')))

        result = GoogleDrive(gauth)

        return result


    
