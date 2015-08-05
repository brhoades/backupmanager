# Billy Rhoades
# 8/4/15
#
# This script creates backups in storagelocation with the name of the key in directories. Only when
# a file in the value of directories is modified does a new backup get created. The folder for the backups
# is automatically created where needed. 
#
# For reference, if you wanted to add another directory just create another line below the example below like so:
# directories["key"] = "value"
# directories["Mass Effect"] = "C:\Program Files (x86)\EA Games\Mass Effect\Saved Games\"
#
# With no wildcard specified at the end of the value, the script will grab the entire folder. If you put a *
# afterwards, only the files in that folder recursively will be grabbed. The backups will be stored in the folder
# "Mass Effect" as a subdirectory of config["storagelocation"]. 
#
# To run this with task scheduler in Windows, you will need to path to pythonw.exe. For example, the top field for
# the executable file will be similar to "C:\Python34\pythonw.exe". The second field, with arguments, will be the
# full path to this script (which can be located anywhere). This script does not need to be ran as System as long
# as you use pythonw, which won't open anything.

import os, sys, datetime
from subprocess import call

directories = dict()
config = dict()

##################################
# Configuration Starts Here
#
# Directories to backup. You can list as many of these as you like in the same format.
#   Wildcards cause those files to save at the top of the 7z file. Without them, Saved Games below
#   becomes THE first file in the 7z file.
# directories["backupfoldername"] = "backup source"
# directories["Mass Effect"] = "C:\Program Files (x86)\EA Games\Mass Effect\Saved Games\"
# directories["Terraria"] = "/home/billy/.steam/steam/SteamApps/common/Terraria/Savefiles/*""
#
directories["tempbackup1 name"] = "/tmp/backupdir1/"

# Date format. This follows Unix date format if you want more details.
config["backupformat"] = "%Y%m%d_%H%M%S"

# Target backup folder, where we store all of the backups. Subdirectories go in here.
config["storagelocation"] = "/mnt/storage/backups/"

# 7-Zip binary location
# FIX THIS and choose the one that works for you. You need double backslashes here.
# config["7z"] = "C:\\Program Files (x86)\\7-zip\\7z.exe"
# config["7z"] = "C:\\Program Files\\7-zip\\7z.exe"
config["7z"] = "/usr/bin/7z"
#
# Configuration Ends Here
##################################


def backup(config, directories):
    print("Checking backups: ")
    # check the target directories for changes
    for key, value in directories.items():
        print(''.join(['  ', '"', key, '"']))
        thisstoragelocation = os.path.join(config["storagelocation"], key)
        if not os.path.isdir(thisstoragelocation) \
           or hasChanged(value, thisstoragelocation):
            updateBackup(value, thisstoragelocation, config)
        else:
            print(''.join(['    ', "Up to date"]))



# Takes two directories and recursively finds the newest file, then compares the timestamps.
#   Returns true if the sourcedirectory is newer, false if same or not.
def hasChanged(sourcedirectory, targetdirectory):
    sourcet = latestFileTimestamp(sourcedirectory)
    if sourcet is None:
        print("    There are no files in the source directory to back up")
        print(''.join(["    Source directory: ", sourcedirectory]))
        if not os.path.isdir(sourcedirectory):
            print("    Directory doesn't exist.")
        return False
    targett = latestFileTimestamp(targetdirectory)
    if targett is None:
        print("    This is the first backup")
        return True


    return sourcet > targett

def updateBackup(sourcedirectory, targetdirectory, config):
    print("  Creating new backup...")
    os.makedirs(targetdirectory, exist_ok=True)
    
    backupname = ''.join(["backup-", 
        latestFileTimestamp(sourcedirectory).strftime(config["backupformat"])])
    backupfull = os.path.join(targetdirectory, backupname)
    call([config["7z"], "a", "-t7z", "-m0=lzma2", "-mx=9", "-aoa", backupfull, sourcedirectory])
    print("  Backup created")




# Takes a folder and recursively finds the newest file in it, returning its timestamp.
def latestFileTimestamp(directory):
    filelist = []
    for dirname, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filelist.append(os.path.join(dirname,filename))
    filelist.sort(key=lambda f: os.stat(f).st_mtime)

    if len(filelist) == 0:
        return None # there are no backups
    return datetime.datetime.fromtimestamp(os.stat(filelist[-1]).st_mtime)
    

if __name__ == '__main__':
    backup(config, directories)
