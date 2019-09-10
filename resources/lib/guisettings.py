import utils as utils
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import json
import xbmc,xbmcvfs


class GuiSettingsManager:
    settingsFile = None
    doc = None
    
    def __init__(self,settingsFile):
        self._readFile(xbmc.translatePath(settingsFile))
    
    def run(self):
        #get a list of all the settings we can manipulate via json
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))
        
        settings = json_response['result']['settings']
        settingsAllowed = []
        
        for aSetting in settings:
            settingsAllowed.append(aSetting['id'])
            
        #parse the existing xml file and get all the settings we need to update
        updateSettings = self.__parseNodes(self.doc.getElementsByTagName('setting'))
        
        #go through all the found settings and update them
        for aSetting in updateSettings:
            if(aSetting.name in settingsAllowed):
                utils.log("updating: " + aSetting.name + ", value: " + aSetting.value)
            
                #check for boolean and numeric values
                if(aSetting.value.isdigit() or (aSetting.value == 'true' or aSetting.value == 'false')):
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.SetSettingValue","params":{"setting":"' + aSetting.name + '","value":' + aSetting.value + '}}')
                else:
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.SetSettingValue","params":{"setting":"' + aSetting.name + '","value":"' + utils.encode(aSetting.value) + '"}}')
                
        #make a copy of the guisettings file to make user based restores easier
        xbmcvfs.copy(self.settingsFile, xbmc.translatePath("special://home/userdata/guisettings.xml.restored"))
            
    def __parseNodes(self,nodeList):
        result = []

        for node in nodeList:
            #only add if it's not a default setting
            if('default' not in node.attributes.keys()):
                aSetting = SettingNode(node.getAttribute('id'),node.firstChild.nodeValue)
                aSetting.isDefault = False

                result.append(aSetting)
            
        return result
    
    def _readFile(self,fileLoc):
        
        if(xbmcvfs.exists(fileLoc)):
            try:
                self.doc = minidom.parse(fileLoc)
                self.settingsFile = fileLoc
            except ExpatError:
                utils.log("Can't read " + fileLoc)
                
class SettingNode:
    name = ''
    value = ''
    isDefault = True
    
    def __init__(self,name,value):
        self.name = name
        self.value= value
        
    def __str__(self):
        return "%s : %s" % (self.name,self.value)
    
    def __repr__(self):
        return self.__str__()
                
        
