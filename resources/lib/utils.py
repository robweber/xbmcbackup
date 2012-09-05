import xbmc
import xbmcaddon

__addon_id__= 'script.xbmcbackup'
__Addon = xbmcaddon.Addon(__addon_id__)

#global functions for logging and encoding
def log(message,loglevel=xbmc.LOGNOTICE):
    xbmc.log(encode(__addon_id__ + ": " + message),level=loglevel)

def getSetting(name):
    return __Addon.getSetting(name)

def setSetting(name,value):
    __Addon.setSetting(name,value)
    
def getString(string_id):
    return __Addon.getLocalizedString(string_id)

def encode(string):
    return string.encode('UTF-8','replace')
