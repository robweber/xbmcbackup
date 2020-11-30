import json
import xbmc
import xbmcvfs
from . import utils as utils
from xml.dom import minidom
from xml.parsers.expat import ExpatError


class GuiSettingsManager:
    filename = 'kodi_settings.json'
    doc = None

    def __init__(self):
        # first make a copy of the file
        xbmcvfs.copy(xbmcvfs.translatePath('special://home/userdata/guisettings.xml'), xbmcvfs.translatePath("special://home/userdata/guisettings.xml.restored"))

        # read in the copy
        self._readFile(xbmcvfs.translatePath('special://home/userdata/guisettings.xml.restored'))

    def backup(self):
        # get all of the current Kodi settings
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettings","params":{"level":"advanced"}}'))

        # write the settings as a json object to the addon data directory
        sFile = xbmcvfs.File(xbmcvfs.translatePath(utils.data_dir() + self.filename), 'w')
        sFile.write(json.dumps(json_response['result']['settings']))
        sFile.write("")
        sFile.close()

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

    def __parseNodes(self, nodeList):
        result = {}

        for node in nodeList:
            nodeValue = ''
            if(node.firstChild is not None):
                nodeValue = node.firstChild.nodeValue

            # check for numbers and booleans
            if(nodeValue.isdigit()):
                nodeValue = int(nodeValue)
            elif(nodeValue == 'true'):
                nodeValue = True
            elif(nodeValue == 'false'):
                nodeValue = False

            result[node.getAttribute('id')] = nodeValue

        return result

    def _readFile(self, fileLoc):

        if(xbmcvfs.exists(fileLoc)):
            try:
                self.doc = minidom.parse(fileLoc)
            except ExpatError:
                utils.log("Can't read " + fileLoc)
