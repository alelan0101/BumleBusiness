def highestTabel(AllData,records):
    import highestUse
    #Her laves en liste til at kunne track, hvor mange af hvert forskellig key der findes
    listOfKeysUsers = []
    listOfKeysEvents = []
    listOfKeysStauts = []
    listOfKeysLevel = []
    Complied_Data = []
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
    #Loop herunder bruges til at indsamle alle data i en dictionary som til sidst bliver tilføjet til en liste. Listen bliver returneret og kan bruges til at finde den user med flest login failures
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
                    if not "Events" in NewDict:
                        NewDict["Events"] = 1
                    else:   
                        NewDict["Events"] += 1
        for z in range(len(listOfKeysStauts)):
            for x in range(len(records)):
                if listOfKeysUsers[i] in records[x].user and listOfKeysStauts[z] in records[x].status:
                    if not listOfKeysStauts[z] in NewDict:
                        NewDict[listOfKeysStauts[z]] = 1
                    else:
                        NewDict[listOfKeysStauts[z]] += 1
                    if not "Status" in NewDict:
                        NewDict["Status"] = 1
                    else:   
                        NewDict["Status"] += 1
        for z in range(len(listOfKeysLevel)):
            for x in range(len(records)):
                if listOfKeysUsers[i] in records[x].user and listOfKeysLevel[z] in records[x].level:
                    if not listOfKeysLevel[z] in NewDict:
                        NewDict[listOfKeysLevel[z]] = 1
                    else:
                        NewDict[listOfKeysLevel[z]] += 1
                    if not "Level" in NewDict:
                        NewDict["Level"] = 1
                    else:   
                        NewDict["Level"] += 1
        Complied_Data.append(NewDict)

    return Complied_Data

    
    #UnholyList.sort(key=lambda x: x.get("LOGIN_FAILED", 0), reverse=True)
    #print(f"UnholyList: {UnholyList[0:9].get('User', 'Unknown') if UnholyList else 'Empty'}")