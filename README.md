# Backup Addon

## About
I've had to recover my database, thumbnails, and source configuration enough times that I just wanted a quick easy way to back them up. That is what this addon is meant to do. 

## Configuration

These options are found in the Settings area of the addon and should be setup prior to using. 

### General

These are general settings regarding how backups are performed, maintained, and displayed. 

* Compress Archives - this will put the backup contents in a zip folder. See notes below regarding how this works in more detail. 
* Backups to Keep - You can keep a set number of backups by setting the integer value of this setting greater than 0. 
* Progress Display - the type of progress bar you want to display, or none if you don't want to see th progress of the backup. 

If you choose to compress your backups there are a few things you need to be aware of. Compressing takes place on the server you are trying to backup and then only the archive is copied to the remote backup location. This means you must have sufficient space available to allow for creating the archive. When restoring a zipped archive the process is the same. It is first copied to your local storage, extracted, and the contents put to their correct locations. The archive is then deleted. Zipped and non-zipped backups can be mixed in the same archive folder.  

### Remote Directories

Here is where you setup the remote path the backup files will be copied to. Each backup will create a folder named in a YYYYMMDDHHmm format so you can create multiple backups. The options currently available are: 

* Browse Path - just browse for a path that Kodi can see via the normal network browser. 
* Type Path - similar to browsing but you type the full path, including "smb://" or "nfs://" protocols as appropriate. See the [Kodi file sharing](http://kodi.wiki/view/File_sharing) page for more info on how to setup file share strings correctly. 
* Dropbox - link the addon to your Dropbox account, see more info below on this. 
* Google Drive - link the addon to your Google Drive account, see more info below on this. 

### File Selection Options

Here you can select the items from your user profile folder that will be sent to the backup location. By default all are turned on except the Addon Data directory. You can also define non-Kodi directories on your device. See "Custom Directories" for more information on how these are handled. 

Here is a breakdown of the file selection options available in the settings. More information about Kodi file paths can be found on [the wiki](http://kodi.wiki/view/Special_protocol)

* User Addons - these are all the addon files located in the main Kodi addons folder. The path is special://home/addons
* Addon Data - this is data saved by addons when changing their settings. The path is special://home/userdata/addon_data
* Database - these are the local Kodi SQLlite databases. Even if using the SQL database there are other DB files such as Addons.db that you would want in this folder. The path is special://home/userdata/Database
* Playlist - Playlists that are created in Kodi. The path is special://home/userdata/playlists
* Profiles - Any files in the profiles folder. Keep in mind this currently includes all database, thumnail and config files in here. The path is special://home/userdata/profiles
* Thumbnails/Fanart - the folder where all thumbnails and fanart is stored. The path is special://home/userdata/Thumbnails
* Config Files - config files refer to a collection of files that Kodi uses for information. This includes the keymaps and peripheral_data, and library directories in the userdata folder. It also includes all the XML files in the root of the userdata directory such as sources.xml, guisettings.xml, favorites.xml, advancedsettings.xml and others. For a full list of files in this directory see the [UserData folder wiki page](http://kodi.wiki/view/The_UserData_Folder)

### Custom Directories

You can define custom directories that are not a part of your Kodi folder structure for backup. These create a "custom_hash" folder in your backup destination. The hash for these folders is very important. During a restore if the hash of the file path in Custom 1 does not match the hash in the restore folder it will not move the files. This is to prevent files from being restored to the wrong location in the event you change file paths in the addon settings. A dialog box will let you know if file paths do not match up. 

Up to 2 Custom directories can be specified. 

## Running the Program

Running the program will allow you to select Backup or Restore as a running mode. Selecting Backup will push files to your remote store using the addon settings you defined. Selecting Restore will give you a list of restore points currently in your remote destination. Selecting one will pull the files matching your selection criteria from the restore point to your local Kodi folders. 

### Restores

During the restore process there are a few checks and post-run procedures to know about. 

The first is a version check. If you are restoring to a different version of Kodi than the one used to create the backup archive you'll get a warning. In most cases it is OK to proceed, just know that some specific items like addons and database files may not work correctly.

The next check is for an advancedsettings.xml file. If you've created this file and it exists in your restore archive you'll be asked to reboot Kodi. This is so that the file can be loaded and used for any special settings, mainly path substitutions, you may have had that would affect the rest of the restore. The Backup addon will prompt you to continue the restore process when you reboot the program. 

The last bit of post-processing is done after all the backup files have been restored. If you have restored your configuration files the addon will attempt to restore any system specific settings that it can from the guisettings.xml file. This is done by comparing the restored file with settings via the JSONPRC Settings.SetSettingValue method. Only system specific settings can be restored so you will get any custom views or skin specific settings back. See the FAQ for how to restore these.  

## Scheduling 

You can schedule backups to be completed on a set interval via the scheduling area. When it is time for the backup to run it will be executed in the background. 

When using the "Shutdown" function this will call Kodi's Shutdown method as defined in System Settings -> Power Saving -> Shutdown Function. This can be simply exiting Kodi, hibernating, or shutting down your htpc. 

## Using Dropbox

Using Dropbox as a storage target adds a few steps the first time you wish to run a backup. First you will need to sign-up for you own developer app key and secret by visiting https://www.dropbox.com/developers. Name your app whatever you want, and make it an "App Folder" type application. Your app can run in developer mode and you should never need to apply for production status. This is to get around Dropbox's rule not allow distribution of production key/secret pairs. 

Once you have your app key and secret add them to the settings. Kodi Backup now needs to have permission to access your Dropbox account. Hit the _Authorize_ button to start this process. When you see the prompt regarding the Dropbox URL Authorization you'll need to type the TinyURL into a browser on your phone, tablet, or computer - **DO NOT click OK**. Once you authorize via the browser you can click OK in Kodi and proceed as normal. Kodi Backup will cache the authorization code so you only have to do this once, or if you revoke the Dropbox permissions. 

## Using Google Drive

Using the Google Drive target is very similar to the Dropbox one. You must create a Google API project and authenticate your account via the id and secret. Instructions for enable the Google API for Google Drive can be found here (https://developers.google.com/api-client-library/python/start/get_started). You'll need the client id and client secret generated for the addon settings. You only need to follow Step 1. 

Once you have the client ID and Secret add them to the addon settings and click _Authorize_. You'll get a popup with a TinyURL to enter in a browser on your phone, tablet, or computer. Click OK and you'll see a notification to enter your authorization code. You'll get this code after authorizing the app via your browser. Put the code from your browser into the pop-up dialog. The addon will cache these credentials so it should be a one-time authentication unless you revoke Google Drive permissions. 

## Scripting A Backup 

If you wish to script this addon using an outside scheduler or script it can be given parameters via the Kodi.RunScript() or JsonRPC.Addons.ExecuteAddon() methods. Parameters given are either "backup" or "restore" to launch the correct program mode. If mode is "restore", an additional "archive" parameter can be given to set the restore point to be used instead of prompting via the GUI. An example would be: 

Python code: 
```python
RunScript(script.Kodibackup,mode=backup)
```

JSON Request: 
```
{ "jsonrpc": "2.0", "method": "Addons.ExecuteAddon","params":{"addonid":"script.Kodibackup","params":{"mode":"restore","archive":"000000000000"}}, "id": 1 }
```

There is also a windows parameter that can be used to check if Kodi Backup is running within a skin or from another program. It is attached to the home window, an example of using it would be the following: 

```python
#kick off the Kodi backup
Kodi.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Addons.ExecuteAddon","params":{"addonid":"script.Kodibackup","params":{"mode":"backup"}}, "id": 1 }')

#sleep for a few seconds to give it time to kick off
Kodi.sleep(10000)

window = Kodigui.Window(10000)

while (window.getProperty('script.Kodibackup.running') == 'true'):
     #do something here, probably just sleep for a few seconds
     Kodi.sleep(5000)

#backup is now done, continue with script
```

## FAQ

1. I can't see any restore points when choosing "Restore", what is the problem? 

	If you've created restore points with an older version of the addon (pre 0.3.6) you may see this issue. New versions of the addon look for a file called xbmcbackup.val to validate that a folder is a valid restore archive. Your older restore folders may not have this file. All you need to do is create a blank text file and rename it to xbmcbackup.val. Then put this file inside the archive directory. Your restore points should show up after selecting "Restore" in the addon again.

2. Why is the Addon prompting me to restart Kodi to continue? 

	If you have an advancedsettings file in your restore folder the addon will ask you if you want to restore this file and restart Kodi to continue. This is because the advancedsettings file may contain path substitution information that you want to be loaded when doing the rest of your restore. By restoring this file and restarting Kodi it will be loaded and the rest of your files will go where they are supposed to. If you know your file does not contain any path substitutions you can select "no" and continue as normal.
	
3. I've re-installed a newer version of Kodi from scratch and tried to restore my data from an older version. Why isn't it working?

	It is working, just not how you are expecting. When re-installing Kodi it is usually easier to install the version you had and do an in-place upgrade by installing the newer version of the top. Kodi will take care of upgrading your content, addons, and databases itself after running it for the first time. By doing a backup of your current, wiping your data, and installing a newer version you're not allowing these processes to take place. What ends up happening is that your old databases and other files get restored, Kodi just doesn't care to use them anymore. In the case of addons this could really mess things up by restoring now non-working addons from an older version of Kodi. 

	If you want to get your databases back after doing this there is something you can do. Kodi will perform a check on startup for the most current database version. If one is not found it will look for an older one and upgrade it. So you can do your restore process, then quit Kodi. Find the database files under userdata/Databases and delete the ones with the highest DB number. Then start Kodi again. It should take your old database and  upgrade it to the most current version - creating a new database file in the process. Please note this only works for the SQLite database. 
	
4. Compressing my backups isn't working, why?

	The most common reason for this is going to be drive space. Non-compressed backups write files directly from your local folders to the remote directory. When compressing the archive the files are first staged locally and then only the compressed folder copied over the remote directory. This means for both backup and restore operations you need to have enough space on your local drive for creation/extraction of the compressed archive. Depending on the folders you are selecting - especially for custom directories - this could be a lot of extra drive space, or very little.
