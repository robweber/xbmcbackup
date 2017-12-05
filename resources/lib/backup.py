import xbmc
import xbmcgui
import xbmcvfs
import utils as utils
import time
import json
from vfs import XBMCFileSystem,DropboxFileSystem,ZipFileSystem,GoogleDriveFilesystem
from progressbar import BackupProgressBar
from resources.lib.guisettings import GuiSettingsManager
from resources.lib.extractor import ZipExtractor
from resources.lib.advanced_editor import BackupSetManager

def folderSort(aKey):
    result = aKey[0]
    
    if(len(result) < 8):
        result = result + "0000"

    return result
    

class XbmcBackup:
    #constants for initiating a back or restore
    Backup = 0
    Restore = 1

    #list of dirs for the "simple" file selection
    simple_directory_list = ['addons','addon_data','database','playlists','profiles','thumbnails','config']

    #file systems
    xbmc_vfs = None
    remote_vfs = None
    saved_remote_vfs = None
    
    restoreFile = None
    remote_base_path = None
    
    #for the progress bar
    progressBar = None
    filesLeft = 0
    filesTotal = 1

    fileManager = None
    restore_point = None
    skip_advanced = False   #if we should check for the existance of advancedsettings in the restore
    
    def __init__(self):
        self.xbmc_vfs = XBMCFileSystem(xbmc.translatePath('special://home'))

        self.configureRemote()
        utils.log(utils.getString(30046))

    def configureRemote(self):
        if(utils.getSetting('remote_selection') == '1'):
            self.remote_base_path = utils.getSetting('remote_path_2');
            self.remote_vfs = XBMCFileSystem(utils.getSetting('remote_path_2'))
            utils.setSetting("remote_path","")
        elif(utils.getSetting('remote_selection') == '0'):
            self.remote_base_path = utils.getSetting('remote_path');
            self.remote_vfs = XBMCFileSystem(utils.getSetting("remote_path"))
        elif(utils.getSetting('remote_selection') == '2'):
            self.remote_base_path = "/"
            self.remote_vfs = DropboxFileSystem("/")
        elif(utils.getSetting('remote_selection') == '3'):
            self.remote_base_path = '/Kodi Backup/'
            self.remote_vfs = GoogleDriveFilesystem('/Kodi Backup/')

    def remoteConfigured(self):
        result = True

        if(self.remote_base_path == ""):
            result = False

        return result

    def listBackups(self):
        result = []

        #get all the folders in the current root path
        dirs,files = self.remote_vfs.listdir(self.remote_base_path)
    
        for aDir in dirs:
            if(self.remote_vfs.exists(self.remote_base_path + aDir + "/xbmcbackup.val")):

                #folder may or may not contain time, older versions didn't include this
                folderName = ''
                if(len(aDir) > 8):
                    folderName = aDir[6:8] + '-' + aDir[4:6] + '-' + aDir[0:4] + " " + aDir[8:10] + ":" + aDir[10:12]
                else:
                    folderName = aDir[6:8] + '-' + aDir[4:6] + '-' + aDir[0:4]

                result.append((aDir,folderName))

        for aFile in files:
            file_ext = aFile.split('.')[-1]
            folderName = utils.encode(aFile.split('.')[0])
            
            if(file_ext == 'zip' and (len(folderName) == 12 or len(folderName) == 8) and str.isdigit(folderName)):
                
                #folder may or may not contain time, older versions didn't include this
                if(len(aFile ) > 8):
                    folderName = aFile [6:8] + '-' + aFile [4:6] + '-' + aFile [0:4] + " " + aFile [8:10] + ":" + aFile [10:12]
                else:
                    folderName = aFile [6:8] + '-' + aFile [4:6] + '-' + aFile [0:4]

                result.append((aFile ,folderName))
                

        result.sort(key=folderSort)
        
        return result

    def selectRestore(self,restore_point):
        self.restore_point = restore_point

    def skipAdvanced(self):
        self.skip_advanced = True

    def run(self,mode=-1,progressOverride=False):
        #set windows setting to true
        window = xbmcgui.Window(10000)
        window.setProperty(utils.__addon_id__ + ".running","true")
        
        #append backup folder name
        progressBarTitle = utils.getString(30010) + " - "
        if(mode == self.Backup and self.remote_vfs.root_path != ''):
            if(utils.getSetting("compress_backups") == 'true'):
                #delete old temp file
                if(self.xbmc_vfs.exists(xbmc.translatePath('special://temp/xbmc_backup_temp.zip'))):
                    if(not self.xbmc_vfs.rmfile(xbmc.translatePath('special://temp/xbmc_backup_temp.zip'))):
                        #we had some kind of error deleting the old file
                        xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30096),utils.getString(30097))
                        return
                    
                #save the remote file system and use the zip vfs
                self.saved_remote_vfs = self.remote_vfs
                self.remote_vfs = ZipFileSystem(xbmc.translatePath("special://temp/xbmc_backup_temp.zip"),"w")
                
            self.remote_vfs.set_root(self.remote_vfs.root_path + time.strftime("%Y%m%d%H%M") + "/")
            progressBarTitle = progressBarTitle + utils.getString(30023) + ": " + utils.getString(30016)
        elif(mode == self.Restore and self.restore_point != None and self.remote_vfs.root_path != ''):
            if(self.restore_point.split('.')[-1] != 'zip'):
                self.remote_vfs.set_root(self.remote_vfs.root_path + self.restore_point + "/")
            progressBarTitle = progressBarTitle + utils.getString(30023) + ": " + utils.getString(30017)
        else:
            #kill the program here
            self.remote_vfs = None
            return

        utils.log(utils.getString(30047) + ": " + self.xbmc_vfs.root_path)
        utils.log(utils.getString(30048) + ": " + self.remote_vfs.root_path)

        
        #setup the progress bar
        self.progressBar = BackupProgressBar(progressOverride)
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

            #read in a list of the directories to backup
            selectedDirs = self._readBackupConfig(utils.addon_dir() + "/resources/data/default_files.json")

            utils.log(utils.getString(30051))
            allFiles = []
            fileManager = FileManager(self.xbmc_vfs)

            if(utils.getSetting('backup_selection_type') == 0):
                #simple mode - get file listings for all enabled directories
                for aDir in self.simple_directory_list:
                    #if this dir enabled
                    if(utils.getSetting('backup_' + aDir) == 'true'):
                        #get a file listing and append it to the allfiles array
                        allFiles.append(self._addBackupDir(aDir,xbmc.translatePath(selectedDirs[aDir]['root']),selectedDirs[aDir]['dirs']))
            else:
                #advanced mode - open custom editor
                setManager = BackupSetManager()

                #go through the custom sets
                for index in range(0,len(setManager.getSets())):
                    #get the set
                    aSet = setManager.getSet(index)
                    utils.log(str(aSet))
                    #get file listing and append
                    allFiles.append(self._addBackupDir(aSet['name'],xbmc.translatePath(aSet['set']['root']),aSet['set']['dirs']))
                
            #create a validation file for backup rotation
            writeCheck = self._createValidationFile(allFiles)
            
            if(not writeCheck):
                #we may not be able to write to this destination for some reason
                shouldContinue = xbmcgui.Dialog().yesno(utils.getString(30089),utils.getString(30090), utils.getString(30044),autoclose=25000)
                
                if(not shouldContinue):
                    return

            orig_base_path = self.remote_vfs.root_path
            
            #backup all the files
            self.filesLeft = self.filesTotal
            for fileGroup in allFiles:
                self.xbmc_vfs.set_root(fileGroup['source'])
                self.remote_vfs.set_root(fileGroup['dest'] + fileGroup['name'])
                filesCopied = self.backupFiles(fileGroup['files'],self.xbmc_vfs,self.remote_vfs)
                
                if(not filesCopied):
                    utils.showNotification(utils.getString(30092))
                    utils.log(utils.getString(30092))
            
            #reset remote and xbmc vfs
            self.xbmc_vfs.set_root("special://home/")
            self.remote_vfs.set_root(orig_base_path)

            if(utils.getSetting("compress_backups") == 'true'):
                #send the zip file to the real remote vfs
                zip_name = self.remote_vfs.root_path[:-1] + ".zip"
                self.remote_vfs.cleanup()
                self.xbmc_vfs.rename(xbmc.translatePath("special://temp/xbmc_backup_temp.zip"), xbmc.translatePath("special://temp/" + zip_name))
                fileManager.addFile(xbmc.translatePath("special://temp/" + zip_name))
               
                #set root to data dir home 
                self.xbmc_vfs.set_root(xbmc.translatePath("special://temp/"))
               
                self.remote_vfs = self.saved_remote_vfs
                self.progressBar.updateProgress(98, utils.getString(30088))
                fileCopied = self.backupFiles(fileManager.getFiles(),self.xbmc_vfs, self.remote_vfs)
                
                if(not fileCopied):
                    #zip archive copy filed, inform the user
                    shouldContinue = xbmcgui.Dialog().ok(utils.getString(30089),utils.getString(30090), utils.getString(30091))
                    
                #delete the temp zip file
                self.xbmc_vfs.rmfile(xbmc.translatePath("special://temp/" + zip_name))

            #remove old backups
            self._rotateBackups()

        elif (mode == self.Restore):
            utils.log(utils.getString(30023) + " - " + utils.getString(30017))

            #catch for if the restore point is actually a zip file
            if(self.restore_point.split('.')[-1] == 'zip'):
                self.progressBar.updateProgress(2, utils.getString(30088))
                utils.log("copying zip file: " + self.restore_point)
                
                #set root to data dir home 
                self.xbmc_vfs.set_root(xbmc.translatePath("special://temp/"))
                
                if(not self.xbmc_vfs.exists(xbmc.translatePath("special://temp/" + self.restore_point))):
                    #copy just this file from the remote vfs
                    zipFile = []
                    zipFile.append(self.remote_base_path + self.restore_point)
               
                    self.backupFiles(zipFile,self.remote_vfs, self.xbmc_vfs)
                else:
                    utils.log("zip file exists already")
                
                #extract the zip file
                zip_vfs = ZipFileSystem(xbmc.translatePath("special://temp/"+ self.restore_point),'r')
                extractor = ZipExtractor()
                
                if(not extractor.extract(zip_vfs, xbmc.translatePath("special://temp/"), self.progressBar)):
                    #we had a problem extracting the archive, delete everything
                    zip_vfs.cleanup()
                    self.xbmc_vfs.rmfile(xbmc.translatePath("special://temp/" + self.restore_point))
                    
                    xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30101))
                    return
                    
                zip_vfs.cleanup()
                
                self.progressBar.updateProgress(0,utils.getString(30049) + "......")
                #set the new remote vfs and fix xbmc path
                self.remote_vfs = XBMCFileSystem(xbmc.translatePath("special://temp/" + self.restore_point.split(".")[0] + "/"))
                self.xbmc_vfs.set_root(xbmc.translatePath("special://home/"))
            
            #for restores remote path must exist
            if(not self.remote_vfs.exists(self.remote_vfs.root_path)):
                xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30045),self.remote_vfs.root_path)
                return

            valFile = self._checkValidationFile(self.remote_vfs.root_path)
            if(valFile == None):
                #don't continue
                return

            utils.log(utils.getString(30051))
            allFiles = []
            fileManager = FileManager(self.remote_vfs)
         
            #check for the existance of an advancedsettings file
            if(self.remote_vfs.exists(self.remote_vfs.root_path + "config/advancedsettings.xml") and not self.skip_advanced):
                #let the user know there is an advanced settings file present
                restartXbmc = xbmcgui.Dialog().yesno(utils.getString(30038),utils.getString(30039),utils.getString(30040), utils.getString(30041))

                if(restartXbmc):
                    #add only this file to the file list
                    fileManager.addFile(self.remote_vfs.root_path + "config/advancedsettings.xml")
                    self.backupFiles(fileManager.getFiles(),self.remote_vfs,self.xbmc_vfs)

                    #let the service know to resume this backup on startup
                    self._createResumeBackupFile()

                    #do not continue running
                    xbmcgui.Dialog().ok(utils.getString(30077),utils.getString(30078)) 
                    return

            #go through each of the directories in the backup and write them to the correct location
            for aDir in valFile['directories']:
                self.xbmc_vfs.set_root(aDir['path'])
                if(self.remote_vfs.exists(self.remote_vfs.root_path + aDir['name'] + '/')):
                    #walk the directory
                    fileManager.walkTree(self.remote_vfs.root_path + aDir['name'] + '/')
                    self.filesTotal = self.filesTotal + fileManager.size()
                    allFiles.append({"source":self.remote_vfs.root_path + aDir['name'],"dest":self.xbmc_vfs.root_path,"files":fileManager.getFiles()}) 
                else:
                    utils.log("error path not found: " + self.remote_vfs.root_path + aDir['name'])
                    xbmcgui.Dialog().ok(utils.getString(30010),utils.getString(30045),self.remote_vfs.root_path + aDir['name'])

            #restore all the files
            self.filesLeft = self.filesTotal
            for fileGroup in allFiles:
                self.remote_vfs.set_root(fileGroup['source'])
                self.xbmc_vfs.set_root(fileGroup['dest'])
                self.backupFiles(fileGroup['files'],self.remote_vfs,self.xbmc_vfs)

            self.progressBar.updateProgress(99,"Clean up operations .....")

            if(self.restore_point.split('.')[-1] == 'zip'):
                #delete the zip file and the extracted directory
                self.xbmc_vfs.rmfile(xbmc.translatePath("special://temp/" + self.restore_point))
                self.xbmc_vfs.rmdir(self.remote_vfs.root_path)

            if(utils.getSetting("backup_config") == "true"):
                #update the guisettings information (or what we can from it)
                gui_settings = GuiSettingsManager('special://home/userdata/guisettings.xml')
                gui_settings.run()

            #call update addons to refresh everything
            xbmc.executebuiltin('UpdateLocalAddons')

        self.xbmc_vfs.cleanup()
        self.remote_vfs.cleanup()
        self.progressBar.close()

        #reset the window setting
        window.setProperty(utils.__addon_id__ + ".running","")

    def backupFiles(self,fileList,source,dest):
        result = True
        
        utils.log("Writing files to: " + dest.root_path)
        utils.log("Source: " + source.root_path)
        for aFile in fileList:
            if(not self.progressBar.checkCancel()):
                utils.log('Writing file: ' + aFile,xbmc.LOGDEBUG)
                if(aFile.startswith("-")):
                    self._updateProgress(aFile[len(source.root_path) + 1:])
                    dest.mkdir(dest.root_path + aFile[len(source.root_path) + 1:])
                else:
                    self._updateProgress()
                    wroteFile = True
                    if(isinstance(source,DropboxFileSystem) or isinstance(source,GoogleDriveFilesystem)):
                        #if copying from cloud storage we need the file handle, use get_file
                        wroteFile = source.get_file(aFile,dest.root_path + aFile[len(source.root_path):])
                    else:
                        #copy using normal method
                        wroteFile = dest.put(aFile,dest.root_path + aFile[len(source.root_path):])
                    
                    #if result is still true but this file failed
                    if(not wroteFile and result):
                        result = False
                        
                        
        return result

    def _addBackupDir(self,folder_name,root_path,dirList):
        fileManager = FileManager(self.xbmc_vfs)
  
        self.xbmc_vfs.set_root(root_path)
        for aDir in dirList:
            fileManager.addDir(aDir)

        self.filesTotal = self.filesTotal + fileManager.size()

        return {"name":folder_name,"source":self.xbmc_vfs.root_path,"dest":self.remote_vfs.root_path,"files":fileManager.getFiles()}
            

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

    def _updateProgress(self,message=None):
        self.filesLeft = self.filesLeft - 1
        self.progressBar.updateProgress(int((float(self.filesTotal - self.filesLeft)/float(self.filesTotal)) * 100),message)

    def _rotateBackups(self):
        total_backups = int(utils.getSetting('backup_rotation'))
        
        if(total_backups > 0):
            #get a list of valid backup folders
            dirs = self.listBackups()
            
            if(len(dirs) > total_backups):
                #remove backups to equal total wanted
                remove_num = 0
                self.filesTotal = self.filesTotal + remove_num + 1

                #update the progress bar if it is available
                while(remove_num < (len(dirs) - total_backups) and not self.progressBar.checkCancel()):
                    self._updateProgress(utils.getString(30054) + " " + dirs[remove_num][1])
                    utils.log("Removing backup " + dirs[remove_num][0])
                    
                    if(dirs[remove_num][0].split('.')[-1] == 'zip'):
                        #this is a file, remove it that way
                        self.remote_vfs.rmfile(self.remote_base_path + dirs[remove_num][0])
                    else:
                        self.remote_vfs.rmdir(self.remote_base_path + dirs[remove_num][0] + "/")
                        
                    remove_num = remove_num + 1

    def _createValidationFile(self,dirList):
        valInfo = {"name":"XBMC Backup Validation File","xbmc_version":xbmc.getInfoLabel('System.BuildVersion'),"type":0}
        valDirs = []
        
        for aDir in dirList:
            valDirs.append({"name":aDir['name'],"path":aDir['source']})
        valInfo['directories'] = valDirs
        
        vFile = xbmcvfs.File(xbmc.translatePath(utils.data_dir() + "xbmcbackup.val"),'w')
        vFile.write(json.dumps(valInfo))
        vFile.write("")
        vFile.close()

        success = self.remote_vfs.put(xbmc.translatePath(utils.data_dir() + "xbmcbackup.val"),self.remote_vfs.root_path + "xbmcbackup.val")
        
        #remove the validation file
        xbmcvfs.delete(xbmc.translatePath(utils.data_dir() + "xbmcbackup.val"))
        
        return success

    def _checkValidationFile(self,path):
        result = None
        
        #copy the file and open it
        self.xbmc_vfs.put(path + "xbmcbackup.val",xbmc.translatePath(utils.data_dir() + "xbmcbackup_restore.val"))

        vFile = xbmcvfs.File(xbmc.translatePath(utils.data_dir() + "xbmcbackup_restore.val"),'r')
        jsonString = vFile.read()
        vFile.close()

        #delete after checking
        xbmcvfs.delete(xbmc.translatePath(utils.data_dir() + "xbmcbackup_restore.val"))

        try:
            result = json.loads(jsonString)

            if(xbmc.getInfoLabel('System.BuildVersion') != result['xbmc_version']):
                shouldContinue = xbmcgui.Dialog().yesno(utils.getString(30085),utils.getString(30086),utils.getString(30044))

                if(not shouldContinue):
                    result = None
                
        except ValueError:
            #may fail on older archives
            result = None

        return result

    def _createResumeBackupFile(self):
        rFile = xbmcvfs.File(xbmc.translatePath(utils.data_dir() + "resume.txt"),'w')
        rFile.write(self.restore_point)
        rFile.close()

    def _readBackupConfig(self,aFile):
        jFile = xbmcvfs.File(xbmc.translatePath(aFile),'r')
        jsonString = jFile.read()
        jFile.close()
        return json.loads(jsonString)

class FileManager:
    not_dir = ['.zip','.xsp','.rar']
    exclude_dir = []
    
    def __init__(self,vfs):
        self.vfs = vfs
        self.fileArray = []

    def walkTree(self,directory,recurse=True):
        
        if(directory[-1:] == '/' or directory[-1:] == '\\'):
            directory = directory[:-1]
       
        if(self.vfs.exists(directory + "/")):
            dirs,files = self.vfs.listdir(directory)

            if(recurse):
                #create all the subdirs first
                for aDir in dirs:
                    dirPath = xbmc.validatePath(xbmc.translatePath(directory + "/" + aDir))
                    file_ext = aDir.split('.')[-1]

                    if(not dirPath in self.exclude_dir):
                    
                        self.addFile("-" + dirPath)

                        #catch for "non directory" type files
                        shouldWalk = True

                        for s in file_ext:
                            if(s in self.not_dir):
                                shouldWalk = False
                
                        if(shouldWalk):
                            self.walkTree(dirPath)  
            
            #copy all the files
            for aFile in files:
                filePath = xbmc.translatePath(directory + "/" + aFile)
                self.addFile(filePath)

    def addDir(self,dirMeta):
        if(dirMeta['type'] == 'include'):
            self.addFile('-' + xbmc.translatePath(dirMeta['path']))
            self.walkTree(xbmc.translatePath(dirMeta['path']),dirMeta['recurse'])
        else:
            self.excludeFile('-' + xbmc.translatePath(dirMeta['path']))
            
    def addFile(self,filename):
        try:
            filename = filename.decode('UTF-8')
        except UnicodeDecodeError:
            filename = filename.decode('ISO-8859-2')
            
        #write the full remote path name of this file
        utils.log("Add File: " + filename,xbmc.LOGDEBUG)
        self.fileArray.append(filename)

    def excludeFile(self,filename):
        try:
            filename = filename.decode('UTF-8')
        except UnicodeDecodeError:
            filename = filename.decode('ISO-8859-2')
            
        #write the full remote path name of this file
        utils.log("Exclude File: " + filename,xbmc.LOGDEBUG)
        self.exclude_dir.append(filename)

    def getFiles(self):
        result = self.fileArray
        self.fileArray = []
        return result

    def size(self):
        return len(self.fileArray)
