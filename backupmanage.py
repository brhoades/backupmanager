import os, sys, datetime
from subprocess import call

#Config
directories = dict()
config = dict()
#
#directories to backup
#Format: directories["backupfoldername"] = "backup source"
#
directories["tempbackup1 name"] = "/tmp/backupdir1/"

# Date format
config["backupformat"] = "%Y%m%d_%H%M%S"

# Target backup folder, where we store all of the backups
config["storagelocation"] = "/mnt/storage/backups/"

# 7-Zip binary location
# config["7z"] = "C:\\Program Files (x86)\\7-zip\\7z.exe"
# config["7z"] = "C:\\Program Files\\7-zip\\7z.exe"
config["7z"] = "/usr/bin/7z"


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
    targett = latestFileTimestamp(targetdirectory)

    return targett == None or sourcet > targett

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
        print("  There are no backups made")
        return None # there are no backups
    return datetime.datetime.fromtimestamp(os.stat(filelist[-1]).st_mtime)
    

if __name__ == '__main__':
    backup(config, directories)
