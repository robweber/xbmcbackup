import utils as utils
import xbmcvfs
import xbmcgui
from dropbox import client, rest, session

APP_KEY = 'f5wlmek6aoriqax'
APP_SECRET = 'b1461sje1kxgzet'

class Vfs:
    root_path = None

    def set_root(self,rootString):
        self.root_path = rootString

        #fix slashes
        self.root_path = self.root_path.replace("\\","/")
        
        #check if trailing slash is included
        if(self.root_path[-1:] != "/"):
            self.root_path = self.root_path + "/"
        
    def listdir(self,directory):
        return {}

    def mkdir(self,directory):
        return True

    def copy(self,source,dest):
        return True

    def rmdir(self,directory):
        return True

    def exists(self,aFile):
        return True
        
class XBMCFileSystem(Vfs):
    
    def listdir(self,directory):
        return xbmcvfs.listdir(directory)

    def mkdir(self,directory):
        return xbmcvfs.mkdir(directory)

    def copy(self,source,dest):
        return xbmcvfs.copy(source,dest)

    def rmdir(self,directory):
        return xbmcvfs.rmdir(directory,True)

    def exists(self,aFile):
        return xbmcvfs.exists(aFile)

class DropboxFileSystem(Vfs):
    user_token = None
    
    def __init__(self):
        self.user_token = utils.getSetting('dropbox_token')
        sess = session.DropboxSession(APP_KEY,APP_SECRET,"app_folder")

        if(self.user_token == ''):
            token = sess.obtain_request_token()
            url = sess.build_authorize_url(token)
            try:
                self.user_token = sess.obtain_access_token(token)
                utils.setSetting("dropbox_token",self.user_token)
            except:
                xbmcgui.Dialog().ok(utils.getString(30010),"Authorize Dropbox URL, also in log",url)
                utils.log("Authorize URL: " + url)

        self.client = client.DropboxClient(sess)
        utils.log(self.client.account_info())
            



            
