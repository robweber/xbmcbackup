import xbmc
import xbmcvfs
import json
import utils as utils

class BackupAddonManager:
    addons = None
    restored = None
    
    def __init__(self):
        #get a list of addons
        json_response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddons","params":{"properties":["dependencies","enabled","name"]}}'))

        if(json_response['result']['addons'] != None):
            self.addons = json_response['result']['addons']
        else:
            self.addons = []


    def getEnabled(self):
        #get a list of enabled addons
        result = [x for x in self.addons if x['enabled'] == True]

        return result

    def setRestored(self,restored):
        #create a dict from this list
        self.restored = {x['addonid']:x for x in restored}

    def restore(self):
        updateOrder = []
        
        #create a list of addons to enable, in order
        for name,addon in self.restored.items():

            #TODO check for dependencies
            updateOrder.append(name)

        for addon in updateOrder:
            xbmc.executeJSONRPC(('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":true}}') % (addon))
            #utils.log(('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":true}}') % (addon))

        
        
        
                
