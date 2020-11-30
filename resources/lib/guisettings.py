import json
import xbmc
import xbmcvfs
from . import utils as utils
from xml.dom import minidom
from xml.parsers.expat import ExpatError


class GuiSettingsManager:
    filename = 'kodi_settings.json'
        
    def backup(self):
        utils.log('Backing up Kodi settings')
        
        # get all of the current Kodi settings
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))

        # write the settings as a json object to the addon data directory
        self._writeFile(xbmcvfs.translatePath(utils.data_dir() + self.filename), json_response['result']['settings'])

    def restore(self):
        utils.log('Restoring Kodi settings')

        # read in the settings from the recovered JSON file
        restoreSettings = self._readFile(xbmcvfs.translatePath(utils.data_dir() + self.filename))

        for aSetting in restoreSettings:
            if(aSetting['type'] != 'action'):
                utils.log('%s : %s' % (aSetting['id'], aSetting['type']))

    def run(self):
        # get all of the current Kodi settings
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))

        settings = json_response['result']['settings']
        currentSettings = {}

        for aSetting in settings:
            if('value' in aSetting):
                currentSettings[aSetting['id']] = aSetting['value']

        # parse the existing xml file and get all the settings we need to restore
        restoreSettings = self.__parseNodes(self.doc.getElementsByTagName('setting'))

        # get a list where the restore setting value != the current value
        updateSettings = {k: v for k, v in list(restoreSettings.items()) if (k in currentSettings and currentSettings[k] != v)}

        # go through all the found settings and update them
        jsonObj = {"jsonrpc": "2.0", "id": 1, "method": "Settings.SetSettingValue", "params": {"setting": "", "value": ""}}
        for anId, aValue in list(updateSettings.items()):
            utils.log("updating: " + anId + ", value: " + str(aValue))

            jsonObj['params']['setting'] = anId
            jsonObj['params']['value'] = aValue

            xbmc.executeJSONRPC(json.dumps(jsonObj))

    def _readFile(self, fileLoc):
        result = []
        
        if(xbmcvfs.exists(fileLoc)):
            with xbmcvfs.File(fileLoc, 'r') as vFile:
                result = json.loads(vFile.read())

        return result

    def _writeFile(self, fileLoc, jsonData):
        sFile = xbmcvfs.File(fileLoc, 'w')
        sFile.write(json.dumps(jsonData))
        sFile.write("")
        sFile.close()
