#!/usr/bin/python3
'''
Created on Oct 5, 2017

@author: jlearx
'''

from os import listdir,stat
from math import floor

def parseLine(line, configuration):
    freqDefs = ["hourly","daily","weekly","monthly","yearly"]
    
    # Skip blank lines
    if (len(line) < 1):
        return
    
    # Find the first space
    idx = line.find(" ")
    key = ""
    val = ""
    
    # If no space, then no value
    if (idx < 0):
        if (line in freqDefs):
            key = "frequency"
            val = line
        else:
            key = line
            val = line
    else:
        # Else key is before space, value is after space
        key = line[0:idx]
        val = line[idx + 1:]
         
    configuration[key] = val

# Returns a list of files from the directory matching the expression
# Supports a maximum of two wild cards
def getMatchingFiles(directory, expression):
    eLen = len(expression)
    
    # Get the files in the directory
    contents = listdir(directory)
    files = []
    
    # Match *
    if (expression == "*"):
        return contents 
    
    idx = expression.find("*")
    idx2 = expression.rfind("*")
    
    # Match no *
    if (idx < 0):            
        try:
            idx = contents.index(expression)
            files.append(contents[idx])
            return files
        except ValueError as err:
            return files
    
    # Get the parts of the expression
    exp1 = ""
    exp2 = ""
    exp3 = ""
    
    # If only one *
    if (idx == idx2):
        if (idx == 0):
            # * at beginning
            exp1 = ""
            exp2 = expression[1:]
        elif (idx == eLen - 1):
            # * at end
            exp1 = expression[:idx]
            exp2 = ""
        else:
            # * somewhere in between
            exp1 = expression[:idx]
            exp2 = expression[idx + 1:]
    else:
        # Else two *'s
        if (idx == 0):
            # First * at beginning
            exp1 = ""
            exp2 = expression[1:idx2]
            
            # Check second *
            if (idx2 == eLen - 1):
                # Second * at end
                exp3 = ""
            else:
                # Second * in middle
                exp3 = expression[idx2 + 1:]
        else:
            # First * somewhere in between
            exp1 = expression[:idx]
            exp2 = expression[idx + 1:idx2]
                  
            # Check second *
            if (idx2 == eLen - 1):
                # Second * at end
                exp3 = ""
            else:
                # Second * in middle
                exp3 = expression[idx2 + 1:]
    
    # Match when exp contains *
    for c in contents:
        # One *
        if (idx == idx2):
            # * is at the start of exp
            if (idx == 0):
                if (c.endswith(exp2)):
                    files.append(c)
            elif (idx == eLen - 1):
                # * at end
                if (c.startswith(exp1)):
                    files.append(c)
            else:
                # * somewhere in between
                if (c.startswith(exp1) and c.endswith(exp2)):
                    files.append(c)
        else:
            # Else two *'s
            if (idx == 0):
                # First * at beginning
                # Check second *
                if (idx2 == eLen - 1):
                    # Second * at end
                    if (c.contains(exp2)):
                        files.append(c)                        
                else:
                    # Second * in middle
                    if (c.endswith(exp3) and c.contains(exp2)):
                        files.append(c)                       
            else:
                # First * somewhere in between
                # Check second *
                if (idx2 == eLen - 1):
                    # Second * at end
                    if (c.startswith(exp1) and c.contains(exp2)):
                        files.append(c)     
                else:
                    # Second * in middle                    
                    if (c.startswith(exp1) and c.contains(exp2) and c.endswith(exp3)):
                        files.append(c)
    
    return files    

def getLogAgeInHours(logPath):
    try:
        result = stat(logPath)
        ageInNs = result.st_ctime_ns
        ageInS = ageInNs / 1000000000
        ageInH = ageInS / 3600
        return ageInH
    except OSError as err:
        return -1

def getExpNumLogs(logAgeInH, frequency):
    if (frequency == 0):
        # Rotate Hourly
        return floor(logAgeInH)
    elif (frequency == 1):
        # Rotate Daily
        logAgeInD = logAgeInH / 24
        return floor(logAgeInD)
    elif (frequency == 2):
        # Rotate Weekly
        logAgeInW = logAgeInH / 168
        return floor(logAgeInW)
    elif (frequency == 3):
        # Rotate Monthly
        logAgeInM = logAgeInH / 730.485
        return floor(logAgeInM)
    else:
        # Rotate Yearly
        logAgeInY = logAgeInH / 8765.82
        return floor(logAgeInY)

def verifyLogRotation(logPaths, configuration):
    compress = True
    copy = False
    copytruncate = False
    create = False
    rotate = 0
    frequency = 1
    size = ""
    maxsize = ""
    minsize = ""
    missingok = False
    maxage = -1
    ifempty = True
    delaycompress = False
    olddir = ""
    
    # Read the configuration out of the dictionary
    for key in configuration:
        val = configuration[key]
        
        if (key == "frequency"):
            if (val == "hourly"):
                frequency = 0
            elif (val == "weekly"):
                frequency = 2
            elif (val == "monthly"):
                frequency = 3
            elif (val == "yearly"):
                frequency = 4
            else:
                frequency = 1
        elif (key == "compress"):
            compress = True
        elif (key == "nocompress"):
            compress = False
        elif (key == "copy"):
            copy = True
        elif (key == "nocopy"):
            copy = False            
        elif (key == "copytruncate"):
            copytruncate = True
        elif (key == "nocopytruncate"):
            copytruncate = False
        elif (key == "create"):
            create = True
        elif (key == "nocreate"):
            create = False
        elif (key == "delaycompress"):
            delaycompress = True
        elif (key == "nodelaycompress"):
            delaycompress = False
        elif (key == "ifempty"):
            ifempty = True
        elif (key == "notifempty"):
            ifempty = False
        elif (key == "maxage"):
            maxage = int(val)
        elif (key == "maxsize"):
            maxsize = val
        elif (key == "minsize"):
            minsize = val             
        elif (key == "size"):
            size = val
        elif (key == "missingok"):
            missingok = True
        elif (key == "nomissingok"):
            missingok = False
        elif (key == "olddir"):
            olddir = val
        elif (key == "noolddir"):
            olddir = ""
        elif (key == "rotate"):
            rotate = int(val)
    
    # Check each log file pattern
    for pathExp in logPaths:
        # Parse the path        
        s = "/"
        pathArr = pathExp.split(s)
        pathArrSz = len(pathArr)
        logExp = pathArr[pathArrSz - 1]
        logDir = s.join(pathArr[:pathArrSz - 1])
        
        # Get the logs to rotate
        logs = getMatchingFiles(logDir, logExp)
        
        # Where are the old logs kept?
        if (olddir == ""):
            olddir = logDir
        
        # For each log matching the pattern
        for log in logs:
            print(logDir + "/" + log + ": ", end="")
            logAge = getLogAgeInHours(logDir + "/" + log)
                       
            # Was the log found?
            if (logAge < 0):
                if (missingok):
                    print("PASS")
                    continue
                else:
                    print("FAIL - Log not found")
                    continue
                        
            # Get the old logs
            oldLogs = getMatchingFiles(olddir, log + "*")
            
            # Don't want to count the log itself
            try:
                idx = oldLogs.index(log)
                
                # Remove the log from the list if found
                del oldLogs[idx]
            except ValueError as err:
                # The original log must not be in the old log directory
                pass
            
            # How many logs are there?
            numLogs = len(oldLogs)
            expectNumLogs = getExpNumLogs(logAge, frequency)
            
            # If no old logs
            if ((numLogs == 0) and ifempty == False):
                print("PASS")
                continue
            elif ((numLogs == 0) and (expectNumLogs != 0) and ifempty):
                print("FAIL - Expected to find more old logs")
                continue
            
            # Check the rotation count
            if (numLogs > rotate):
                print("FAIL - Found too many old logs")
                continue
            elif ((numLogs < rotate) and (numLogs < expectNumLogs) and ifempty):
                print("FAIL - Expected to find more old logs")
                continue
                
            # How many are compressed and uncompressed?
            numCompress = 0
            
            # Check the logs for compression
            for oldLog in oldLogs:
                # Is it compressed?
                if (oldLog.endswith(".gz")):
                    numCompress += 1

            # Check if compression was enabled
            if (compress):                
                # Check if delayed compression was enabled
                if ((numCompress != numLogs - 1) and delaycompress):
                    # Should be exactly 1 uncompressed log
                    print("FAIL - Found too many uncompressed logs")
                    continue
                elif ((numCompress != numLogs) and (delaycompress == False)):
                    # Should be no uncompressed log
                    print("FAIL - Expected no uncompressed logs")
                    continue                    
            elif ((compress == False) and (numCompress > 0)):
                # Shouldn't be compressing if compression is disabled
                print("FAIL - Compression disabled but found compressed logs")
                continue                
            
            print("PASS")    
    
if __name__ == '__main__':
    scriptDefs = ["postrotate","prerotate","firstaction","lastaction","preremove"]
    rotateConfigPath = "/etc/logrotate.d"
    
    # Get list of log rotate configs    
    configFiles = listdir(rotateConfigPath)
    
    # For each config file
    for file in configFiles:
        with open(rotateConfigPath + '/' + file,'r') as config:
            openCurlyFound = False
            closeCurlyFound = False
            logPaths = []
            configuration = {}
            
            # Read the file, line by line
            line = config.readline()
            script = ""
            
            while (line != ""):
                line = line.strip()
                
                # Skip parsing if it is empty
                if (len(line) < 1):
                    line = config.readline()
                    continue             
                
                # Skip comments
                if (line[0] == "#"):
                    line = config.readline()
                    continue
                
                # End of log rotation declaration found
                if ((line == "}") or (closeCurlyFound == True)):
                    verifyLogRotation(logPaths, configuration)
                    openCurlyFound = False
                    closeCurlyFound = False
                    logPaths = []
                    configuration = {}
                    script = ""
                    line = config.readline()
                    continue
                    
                # If start of log rotation declaration               
                if (openCurlyFound == False):
                    lineArr = line.split()
                    lineRem = ""
                    
                    # Loop through line word by word
                    for e in lineArr:
                        if (openCurlyFound == False):
                            # Look for log paths to rotate
                            if (e == "{"):
                                openCurlyFound = True
                            else:
                                logPaths.append(e)
                        else:
                            # If End of log rotation declaration found
                            if (e == "}"):
                                lineRem = lineRem.strip()
                                
                                if (len(lineRem) > 0):
                                    parseLine(lineRem, configuration)
                                    
                                openCurlyFound = False
                                closeCurlyFound = True
                                break
                            
                            # Else not the end of log rotation declaration
                            lineRem += e + ' '
                            
                    # End of log rotation declaration found
                    if (closeCurlyFound == True):
                        continue
                    
                    lineRem = lineRem.strip()
                    
                    # Skip parsing if it is empty
                    if (len(lineRem) < 1):
                        line = config.readline()
                        continue
                    
                    # Check for start of script
                    if (lineRem in scriptDefs):
                        script = lineRem
                    else:
                        parseLine(lineRem, configuration)
                else:
                    # Else it is body of log rotation declaration
                    idx = line.find("}")
                    
                    # If End of log rotation declaration found
                    if (idx >= 0):
                        closeCurlyFound = True
                        
                        # Check the start of the line
                        line = line[:idx]
                        line = line.strip()
                    else:
                        # Else not the end of log rotation declaration
                        # Check for start of script
                        if (line in scriptDefs):
                            script = line
                            line = config.readline()
                            continue
                        
                        if ((len(script) > 0) and (line != "endscript")):
                            script += " " + line
                            line = config.readline()
                            continue
                        
                    if (line == "endscript"):
                        line = script
                        script = ""
                        
                    parseLine(line, configuration)
                
                    # End of log rotation declaration found
                    if (closeCurlyFound == True):
                        continue
                    
                line = config.readline()
