import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os

class RestoreFile:
    addonDir = ''
    fHandle = None
    
    def __init__(self,addon_dir):
        self.addonDir = addon_dir

    def createRestoreFile(self):
        #create the addon folder if it doesn't exist
        if(not os.path.exists(unicode(xbmc.translatePath(self.addonDir),'utf-8'))):
            os.makedirs(unicode(xbmc.translatePath(self.addonDir),'utf-8'))
        xbmc.log(self.addonDir)
        self.fHandle = open(unicode(xbmc.translatePath(self.addonDir + "restore.txt"),'utf-8'),"w")

    def addFile(self,filename):
        #write the full remote path name of this file
        if(self.fHandle != None):
            self.fHandle.write(str(filename) + "\n")

    def closeRestoreFile(self,sendDir):
        #close out the file and write it to the remote store
        if(self.fHandle != None):
            self.fHandle.close()
            #xbmcvfs.copy(self.addonDir + "restore.txt",sendDir + "restore.txt")
            

class XbmcBackup:
    __addon_id__ = 'script.xbmcbackup'
    Addon = xbmcaddon.Addon(__addon_id__)
    local_path = ''
    remote_path = ''
    restoreFile = None
    
    #for the progress bar
    progressBar = None
    dirsLeft = 0
    dirsTotal = 0
    
    def __init__(self):
        self.local_path = xbmc.translatePath("special://home")

        if(self.Addon.getSetting('remote_path') != '' and self.Addon.getSetting("backup_name") != ''):
            self.remote_path = self.Addon.getSetting("remote_path") + self.Addon.getSetting('backup_name') + "/"

        self.restoreFile = RestoreFile(self.Addon.getAddonInfo('profile'))
        
        self.log("Starting")
        self.log('Local Dir: ' + self.local_path)
        self.log('Remote Dir: ' + self.remote_path)
        
    def syncFiles(self):
        self.restoreFile.createRestoreFile()
        
        if(xbmcvfs.exists(self.remote_path)):
            #this will fail - need a disclaimer here
            self.log("Remote Path exists - may have old files in it!")

        xbmcvfs.mkdir(self.remote_path)

        if(self.Addon.getSetting('run_silent') == 'false'):
            self.progressBar = xbmcgui.DialogProgress()
            self.progressBar.create('XBMC Backup','Running......')
            self.updateProgress(1)

        #figure out which syncing options to run
        if(self.Addon.getSetting('backup_addons') == 'true' and not self.checkCancel()):
            xbmcvfs.mkdir(self.remote_path + "addons")
            self.walkTree(self.local_path + "addons/")

        xbmcvfs.mkdir(self.remote_path + "userdata")
        if(self.Addon.getSetting('backup_addon_data') == 'true' and not self.checkCancel()):
            xbmcvfs.mkdir(self.remote_path + "userdata/addon_data")
            self.walkTree(self.local_path + "userdata/addon_data/")
           
        if(self.Addon.getSetting('backup_database') == 'true' and not self.checkCancel()):
			xbmcvfs.mkdir(self.remote_path + "userdata/Database")
			self.walkTree(self.local_path + "userdata/Database")
        
        if(self.Addon.getSetting("backup_playlists") == 'true' and not self.checkCancel()):
			xbmcvfs.mkdir(self.remote_path + "userdata/playlists")
			self.walkTree(self.local_path + "userdata/playlists")
			
        if(self.Addon.getSetting("backup_thumbnails") == "true" and not self.checkCancel()):
			xbmcvfs.mkdir(self.remote_path + "userdata/Thumbnails")
			self.walkTree(self.local_path + "userdata/Thumbnails")
		
        if(self.Addon.getSetting("backup_config") == "true" and not self.checkCancel()):
			#this one is an oddity
			configFiles = os.listdir(self.local_path + "userdata/")
			for aFile in configFiles:
				if(aFile.endswith(".xml")):
					self.log("Copying: " + self.local_path + "userdata/" + aFile)
					xbmcvfs.copy(self.local_path + "userdata/" + aFile,self.remote_path + "userdata/" + aFile)

        #close out everything
        self.restoreFile.closeRestoreFile(self.remote_path)
        if(self.Addon.getSetting('run_silent') == 'false'):
            self.progressBar.close()
		    
			
    def walkTree(self,directory):
        for (path, dirs, files) in os.walk(directory):
            if(not self.checkCancel()):
                #get the relative part of this path
                path = path[len(self.local_path):]
            
                #subtract one from total
                self.dirsLeft = self.dirsLeft - 1
                self.updateProgress(len(dirs),"Copying: " + path)

                #create all the subdirs first
                for aDir in dirs:
                    xbmcvfs.mkdir(self.remote_path + os.sep + path + os.sep +  aDir)
                    self.restoreFile.addFile(path + os.sep + aDir)
                #copy all the files
                for aFile in files:
                    filePath = path + os.sep + aFile
                    self.log("copying: " + self.local_path + filePath)
                    self.restoreFile.addFile(filePath)
                    
                    xbmcvfs.copy(self.local_path + filePath,self.remote_path + filePath)

    def updateProgress(self,dirCount,message=''):
        #add to the total
        self.dirsTotal = self.dirsTotal + dirCount
        self.dirsLeft = self.dirsLeft + dirCount

        #update the progress bar
        if(self.progressBar != None):
            self.progressBar.update((float(self.dirsTotal - self.dirsLeft)/float(self.dirsTotal)) * 100,message)
            
    def checkCancel(self):
        result = False

        if(self.progressBar != None):
            result = self.progressBar.iscanceled()

        return result
      
    def log(self,message):
        xbmc.log(self.__addon_id__ + ": " + message)

    def isReady(self):
        return True if self.remote_path != '' else False

#run the profile backup
backup = XbmcBackup()

if(backup.isReady()):
    backup.syncFiles()
else:
    xbmcgui.Dialog().ok('XBMC Backup','Error: Remote path cannot be empty')
