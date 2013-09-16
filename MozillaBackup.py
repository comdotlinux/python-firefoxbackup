import os
from datetime import datetime
import configparser
import logging
import sys
import subprocess
import time

# Get Date in required format
now = datetime.now().strftime('%A.%d-%b-%Y.%H%MHrs')

#get Data from properties file
property_file = 'MozillaBackup.properties'

# Log Filename :: TODO : get filename from sys.argv[0]
filename = "MozillaBackup.log"

#Change test_run to False to run backup
test_run = False

# Setup Logging
LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL,
            }

if len(sys.argv) > 1:
    level_name = sys.argv[1]
else:
    level_name = 'debug'

FORMAT = '%(asctime)-15s : %(message)s'
level = LEVELS.get(level_name, logging.NOTSET)
logging.basicConfig(level=level, format=FORMAT, filename=filename,filemode='a')
log = logging.getLogger('FirefoxBackup')

log.debug("-- Firefox Backup Starting --")
log.debug("Reading properties file -- Start")
# Reading Properties file
try:
    
    parser = configparser.ConfigParser()
    parser.read(property_file)
    
    firefox_executable = parser['Mozilla Firefox Backup']['FIREFOX_EXE_PATH']
    firefox_profile = parser['Mozilla Firefox Backup']['FIREFOX_PROFILE']
    moz_backup_executable = parser['Mozilla Firefox Backup']['MOZBACKUP_EXE_PATH']
    backup_dest = parser['Mozilla Firefox Backup']['BACKUP_DEST_DIR']
except configparser.Error as err:
    print("Error while parsing details are : " + str(err))
except IOError as err:
    print("Error while parsing details are : " + str(err))
log.debug("Reading properties file -- Ends")

log.debug("Splitting path -- Starts")
log.debug("firefox_executable as retrieved = " + firefox_executable)
log.debug("moz_backup_executable as retrieved = " + moz_backup_executable)

(firefox_path, firefox_exe) = os.path.split(firefox_executable)
(moz_backup_path, moz_backup_exe) = os.path.split(moz_backup_executable)
log.debug("After Splitting : ")
log.debug("firefox_path = " + firefox_path)
log.debug("firefox_exe = " + firefox_exe)
log.debug("moz_backup_path = " + moz_backup_path)
log.debug("moz_backup_exe = " + moz_backup_exe)

log.debug("Splitting path -- Ends")

log.debug("Get Firefox version -- Starts")
# getting Firefox version
try:
    firefox_version = subprocess.check_output([firefox_executable, '-v'], shell=False).strip()
    firefox_version = str(firefox_version).lstrip('b\'').rstrip('\r\n\'')
    if firefox_version:
        log.debug("Firefox version is -- " + firefox_version)

except (subprocess.SubprocessError, IOError) as err:
    exception_info = "Error while getting Firefox version : " + str(err)
    log.error(exception_info)
    print(exception_info)

log.debug("Get Firefox version -- Ends")

log.debug("Generating mozprofile file -- Starts")
# Generating required variable values
log.debug("firefox_executable = " + firefox_exe)
application = firefox_exe.split('.',maxsplit=1)[0].capitalize()
output = backup_dest + '\\' + firefox_version + ' - ' + now + '.pcv'
mozprofile_file = firefox_profile + '-firefox.mozprofile'
moz_profile = os.path.join(moz_backup_path, mozprofile_file)
log.debug("mozprofile file name -- " + moz_profile)
log.debug("Generating mozprofile file -- Ends")

# Writing MozBackup INI File to pass as parameter for MozBackup
# The generated file should be like below(without leading #)
#[General]
#action=backup
#application=Firefox
#profile=Default
#output=c:\backup.pcv
#password=

log.debug("Writing Mozprofile File")
try:
    os.chdir(moz_backup_path)
    parser = configparser.ConfigParser()

    parser.add_section('General')
    parser.set('General', 'action', 'backup')
    parser.set('General', 'application', application)
    parser.set('General', 'profile', firefox_profile)
    parser.set('General', 'output', output)
    parser.set('General', 'password', '')
    
    with open(moz_profile, 'w') as mozprof_file_handle:
        parser.write(mozprof_file_handle,space_around_delimiters=True)
        
except configparser.Error as err:
    print('Exception while writing ' + moz_profile + ' to ' + backup_dest + '\nDetails of Exception are ; ' + str(err))
except IOError as err:
    print('Exception while writing ' + moz_profile + ' to ' + backup_dest + '\nDetails of Exception are ; ' + str(err))


#Running Backup
# TODO: Check that Firefox is not running and else kill it.
#tasklist /fi "Imagename eq firefox.exe"
log.debug("Kill firefox -- Starts")
try:
    subprocess.call(['taskkill', '/IM', 'firefox.exe'], shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(50)
    subprocess.call(['taskkill', '/F', '/IM', 'firefox.exe'], shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(5)
except (subprocess.SubprocessError, IOError) as err:
    exception_info = "Error while checking if Firefox is running : " + str(err)
    log.error(exception_info)
    print(exception_info)
log.debug("Kill firefox -- Ends")


log.debug("Running Firefox backup")

try:
    os.chdir(moz_backup_path)
    if not test_run:
        output = subprocess.call([moz_backup_executable, moz_profile], shell=False)

except OSError as err:
    print('Exception occured while running Backup Details are : ' + str(err))
except ValueError as err:
    print('Exception occured while running Backup Details are : ' + str(err))
except IOError as err:
    print('Exception occured while running Backup Details are : ' + str(err))

finally:
    try:
        log.debug("Removing : " + moz_profile)
        os.remove(moz_profile)
    except IOError as err:
        log.error("Error removing file : " + moz_profile + " Error Details are : " + str(err))

log.debug("-- Firefox Backup Ends --")
