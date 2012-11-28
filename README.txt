XBMC Backup

About: 
I've had to recover my database, thumbnails, and source configuration enough times that I just wanted a quick easy way to back them up. That is what this addon is meant to do. 

Remote Destination/File Selection: 

In the addon settings you can define a remote path for the destination of your xbmc files. Each backup will create a folder named in a YYYYMMDD format so you can create multiple backups. 

On the Backup Selection page you can select which items from your user profile folder will be sent to the backup location. By default all are turned on except the Addon Data directory. 

Scheduling: 

You can also schedule backups to be completed on a set interval via the scheduling area. When it is time for the backup to run it will be executed in the background. 

Running the Program:

Running the program will allow you to select Backup or Restore as a running mode. Selecting Backup will push files to your remote store using the addon settings you defined. Selecting Restore will give you a list of restore points currently in your remote destination. Selecting one will pull the files matching your selection criteria from the restore point to your local XBMC folders. 

What this Addon Will Not Do:

This is not meant as an XBMC file sync solution. If you have multiple frontends you want to keep in sync this addon may work in a "poor man's" sort of way but it is not intended for that. 

This backup will not check the backup destination and delete files that do not match. It is best to only do one backup per day so that each folder is correct. 

