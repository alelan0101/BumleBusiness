def highestTabel(AllData,records):
    import highestUse
    listOfKeysUsers = []
    listOfKeysEvents = []
    listOfKeysStauts = []
    listOfKeysLevel = []
    UnholyList = []
    for i in range(len(AllData)):
        for key in AllData[i]:
            for z in range(len(records)):
                if key in records[z].user:
                    if not key in listOfKeysUsers:
                        listOfKeysUsers.append(key)
                if key in records[z].event:
                    if not key in listOfKeysEvents:
                        listOfKeysEvents.append(key)
                if key in records[z].status:
                    if not key in listOfKeysStauts:
                        listOfKeysStauts.append(key)
                if key in records[z].level:
                    if not key in listOfKeysLevel:
                        listOfKeysLevel.append(key)
    for i in range(len(listOfKeysUsers)):
        NewDict = {}
        NewDict["User"] = listOfKeysUsers[i]
        for z in range(len(listOfKeysEvents)):
            for x in range(len(records)):
                if listOfKeysUsers[i] in records[x].user and listOfKeysEvents[z] in records[x].event:
                    if not listOfKeysEvents[z] in NewDict:
                        NewDict[listOfKeysEvents[z]] = 1
                    else:
                        NewDict[listOfKeysEvents[z]] += 1
        for z in range(len(listOfKeysStauts)):
            for x in range(len(records)):
                if listOfKeysUsers[i] in records[x].user and listOfKeysStauts[z] in records[x].status:
                    if not listOfKeysStauts[z] in NewDict:
                        NewDict[listOfKeysStauts[z]] = 1
                    else:
                        NewDict[listOfKeysStauts[z]] += 1
        for z in range(len(listOfKeysLevel)):
            for x in range(len(records)):
                if listOfKeysUsers[i] in records[x].user and listOfKeysLevel[z] in records[x].level:
                    if not listOfKeysLevel[z] in NewDict:
                        NewDict[listOfKeysLevel[z]] = 1
                    else:
                        NewDict[listOfKeysLevel[z]] += 1
        UnholyList.append(NewDict)

    print(highestUse.getHighestUser(UnholyList))

    
    #UnholyList.sort(key=lambda x: x.get("LOGIN_FAILED", 0), reverse=True)
    #print(f"UnholyList: {UnholyList[0:9].get('User', 'Unknown') if UnholyList else 'Empty'}")