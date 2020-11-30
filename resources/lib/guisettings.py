import json
import xbmc
import xbmcvfs
from . import utils as utils


class GuiSettingsManager:
    filename = 'kodi_settings.json'
    systemSettings = None

    def __init__(self):
        # get all of the current Kodi settings
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))

        self.systemSettings = json_response['result']['settings']
    
    def backup(self):
        utils.log('Backing up Kodi settings')

        # write the settings as a json object to the addon data directory
        self._writeFile(xbmcvfs.translatePath(utils.data_dir() + self.filename), self.systemSettings)

    def restore(self):
        utils.log('Restoring Kodi settings')

        updateJson = {"jsonrpc": "2.0", "id": 1, "method": "Settings.SetSettingValue", "params": {"setting": "", "value": ""}}

        # create a setting=value dict of the current settings
        settingsDict = {}
        for aSetting in self.systemSettings:
            # ignore action types, no value
            if(aSetting['type'] != 'action'):
                settingsDict[aSetting['id']] = aSetting['value']

        # read in the settings from the recovered JSON file
        restoreSettings = self._readFile(xbmcvfs.translatePath(utils.data_dir() + self.filename))
        restoreCount = 0;
        for aSetting in restoreSettings:
            # only update a setting if its different than the current (action types have no value)
            if(aSetting['type'] != 'action' and settingsDict[aSetting['id']] != aSetting['value']):
                if(utils.getSettingBool('verbose_logging')):
                    utils.log('%s different than current: %s' % (aSetting['id'], str(aSetting['value'])))
                    
                updateJson['params']['setting'] = aSetting['id']
                updateJson['params']['value'] = aSetting['value']

                xbmc.executeJSONRPC(json.dumps(updateJson))
                restoreCount = restoreCount + 1

        utils.log('Update %d settings' % restoreCount)

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
