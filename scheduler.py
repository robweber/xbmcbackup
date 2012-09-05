import xbmc
import time
import resources.lib.utils as utils
from resources.lib.backup import XbmcBackup

class BackupScheduler:
    enabled = "false"

    def __init__(self):
        self.enabled = utils.getSetting("enable_scheduler")
        
    def start(self):
        while(not xbmc.abortRequested):
            if(self.enabled == "true"):
                cron_exp = self.parseSchedule()
                utils.log(cron_exp)
            else:
                utils.log("backup not enabled")
                self.enabled = utils.getSetting("enable_scheduler")
                
            time.sleep(10)

    def parseSchedule(self):
        schedule_type = int(utils.getSetting("schedule_interval"))
        cron_exp = utils.getSetting("cron_schedule")

        hour_of_day = utils.getSetting("schedule_time")
        hour_of_day = int(hour_of_day[0:2])
        if(schedule_type == 0):
            #every day
           
            cron_exp = "0 " + str(hour_of_day) + " * * *"
        elif(schedule_type == 1):
            #once a week
            day_of_week = utils.getSetting("day_of_week")
            cron_exp = "0 " + str(hour_of_day) + " * * " + day_of_week
        elif(schedule_type == 2):
            #first day of month
            cron_exp = "0 " + str(hour_of_day) + " 1 * *"

        return cron_exp    
        
BackupScheduler().start()
