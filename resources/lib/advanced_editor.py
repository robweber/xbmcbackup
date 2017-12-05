import json
import utils as utils
import xbmcvfs
import xbmc
import xbmcgui

class BackupSetManager:
    jsonFile = xbmc.translatePath(utils.data_dir() + "custom_paths.json")
    paths = None
    
    def __init__(self):
        self.paths = {}
        
        #try and read in the custom file
        self._readFile()

    def addSet(self,aSet):
        self.paths[aSet['name']] = {'root':aSet['root'],'dirs':[{"type":"include","path":aSet['root'],'recurse':True}]}

        #save the file
        self._writeFile()

    def updateSet(self,name,aSet):
        self.paths[name] = aSet

        #save the file
        self._writeFile()

    def deleteSet(self,index):
        #match the index to a key
        keys = self.getSets()

        #delete this set
        del self.paths[keys[index]]

        #save the file
        self._writeFile()
    
    def getSets(self):
        #list all current sets by name
        keys = self.paths.keys()
        keys.sort()

        return keys

    def getSet(self,index):
        keys = self.getSets();

        #return the set at this index
        return {'name':keys[index],'set':self.paths[keys[index]]}

    def _writeFile(self):
        #create the custom file
        aFile = xbmcvfs.File(self.jsonFile,'w')
        aFile.write(json.dumps(self.paths))
        aFile.close()
    
    def _readFile(self):
        
        if(xbmcvfs.exists(self.jsonFile)):

            #read in the custom file
            aFile = xbmcvfs.File(self.jsonFile)

            #load custom dirs
            self.paths = json.loads(aFile.read())
            aFile.close()
        else:
            #write a blank file
            self._writeFile()

class AdvancedBackupEditor:
    dialog = None

    def __init__(self):
        self.dialog = xbmcgui.Dialog()

    def createSet(self):
        backupSet = None
    
        name = self.dialog.input("Set Name",defaultt='Backup Set')

        if(name != ''):

            #give a choice to start in home or enter a root path
            enterHome = self.dialog.yesno('Root folder selection',line1='Browse Folder - starts in Kodi home',line2='Enter Own - enter path to start there',nolabel='Browse Folder',yeslabel='Enter Own')

            rootFolder = 'special://home'
            if(enterHome):
                rootFolder = self.dialog.input('Enter root path',defaultt=rootFolder)

                #check that this path even exists
                if(not xbmcvfs.exists(xbmc.translatePath(rootFolder))):
                    self.dialog.ok('Path Error','Path does not exist',rootFolder)
            else:
                #select path to start set
                rootFolder = self.dialog.browse(type=0,heading="Select Root",shares='files',defaultt=rootFolder)

            backupSet = {'name':name,'root':rootFolder}
    
        return backupSet

    def editSet(self,name,backupSet):
        optionSelected = ''
    
        while(optionSelected != -1):
            options = ['Add Exclusion','Root: ' + backupSet['root']]

            for aDir in backupSet['dirs']:
                if(aDir['type'] == 'exclude'):
                    options.append('Exclude: ' + aDir['path'])

            optionSelected = self.dialog.select('Edit ' + name,options)

            if(optionSelected == 0):
                #add an exclusion
                excludeFolder = self.dialog.browse(type=0,heading="Add Exclusion",shares='files',defaultt=backupSet['root'])

                #will equal root if cancel is hit
                if(excludeFolder != backupSet['root']):
                    backupSet['dirs'].append({"path":excludeFolder,"type":"exclude"})
            elif(optionSelected == 1):
                self.dialog.ok('Root Folder','The root folder cannot be changed',backupSet['root'])
            elif(optionSelected > 1):
                #remove exclusion folder
                del backupSet['dirs'][optionSelected - 2]

        return backupSet
    

    def showMainScreen(self):
        exitCondition = ""
        customPaths = BackupSetManager()

        #show this every time
        self.dialog.ok('Disclaimer','Canceling this menu will close and save changes')
 
        while(exitCondition != -1):
            #load the custom paths
            options = ['Add Set']
        
            for aPath in customPaths.getSets():
                options.append(aPath)
            
            #show the gui
            exitCondition = self.dialog.select('Advanced Editor',options)
        
            if(exitCondition >= 0):
                if(exitCondition == 0):
                    newSet = self.createSet()

                    customPaths.addSet(newSet)
                else:
                    #bring up a context menu
                    menuOption = self.dialog.select(heading="Choose Action",list=['Edit','Delete'],preselect=0)

                    if(menuOption == 0):
                        #get the set
                        aSet = customPaths.getSet(exitCondition -1)

                        #edit the set
                        updatedSet = self.editSet(aSet['name'],aSet['set'])

                        #save it
                        customPaths.updateSet(aSet['name'],updatedSet)
                    
                    elif(menuOption == 1):
                        if(self.dialog.yesno(heading="Delete Set",line1="Are you sure you want to delete?")):
                            #delete this path - subtract one because of "add" item
                            customPaths.deleteSet(exitCondition -1)
              

