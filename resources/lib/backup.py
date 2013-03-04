import xbmc
import xbmcgui
import xbmcvfs
import utils as utils
import os.path
import time
from vfs import XBMCFileSystem,DropboxFileSystem

class XbmcBackup:
    #constants for initiating a back or restore
    Backup = 0
    Restore = 1

    #remote file system
    xbmc_vfs = None
    remote_vfs = None
    restoreFile = None
    
    #for the progress bar
    progressBar = None
    filesLeft = 0
    filesTotal = 1

    fileManager = None
    restore_point = None

    def __init__(self):
        self.xbmc_vfs = XBMCFileSystem(xbmc.translatePath('special://home'))

        self.configureRemote()
        utils.log(utils.getString(30046))

    def configureRemote(self):
        if(utils.getSetting('remote_selection') == '1'):
            self.remote_vfs = XBMCFileSystem(utils.getSetting('remote_path_2'))
	    utils.setSetting("remote_path","")
        elif(utils.getSetting('remote_selection') == '0'):
            self.remote_vfs = XBMCFileSystem(utils.getSetting("remote_path"))
        elif(utils.getSetting('remote_selection') == '2'):
            self.remote_vfs = DropboxFileSystem("/")

    def listBackups(self):
        result = list()

        #get all the folders in the current root path
        dirs,files = self.remote_vfs.listdir(self.remote_vfs.root_path)
        
        for aDir in dirs:
            result.append(aDir)

        return result

    def selectRestore(self,restore_point):
        self.restore_point = restore_point

    def run(self,mode=-1,runSilent=False):
        #append backup folder name
        remote_base_path = ""
        progressBarTitle = utils.getString(30010) + " - "
        if(mode == self.Backup and self.remote_vfs.root_path != ''):
            #capture base path for backup rotation
            remote_base_path = self.remote_vfs.set_root(self.remote_vfs.root_path + time.strftime("%Y%m%d") + "/")
            progressBarTitle = progressBarTitle + utils.getString(30016)
	elif(mode == self.Restore and self.restore_point != None and self.remote_vfs.root_path != ''):
	    self.remote_vfs.set_root(self.remote_vfs.root_path + self.restore_point + "/")
	    progressBarTitle = progressBarTitle + utils.getString(30017)
	else:
            #kill the program here
	    self.remote_vfs = None
	    return

        utils.log(utils.getString(30047) + ": " + self.xbmc_vfs.root_path)
        utils.log(utils.getString(30048) + ": " + self.remote_vfs.root_path)

        #check if we should use the progress bar
        if(utils.getSetting('run_silent') == 'false' and not runSilent):
            self.progressBar = xbmcgui.DialogProgress()
            self.progressBar.create(progressBarTitle,utils.getString(30049) + "......")

        if(mode == self.Backup):
            utils.log(utils.getString(30023) + " - " + utils.getString(30016))
            #check if remote path exists
            if(self.remote_vfs.exists(self.remote_vfs.root_path)):
                #may be data in here already
                utils.log(utils.getString(30050))
            else:
                #make the remote directory
                self.remote_vfs.mkdir(self.remote_vfs.root_path)

            utils.log(utils.getString(30051))
            allFiles = []
            fileManager = FileManager(self.xbmc_vfs)
         
            #go through each of the user selected items and write them to the backup store
            if(utils.getSetting('backup_addons') == 'true'):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "addons")
                fileManager.walkTree(xbmc.translatePath('special://home/addons'))

            self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata")

            if(utils.getSetting('backup_addon_data') == 'true'):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/addon_data")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/addon_data'))

            if(utils.getSetting('backup_database') == 'true'):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/Database")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/Database'))
        
            if(utils.getSetting("backup_playlists") == 'true'):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/playlists")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/playlists'))
                
            if(utils.getSetting("backup_thumbnails") == "true"):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/Thumbnails")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/Thumbnails'))
	  
            if(utils.getSetting("backup_config") == "true"):
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/keymaps")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/keymaps'))
                
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "userdata/peripheral_data")
                fileManager.walkTree(xbmc.translatePath('special://home/userdata/peripheral_data'))
            
                #this part is an oddity
                dirs,configFiles = self.xbmc_vfs.listdir(xbmc.translatePath('special://home/userdata/'))
                for aFile in configFiles:
                    if(aFile.endswith(".xml")):
                        fileManager.addFile(xbmc.translatePath('special://home/userdata/') + aFile)

            #add to array
            self.filesTotal = fileManager.size()
            allFiles.append({"source":self.xbmc_vfs.root_path,"dest":self.remote_vfs.root_path,"files":fileManager.getFiles()})

            #check if there are custom directories
            if(utils.getSetting('backup_custom_dir') != ''):

                #create a special remote path with hash                
                self.xbmc_vfs.set_root(utils.getSetting('backup_custom_dir'))
                self.remote_vfs.mkdir(self.remote_vfs.root_path + "custom_1_" + self._createCRC(self.xbmc_vfs.root_path))
                self.remote_vfs.set_root(self.remote_vfs.root_path + "custom_1_" + self._createCRC(self.xbmc_vfs.root_path))

                fileManager.walkTree(self.xbmc_vfs.root_path)
                self.filesTotal = self.filesTotal + fileManager.size()
                allFiles.append({"source":self.xbmc_vfs.root_path,"dest":self.remote_vfs.root_path,"files":fileManager.getFiles()})

            #backup all the files
            self.filesLeft = self.filesTotal
            for fileGroup in allFiles:
                self.xbmc_vfs.set_root(fileGroup['source'])
                self.remote_vfs.set_root(fileGroup['dest'])
                self.backupFiles(fileGroup['files'],self.xbmc_vfs,self.remote_vfs)

            #remove old backups
            total_backups = int(utils.getSetting('backup_rotation'))
            if(total_backups > 0):
                
                dirs,files = self.remote_vfs.listdir(remote_base_path)
                if(len(dirs) > total_backups):
                    #remove backups to equal total wanted
                    dirs.sort()
                    remove_num = len(dirs) - total_backups - 1
                    self.filesTotal = self.filesTotal + remove_num + 1

                    #update the progress bar if it is available
                    while(remove_num >= 0 and not self._checkCancel()):
                        self._updateProgress(utils.getString(30054) + " " + dirs[remove_num])
                        utils.log("Removing backup " + dirs[remove_num])
                        self.remote_vfs.rmdir(remote_base_path + dirs[remove_num] + "/")
                        remove_num = remove_num - 1

        elif (mode == self.Restore):
            utils.log(utils.getString(30023) + " - " + utils.getString(30017))

            #for restores remote path must exist
            if(not self.remote_vfs.exists(self.remote_vfs.root_path)):
                xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30045),self.remote_vfs.root_path)
                return

            utils.log(utils.getString(30051))
            allFiles = []
            fileManager = FileManager(self.remote_vfs)
         
            #go through each of the user selected items and write them to the backup store
            if(utils.getSetting('backup_addons') == 'true'):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/addons'))
                fileManager.walkTree(self.remote_vfs.root_path + "addons")

            self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata'))

            if(utils.getSetting('backup_addon_data') == 'true'):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/addon_data'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/addon_data")

            if(utils.getSetting('backup_database') == 'true'):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/Database'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/Database")
        
            if(utils.getSetting("backup_playlists") == 'true'):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/playlists'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/playlists")
                
            if(utils.getSetting("backup_thumbnails") == "true"):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/Thumbnails'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/Thumbnails")
	  
            if(utils.getSetting("backup_config") == "true"):
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/keymaps'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/keymaps")
                
                self.xbmc_vfs.mkdir(xbmc.translatePath('special://home/userdata/peripheral_data'))
                fileManager.walkTree(self.remote_vfs.root_path + "userdata/peripheral_data")
            
                #this part is an oddity
                dirs,configFiles = self.remote_vfs.listdir(self.remote_vfs.root_path + "userdata/")
                for aFile in configFiles:
                    if(aFile.endswith(".xml")):
                        fileManager.addFile(self.remote_vfs.root_path + "userdata/" + aFile)

            #add to array
            self.filesTotal = fileManager.size()
            allFiles.append({"source":self.remote_vfs.root_path,"dest":self.xbmc_vfs.root_path,"files":fileManager.getFiles()})    

            #check if there are custom directories
            if(utils.getSetting('backup_custom_dir') != ''):

                self.xbmc_vfs.set_root(utils.getSetting('backup_custom_dir'))
                if(self.remote_vfs.exists(self.remote_vfs.root_path + "custom_1_" + self._createCRC(self.xbmc_vfs.root_path))):
                    #index files to restore
                    self.remote_vfs.set_root(self.remote_vfs.root_path + "custom_1_" + self._createCRC(self.xbmc_vfs.root_path))

                    fileManager.walkTree(self.remote_vfs.root_path)
                    self.filesTotal = self.filesTotal + fileManager.size()
                    allFiles.append({"source":self.remote_vfs.root_path,"dest":self.xbmc_vfs.root_path,"files":fileManager.getFiles()})
                else:
                    xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30045),self.remote_vfs.root_path + "custom_1_" + self._createCRC(utils.getSetting('backup_custom_dir')))

            #restore all the files
            self.filesLeft = self.filesTotal
            for fileGroup in allFiles:
                self.remote_vfs.set_root(fileGroup['source'])
                self.xbmc_vfs.set_root(fileGroup['dest'])
                self.backupFiles(fileGroup['files'],self.remote_vfs,self.xbmc_vfs)

            #call update addons to refresh everything
            xbmc.executebuiltin('UpdateLocalAddons')

        if(utils.getSetting('run_silent') == 'false' and not runSilent):
            self.progressBar.close()

    def backupFiles(self,fileList,source,dest):
        utils.log("Writing files to: " + dest.root_path)
        utils.log("Source: " + source.root_path)
        for aFile in fileList:
            if(not self._checkCancel()):
                utils.log('Writing file: ' + aFile,xbmc.LOGDEBUG)
                self._updateProgress(aFile)
                if(aFile.startswith("-")):
                    dest.mkdir(dest.root_path + aFile[len(source.root_path) + 1:])
                else:
                    if(isinstance(source,DropboxFileSystem)):
                        #if copying from dropbox we need the file handle, use get_file
                        source.get_file(aFile,dest.root_path + aFile[len(source.root_path):])
                    else:
                        #copy using normal method
                        dest.put(aFile,dest.root_path + aFile[len(source.root_path):])

    def _createCRC(self,string):
        #create hash from string
        string = string.lower()        
        bytes = bytearray(string.encode())
        crc = 0xffffffff;
        for b in bytes:
            crc = crc ^ (b << 24)          
            for i in range(8):
                if (crc & 0x80000000 ):                 
                    crc = (crc << 1) ^ 0x04C11DB7                
                else:
                    crc = crc << 1;                        
                    crc = crc & 0xFFFFFFFF
        
        return '%08x' % crc
    
    def _updateProgress(self,message=''):
        self.filesLeft = self.filesLeft - 1

        #update the progress bar
        if(self.progressBar != None):
            self.progressBar.update(int((float(self.filesTotal - self.filesLeft)/float(self.filesTotal)) * 100),message)
            
    def _checkCancel(self):
        result = False

        if(self.progressBar != None):
            result = self.progressBar.iscanceled()

        return result

class FileManager:
    fileArray = []
    not_dir = ['.zip','.xsp','.rar']
    vfs = None

    def __init__(self,vfs):
        self.vfs = vfs

    def walkTree(self,directory):
        dirs,files = self.vfs.listdir(directory)
        
        #create all the subdirs first
        for aDir in dirs:
            dirPath = xbmc.translatePath(directory + "/" + aDir)
            file_ext = aDir.split('.')[-1]
            self.addFile("-" + dirPath)  
            #catch for "non directory" type files
            if (not any(file_ext in s for s in self.not_dir)):
                self.walkTree(dirPath)  
            
        #copy all the files
        for aFile in files:
            filePath = xbmc.translatePath(directory + "/" + aFile)
            self.addFile(filePath)
                    
    def addFile(self,filename):
        try:
            filename = filename.decode('UTF-8')
        except UnicodeDecodeError:
            filename = filename.decode('ISO-8859-2')
            
        #write the full remote path name of this file
        utils.log("Add File: " + filename,xbmc.LOGDEBUG)
        self.fileArray.append(filename)

    def getFiles(self):
        result = self.fileArray
        self.fileArray = []
        return result

    def size(self):
        return len(self.fileArray)
