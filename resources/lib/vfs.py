import utils as utils
import xbmcvfs
from dropbox import client, rest, session

APP_KEY = 'f5wlmek6aoriqax'
APP_SECRET = 'b1461sje1kxgzet'

class Vfs:
    type = 'none'

    def listdir(directory):
        return {}

    def mkdir(directory):
        return True

    def copy(source,dest):
        return True

    def rmdir(directory):
        return True

    def exists(aFile):
        return True
        
class XBMCFileSystem(Vfs):
    self.root_path
    def listdir(directory):
        return xbmcvfs.listdir(directory)

    def mkdir(directory):
        return xbmcvfs.mkdir(directory)

    def rmdir(directory):
        return xbmcvfs.rmdir(directory,True)

    def exists(aFile):
        return xbmcvfs.exists(aFile)

class DropboxFilesystem(Vfs):

    def __init__(self):
        session = session.DropboxSession(APP_KEY,APP_SECRET,"app_folder")
        token = session.obtain_request_token()
        access_token = session.obtain_access_token(token)
