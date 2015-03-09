#!/usr/bin/python

import os, commands, sqlite3, sys, pwd, time, getopt, getpass, re

##########################################################################################
# Name the Casper Parameters:
# 4 Apps to effect (ALL, APPLE, NONAPPLE, NONSYSTEM, CASPER)
# 5 Alert Style (BANNER, ALERT, OFF)
# 6 Show Previews (ALWAYS, UNLOCKED, OFF)
# 7 Show on Lock Screen (ON, OFF)
# 8 Show in Notification Center: 0,1,5,10,20
# 9 Show Badges (ON, OFF)
# 10 Play Sounds (ON, OFF)
#
# When creating a policy in the JSS, be sure that every parameter has SOMETHING in it.
# For Example if you want to set all Notification Items to have the sound off but keep
# all other settings the same, you can put a dot or "Same" in the other parameters to keep
# them how the user has them.
#
# The policy cannot be triggered to run during startup, login or logout
# (and probably not during enrollment complete)
# It needs a logged in user to function.
#
##########################################################################################






#########################################################################################
# Get Current Finder User
#########################################################################################
CURRENT_SCRIPT_USERID = os.getuid()
CURRENT_SCRIPT_USERNAME = getpass.getuser()
CURRENT_FINDER_USERNAME = os.getlogin()
CURRENT_FINDER_USERID = pwd.getpwnam(CURRENT_FINDER_USERNAME).pw_uid
CURRENT_FINDER_HOME = pwd.getpwnam(CURRENT_FINDER_USERNAME).pw_dir

#########################################################################################
# Switch to Current Finder User to run the rest of the script
#########################################################################################
os.setuid(CURRENT_FINDER_USERID)

#########################################################################################
# Global Variables
#########################################################################################
_THIS_SCRIPT = str(sys.argv[0])
_DEBUG = False
_VERBOSE = True
APPS_IN_QUESTION = ""
APPS_LIST = []
ALERT_STYLE = "SAME"
SHOW_ON_LOCK = "SAME"
SHOW_IN_CENTER = "SAME"
RECENT_ITEMS = 0
BADGE_ICONS = "SAME"
SOUNDS = "SAME"
PREVIEWS = "SAME"

APPS_WHERE_DICT = { "ALL" : "",
    "APPLE" : "WHERE bundleid LIKE 'COM.APPLE.%'",
    "NONAPPLE": "WHERE bundleid NOT LIKE '%COM.APPLE.%' AND bundleid NOT LIKE '_SYSTEM_CENTER_%'",
    "NONSYSTEM" : "WHERE bundleid NOT LIKE '_SYSTEM_CENTER_%'",
    "CASPER" : "WHERE bundleid LIKE 'com.jamfsoftware.Management-Action'"
}

#########################################################################################
# Get the Current Finder User's Cache Folder
#########################################################################################
CURRENT_FINDER_CACHE_FOLDER = commands.getoutput("getconf DARWIN_USER_DIR")
NOTIFICATION_DATABASE = CURRENT_FINDER_CACHE_FOLDER + "com.apple.notificationcenter/db/db"




#########################################################################################
# Check for existance of Current Finder User's Cache Folder
#########################################################################################
if os.path.exists(NOTIFICATION_DATABASE):
    pass
else:
    if _DEBUG: print "Can not find Notification Database in /var/folders/ checking home folder"
    CURRENT_FINDER_CACHE_FOLDER = CURRENT_FINDER_HOME + "/Library/Application Support/NotificationCenter/"
    FILES = os.listdir(CURRENT_FINDER_CACHE_FOLDER)
    for file in FILES:
        if re.match("\d*.*\.db",file):
            NOTIFICATION_DATABASE = CURRENT_FINDER_CACHE_FOLDER + file
    if os.path.exists(NOTIFICATION_DATABASE):
    	if _DEBUG | _VERBOSE: print "Found Notification Database at " + NOTIFICATION_DATABASE
        pass
    else:
        print "Can not find Notification Database."
        exit(1)

#########################################################################################
# Connect to the Database and Pull App Bundle List
#########################################################################################
con = sqlite3.connect(NOTIFICATION_DATABASE)
cur = con.cursor()
cur.execute("SELECT bundleid FROM app_info")
BUNDLESTUP = cur.fetchall()
for bun in BUNDLESTUP:
    APPS_LIST.append(bun[0].upper())

#########################################################################################
#     Print some Debug info if needed
#########################################################################################
def SHOW_DEBUG(currentArgs):
    if _DEBUG: print "\nCurrent options: %s" % str(currentArgs)
    if _DEBUG: print "Database:\t", NOTIFICATION_DATABASE
    if _DEBUG: print "Process Owner:\t", CURRENT_SCRIPT_USERNAME, CURRENT_SCRIPT_USERID
    if _DEBUG: print "Finder User:\t", CURRENT_FINDER_USERNAME, CURRENT_FINDER_USERID
    if _DEBUG: print "\n"

#########################################################################################
#     Parse our arguments and options
#########################################################################################
if len(sys.argv) < 4:
    print "Missing Options"
    exit()


#EFFECT
if sys.argv[4].upper() in ("ALL","APPLE","NONAPPLE","NONSYSTEM","CASPER"):
    APPS_IN_QUESTION = sys.argv[4].upper()
    if _DEBUG | _VERBOSE: print "Modifying " + APPS_IN_QUESTION
elif sys.argv[4].upper() in APPS_LIST:
    APPS_IN_QUESTION = sys.argv[4].upper()
    if _DEBUG | _VERBOSE: print "Modifying " + APPS_IN_QUESTION
else:
    print "\n\n****Missing or Incorrect Application"
    exit(2)

#ALERT
try:
    if sys.argv[5].upper() in ("BANNER","ALERT","OFF"):
        ALERT_STYLE = sys.argv[5].upper()
        if _DEBUG | _VERBOSE:print "Alert Style: " + ALERT_STYLE
except:
    pass
#PREVIEWS
try:
    if sys.argv[6].upper() in ("ALWAYS","UNLOCKED","OFF"):
        PREVIEWS = sys.argv[6].upper()
        if _DEBUG | _VERBOSE:print "Preview Style: " + PREVIEWS
except:
    pass

#LOCK
try:
    if sys.argv[7].upper() in ("ON","OFF"):
        SHOW_ON_LOCK = sys.argv[7].upper()
        if _DEBUG | _VERBOSE:print "Lock Screen: " + SHOW_ON_LOCK
except:
    pass


#CENTER
try:
    if sys.argv[8] == "0":
        SHOW_IN_CENTER = "OFF"
        if _DEBUG | _VERBOSE:print "Not Showing in Notification Center"
except:
    pass

try:
    if sys.argv[8] in ("1","5","10","20"):
        SHOW_IN_CENTER = "ON"
        RECENT_ITEMS = sys.argv[8]
        if _DEBUG | _VERBOSE:print "Showing " + RECENT_ITEMS + " Recent Items in Notification Center "
except:
    pass

#BADGE
try:
    if sys.argv[9].upper() in ("ON","OFF"):
        BADGE_ICONS = sys.argv[9].upper()
        if _DEBUG | _VERBOSE:print "Badge Icons: " + BADGE_ICONS
except:
    pass

#SOUND
try:
    if sys.argv[10].upper() in ("ON","OFF"):
        SOUNDS = sys.argv[10].upper()
        if _DEBUG | _VERBOSE:print "Sounds: ", SOUNDS
except:
    pass

#########################################################################################
# Figure out what App or Apps we are working with
#########################################################################################
if APPS_IN_QUESTION == "ALL": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["ALL"])
elif APPS_IN_QUESTION == "APPLE": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["APPLE"])
elif APPS_IN_QUESTION == "NONAPPLE": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["NONAPPLE"])
elif APPS_IN_QUESTION == "NONSYSTEM": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["NONSYSTEM"])
elif APPS_IN_QUESTION == "CASPER": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["CASPER"])
else: cur.execute("SELECT * FROM app_info WHERE bundleid LIKE '%s'"% APPS_IN_QUESTION)

WORKING_APP_LIST = cur.fetchall()

#########################################################################################
# Determine the current Settings
#########################################################################################
for workingApp in WORKING_APP_LIST:
    currentBundleID = workingApp[1]
    currentSettings = workingApp[2]
    if _DEBUG: print "Bundle ID:\t\t" + currentBundleID + "\nCurrent Settings:\t" + str(currentSettings)
    newSettings = currentSettings
    # Find out what settings are currently on
    currentSHOW_IN_CENTER = "ON" if currentSettings & 1 == 0 else "OFF"
    currentBADGE_ICONS = "OFF" if currentSettings & 1 << 1 == 0 else "ON"
    currentSOUNDS = "OFF" if currentSettings & 1 << 2 == 0 else "ON"
    if (currentSettings & 1 << 3 == 0) and (currentSettings & 1 << 4 == 0):
        currentALERT_STYLE = "OFF"
    elif (currentSettings & 1 << 3 != 0) and (currentSettings & 1 << 4 == 0):
        currentALERT_STYLE = "BANNER"
    else:
        currentALERT_STYLE = "ALERT"

    currentSHOW_ON_LOCK = "ON" if currentSettings & 1 << 12 == 0 else "OFF"

    if (currentSettings & (1 << 13) == 0) and (currentSettings & (1 << 14) != 0) :
        currentSHOWPREVIEWS = "OFFUNLOCKED"
    elif (currentSettings & (1 << 13) != 0) and (currentSettings & (1 << 14) != 0) :
        currentSHOWPREVIEWS = "OFFALWAYS"
    elif (currentSettings & 1 << 13 != 0) and (currentSettings & 1 << 14 == 0):
        currentSHOWPREVIEWS = "ALWAYS"
    elif (currentSettings & 1 << 13 == 0) and (currentSettings & 1 << 14 == 0):
        currentSHOWPREVIEWS = "UNLOCKED"


    if _DEBUG : print "Center: " + currentSHOW_IN_CENTER + "\nBadge: " + currentBADGE_ICONS + "\nSounds: " + currentSOUNDS + "\nAlert Style: " + currentALERT_STYLE + "\nLock: " + currentSHOW_ON_LOCK + "\nPreviews: " + currentSHOWPREVIEWS

#########################################################################################
# Make Changes
#########################################################################################
    if SHOW_IN_CENTER == "OFF" and currentSHOW_IN_CENTER == "ON": newSettings = newSettings ^ 1
    if SHOW_IN_CENTER == "ON" and currentSHOW_IN_CENTER == "OFF": newSettings = newSettings ^ 1

    if BADGE_ICONS == "OFF" and currentBADGE_ICONS == "ON": newSettings = newSettings ^ 1 << 1
    if BADGE_ICONS == "ON" and currentBADGE_ICONS == "OFF": newSettings = newSettings ^ 1 << 1

    if SOUNDS == "OFF" and currentSOUNDS == "ON": newSettings = newSettings ^ (1 << 2)
    if SOUNDS == "ON" and currentSOUNDS == "OFF": newSettings = newSettings ^ (1 << 2)

    if SHOW_ON_LOCK == "OFF" and currentSHOW_ON_LOCK == "ON": newSettings = newSettings ^ (1 << 12)
    if SHOW_ON_LOCK == "ON" and currentSHOW_ON_LOCK == "OFF": newSettings = newSettings ^ (1 << 12)


    if ALERT_STYLE == "OFF" and currentALERT_STYLE == "BANNER": newSettings = newSettings ^ (1 << 3)
    if ALERT_STYLE == "OFF" and currentALERT_STYLE == "ALERT": newSettings = newSettings ^ (1 << 4)
    if ALERT_STYLE == "BANNER" and currentALERT_STYLE == "ALERT":
        newSettings = newSettings ^ (1 << 3)
        newSettings = newSettings ^ (1 << 4)
    if ALERT_STYLE == "BANNER" and currentALERT_STYLE == "OFF":
        newSettings = newSettings ^ (1 << 3)
    if ALERT_STYLE == "ALERT" and currentALERT_STYLE == "BANNER":
        newSettings = newSettings ^ (1 << 3)
        newSettings = newSettings ^ (1 << 4)
    if ALERT_STYLE == "ALERT" and currentALERT_STYLE == "OFF":
        newSettings = newSettings ^ (1 << 4)

    if PREVIEWS == "OFF" and currentSHOWPREVIEWS != "OFF": newSettings = newSettings ^ (1 << 14)
    if PREVIEWS == "UNLOCKED" and currentSHOWPREVIEWS == "OFFUNLOCKED" : newSettings = newSettings ^ (1 << 14)
    if PREVIEWS == "UNLOCKED" and currentSHOWPREVIEWS == "OFFALWAYS" :
        newSettings = newSettings ^ (1 << 14)
        newSettings = newSettings ^ (1 << 13)
    if PREVIEWS == "ALWAYS" and currentSHOWPREVIEWS == "OFFALWAYS" : newSettings = newSettings ^ (1 << 14)
    if PREVIEWS == "ALWAYS" and currentSHOWPREVIEWS == "OFFUNLOCKED" :
        newSettings = newSettings ^ (1 << 14)
        newSettings = newSettings ^ (1 << 13)

    if _DEBUG: print "New Settings: ", newSettings
#########################################################################################
# Commit Changes to Database
#########################################################################################
    cur.execute("UPDATE app_info SET flags = %s WHERE bundleid LIKE '%s'"% (newSettings,currentBundleID))
    if RECENT_ITEMS != 0 : cur.execute("UPDATE app_info SET show_count = %s WHERE bundleid LIKE '%s'"% (RECENT_ITEMS,currentBundleID))


#########################################################################################
# Close Connection to the Database
#########################################################################################
con.commit()
con.close()

#########################################################################################
# Unload and Reload the usernoted
#########################################################################################
commands.getoutput("launchctl unload /System/Library/LaunchAgents/com.apple.usernoted.plist")
time.sleep(1)
commands.getoutput("launchctl load /System/Library/LaunchAgents/com.apple.usernoted.plist")


