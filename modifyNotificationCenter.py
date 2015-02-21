#!/usr/bin/python

import os, commands, sqlite3, sys, pwd, time, getopt, getpass

#########################################################################################
#     Build our help menu
#########################################################################################
def SHOW_HELP_MENU():
    print "\nUsage: python %s [options]"% _THIS_SCRIPT
    print "-h, --help\t\t\t\t\t\tPrint this message"
    print "-i, --id\t\t\t\t\t\tPrint Bundle IDs in Notification Database\n"
    print "-v, --verbose\t\t\t\t\t\tShow information"
    print "-e, --effect \t\t\t\t\t\tApplications to effect: [All, Apple, NonApple, NonSystem [Specific] (see examples)] "
    print "-a [Banner, Alert], --alert [Banner, Alert] \t\tSet Alert Style (For None use -A)"
    print "-A, --alertsoff \t\t\t\t\tTurn off Alerts"
    print "-c [1,5,10,20], --center [1,5,10,20]\t\t\tShow in Notification Center"
    print "-C, --centeroff \t\t\t\t\tShow off Display in Notification Center"
    print "-b, --badge \t\t\t\t\t\tShow App Badge Icon"
    print "-B, --badgesoff \t\t\t\t\tDo Not Show App Badge Icon"
    print "-l, --lock \t\t\t\t\t\tShow on Lock Screen"
    print "-L, --lockoff \t\t\t\t\t\tDo Not Show on Lock Screen"
    print "-s, --sounds \t\t\t\t\t\tTurn on Sounds"
    print "-S, --soundsoff \t\t\t\t\tTurn Off Sounds"
    print "-p [Always, Unlocked], --previews [Always, Unlocked] \tTurn on previews (For None use -P)"
    print "-P, --previewsoff \t\t\t\t\tTurn Off Previews (iMessages and OS X Mail)"

    print "\n"
    
    print "Examples:"
    print "  " + _THIS_SCRIPT + " -e All -L -c 20 -b -S -a Banner -p Unlocked"
    print "  Turns off Lock Screen Notifications and Sounds. Turns on App Bages and shows 20 recent items in Notification Center, Sets Alert style to Banner, turns on Message Previews only when the system is unlocked"
    print "\n"

    print "  " + _THIS_SCRIPT + " -e Apple -A -lockoff -centeroff --badgseoff -soundsoff -P"
    print "  Turns off all Notifications from Apple Apps but turns off Message Previews"
    print "\n"

    print "  " + _THIS_SCRIPT + " -e com.jamfsoftware.Management-Action -L -C"
    print "  Turns off Lock Screen and Notification Center for Self Service"
    print "  Use -i to find Bundle IDs"
    print "\n"


    exit()

#########################################################################################
# Get Current Finder User
#########################################################################################
CURRENT_SCRIPT_USERID = os.getuid()
CURRENT_SCRIPT_USERNAME = getpass.getuser()
CURRENT_FINDER_USERNAME = os.getlogin()
CURRENT_FINDER_USERID = pwd.getpwnam(CURRENT_FINDER_USERNAME).pw_uid

#########################################################################################
# Switch to Current Finder User to run the rest of the script
#########################################################################################
os.setuid(CURRENT_FINDER_USERID)

#########################################################################################
# Global Variables
#########################################################################################
_THIS_SCRIPT = str(sys.argv[0])
_DEBUG = False
_VERBOSE = False
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
    print "Can not find Notification Database"
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
if len(sys.argv) < 2:
    print "Missing Options"
    SHOW_HELP_MENU()
    exit()

try:
    opts, args = getopt.getopt(sys.argv[1:], "vhde:Aa:Llc:CBbsSip:P", ["verbose","help","debug","effect=","alertsoff""alert=","lock=","lockoff","center=","centeroff","badge","badgesoff","sounds","soundsoff","id","previews=","previewsoff"])
except getopt.GetoptError as err:
    print(err)
    SHOW_HELP_MENU()
    exit(2)

for opt, arg in opts:
#DEBUG
    if opt in ("-d", "--debug"):
        _DEBUG = True

#VERBOSE
    if opt in ("-v", "--verbose"):
        _VERBOSE = True

#HELP
    elif opt in ("-h", "--help"):
        SHOW_HELP_MENU()
#EFFECT
    elif opt in ("-e", "--effects"):
        if arg.upper() in ("ALL","APPLE","NONAPPLE","NONSYSTEM"):
            APPS_IN_QUESTION = arg.upper()
            if _DEBUG | _VERBOSE: print "Modifying " + APPS_IN_QUESTION
        elif arg.upper() in APPS_LIST:
            APPS_IN_QUESTION = arg.upper()
            if _DEBUG | _VERBOSE: print "Modifying " + APPS_IN_QUESTION
        else:
            print "\n\n****Missing or Incorrect Application"
            SHOW_HELP_MENU()
            exit(2)
#ALERT
    elif opt in ("-a", "--alert"):
        if arg.upper() in ("BANNER","ALERT"):
            ALERT_STYLE = arg.upper()
            if _DEBUG | _VERBOSE:print "Alert Style " + ALERT_STYLE
        else:
            print "\n\n****Missing or Incorrect Number for Alert Style"
            SHOW_HELP_MENU()
            exit(2)

    elif opt in ("-A", "--alertsoff"):
        ALERT_STYLE = "OFF"
        if _DEBUG | _VERBOSE:print "Not Showing Alerts"


#PREVIEWS
    elif opt in ("-p", "--previews"):
        if arg.upper() in ("ALWAYS","UNLOCKED"):
            PREVIEWS = arg.upper()
            if _DEBUG | _VERBOSE:print "Preview Style " + PREVIEWS
        else:
            print "\n\n****Missing or Incorrect Number for Preview Style"
            SHOW_HELP_MENU()
            exit(2)

    elif opt in ("-P", "--previews"):
        PREVIEWS = "OFF"
        if _DEBUG | _VERBOSE:print "Not Showing Previews"

#LOCK
    elif opt in ("-L", "--lockoff"):
        SHOW_ON_LOCK = "OFF"
        if _DEBUG | _VERBOSE:print "Not Showing on Lock Screen"

    elif opt in ("-l", "--lock"):
        SHOW_ON_LOCK = "ON"
        if _DEBUG | _VERBOSE:print "Showing on Lock Screen"
#CENTER
    elif opt in ("-C", "--centeroff"):
        SHOW_IN_CENTER = "OFF"
        if _DEBUG | _VERBOSE:print "Not Showing in Notification Center"

    elif opt in ("-c", "--center"):
        if arg in ("1","5","10","20"):
            SHOW_IN_CENTER = "ON"
            RECENT_ITEMS = arg
            if _DEBUG | _VERBOSE:print "Showing " + RECENT_ITEMS + " Recent Items in Notification Center "
        else:
            print "\n\n****Missing or Incorrect Number for Showing in Notification Center****"
            SHOW_HELP_MENU()
            exit(2)
#BADGE
    elif opt in ("-b", "--badge"):
        BADGE_ICONS = "ON"
        if _DEBUG | _VERBOSE:print "Turning on Badges"

    elif opt in ("-B", "--badgesoff"):
        BADGE_ICONS = "OFF"
        if _DEBUG | _VERBOSE:print "Turning off Badges"
#SOUND
    elif opt in ("-s", "--sounds"):
        SOUNDS = "ON"
        if _DEBUG | _VERBOSE:print "Sounds: ", SOUNDS

    elif opt in ("-S", "--soundsoff"):
        SOUNDS = "OFF"
        if _DEBUG | _VERBOSE:print "Sounds: ",SOUNDS
#IDs
    elif opt in ("-i", "--id"):
        for i in APPS_LIST:
            print i

if _DEBUG: SHOW_DEBUG(sys.argv)




#########################################################################################
# Figure out what App or Apps we are working with
#########################################################################################
if APPS_IN_QUESTION == "ALL": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["ALL"])
elif APPS_IN_QUESTION == "APPLE": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["APPLE"])
elif APPS_IN_QUESTION == "NONAPPLE": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["NONAPPLE"])
elif APPS_IN_QUESTION == "NONSYSTEM": cur.execute("SELECT * FROM app_info %s"% APPS_WHERE_DICT["NONSYSTEM"])
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


