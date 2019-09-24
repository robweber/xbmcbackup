import xbmc
import xbmcgui
import xbmcaddon

__addon_id__= 'script.xbmcbackup'
__Addon = xbmcaddon.Addon(__addon_id__)

def data_dir():
    return __Addon.getAddonInfo('profile')

def addon_dir():
    return __Addon.getAddonInfo('path')

def openSettings():
    __Addon.openSettings()

def log(message,loglevel=xbmc.LOGDEBUG):
    xbmc.log(encode(__addon_id__ + "-" + __Addon.getAddonInfo('version') +  ": " + message),level=loglevel)

def showNotification(message):
    xbmcgui.Dialog().notification(encode(getString(30010)),encode(message),time=4000,icon=xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/images/icon.png"))

def getSetting(name):
    return __Addon.getSetting(name)

def setSetting(name,value):
    __Addon.setSetting(name,value)
    
def getString(string_id):
    return __Addon.getLocalizedString(string_id)

def getRegionalTimestamp(date_time,dateformat=['dateshort']):
    result = ''
    
    for aFormat in dateformat:
        result = result + ("%s " % date_time.strftime(xbmc.getRegion(aFormat)))
        
    return result.strip()

def encode(string):
    result = ''

    try:
        result = string.encode('UTF-8','replace')
    except UnicodeDecodeError:
        result = 'Unicode Error'
    
    return result
