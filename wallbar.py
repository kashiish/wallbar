#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 23:15:49 2018

@author: kashish
"""

from crontab import CronTab
from configparser import ConfigParser  
import argparse
import os


once_every = ["hourly", "daily", "weekly", "monthly", "yearly"]
time_units = ["hour", "hours", "day", "days", "month", "months"]

fetch_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch.py")

cron = CronTab(user=True)

cron_command = """ /usr/local/bin/python3 {0} """.format(fetch_py)

def create_new_job(schedule, query=None):
    """
    
    Creates a new cron job with specified schedule to run python file `fetch.py`.
    
    params:
        schedule: (string) when the wallpaper should be changed
    
    
    """
    if _cron_job_exists():
        _remove_job()          
    
    job  = cron.new(command=cron_command)
    
    if query is not None:
        _update_image_query(query)
    else:
        _update_image_query("")


    if schedule in once_every:
        _set_frequency_once_every(job, schedule)
    else:
        _set_frequency_with_time_units(job, schedule)
        
    job.set_comment("WallBar")
    
    cron.write()
    

def _remove_job():
    """
    Removes WallBar cron job from user's system.
    
    """
    cron.remove_all(comment="WallBar")
    
def _set_frequency_once_every(job, schedule):
    """
    Sets frequency of cron job based on `schedule` which is a
    "once every xxx" string (hourly, daily, weekly, etc).
    
    params:
        job: (cron job object) the job to set the frequency for
        schedule: (string) a string from `once_every` list
    
    """
    schedule = schedule.lower()

    if schedule == "hourly":
        job.setall("@hourly")
    if schedule == "daily":
        job.setall("@daily")
    if schedule == "weekly":
        job.setall("@weekly")
    if schedule == "monthly":
        job.setall("@monthly")
    if schedule == "yearly":
        job.setall("@yearly")
        
def _set_frequency_with_time_units(job, schedule):  
    """
    
    Sets the frequncy of cron job based on `schedule` which is a
    string with a specified integer and time unit (hours, days, etc.).
    
    params:
        job: (cron job object) the job to set the frequency for
        schedule: (string) a string with a specified integer and time unit (from `time_units` list)
    
    
    """
    schedule_list = schedule.split()
    schedule_int = int(schedule_list[0])
    schedule_unit = schedule_list[1].lower()
    if schedule_unit == "hour" or schedule_unit == "hours":
        job.hour.every(schedule_int)
    if schedule_unit == "day" or schedule_unit == "days":
        job.day.every(schedule_int)
    if schedule_unit == "week" or schedule_unit == "weeks":
        job.week.every(schedule_int)
    if schedule_unit == "month" or schedule_unit == "months":
        job.month.every(schedule_int)

def _update_image_query(query):
    """
    Updates the image query in the config file. The image query is used while fetching
    a random image from the Unsplash API.
    
    """

    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/config.cfg")
    config = ConfigParser()
    config.read(config_file)

    config["unsplash"]["query"] = query
    
    with open(config_file, "w") as file:
        config.write(file)
        
            
def _cron_job_exists():
    """
    Determines if a WallBar cron job already exists in the user's system.
    
    return:
        boolean
    """
    jobs = cron.find_comment("WallBar")
    if sum(1 for _ in jobs) == 0:
        return False
    return True

class CustomAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 2 or (len(values) == 2 and (not values[0].isdigit() or values[1].lower() not in time_units)) or (len(values) == 1 and values[0].lower() not in once_every):
            parser.error("Invalid schedule argument. Valid arguments include " + str(once_every) + " or specified frequency: <int> + <time_unit>. Time units include: " + str(time_units))
    
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--schedule", nargs="+", help="Sets the schedule to change wallpaper.", action=CustomAction)
    parser.add_argument("-q", "--query", nargs="+", help="Sets the search query for wallpaper.")
    args = parser.parse_args()

    if args.schedule is None:
        parser.error("Please enter a schedule using '-s <schedule>'")
    else:
        schedule = " ".join(list(args.schedule))
   
        query = None
   
        if args.query is not None:
            query = " ".join(list(args.query))
       
        create_new_job(schedule, query)

if __name__ == '__main__':
   main()