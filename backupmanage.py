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
# task scheduler, "Program/Script", will be similar to "C:\Python34\pythonw.exe" (whereever pythonw.exe is). 
# The second field, "add arguments",  will be the  full path to this script  (which can be located anywhere). 
# This script does not need to be ran as System as long  as you use pythonw, which won't open any prompts.

import os, sys, datetime, tarfile, lzma
from subprocess import call

directories = dict()
config = dict()

##################################
# Configuration Starts Here
#
# Directories to backup. You can list as many of these as you like in the same format.
#   WINDOWS NOTE: You must use double backslashes on all quotes. Alternatively, you can use
#   os.path.join(["C:", "Folder", "Folder"]).
# Format:
#   directories["backupfoldername"] = "backup source"
# Examples: 
#   directories["Mass Effect"] = "C:\\Program Files (x86)\\EA Games\\Mass Effect\\Saved Games"
#   directories["BF4"] = os.path.join(["C:", "Program Files", "Battlefield 4", "Saves"])
#   directories["Terraria"] = "/home/billy/.steam/steam/SteamApps/common/Terraria/Savefiles"
directories["tempbackup1 name"] = "/tmp/backmeup/"

# Preserve directory hierarchy boolean
# If you want to see in the archive your directories, ie the archive starts with tmp
# then backmeup, and THEN your files, choose True. Otherwise False.
config["preservehierarchy"] = False

# Date format. This follows Unix date format if you want more details.
config["backupformat"] = "_%Y-%m-%d_%H-%M-%S"

# Target backup folder, where we store all of the backups. Subdirectories go in here.
#config["storagelocation"] = "C:\\Users\\Billy\\Dropbox\\Saved Games\\"
config["storagelocation"] = "/mnt/storage/backups/"

# Basename for all files... What goes before the timestamp
config["basename"] = "backup"

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
    
    backupname = ''.join([config["basename"], 
        latestFileTimestamp(sourcedirectory).strftime(config["backupformat"]), '.tar.xz'])
    backupfull = os.path.join(targetdirectory, backupname)

    file = lzma.LZMAFile(backupfull, mode='w')

    with tarfile.open(mode='w', fileobj=file) as xz:
        if config['preservehierarchy']:
            xz.add(sourcedirectory)
        else:
            xz.add(sourcedirectory, arcname='')
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
