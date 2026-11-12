
def filtering(records):
    #Alle disse bruges til forskellige former for record keeping
    everyUser = []
    everyLevel = []
    everyEvent = []
    everyStatus = []
    everyDict = []
    UserDict = {}
    LevelDict = {}
    EventDict = {}
    StatusDict = {}
    for i in range(len(records)):
        if not records[i].user in everyUser:
            everyUser.append(records[i].user)
        if not records[i].level in everyLevel:
            everyLevel.append(records[i].level)    
        if not records[i].event in everyEvent:
            everyEvent.append(records[i].event)
        if not records[i].status in everyStatus:
            everyStatus.append(records[i].status)
    everyUser.sort()
    everyLevel.sort()
    everyEvent.sort()
    everyStatus.sort()
    #her går vi igennem alle records og tæller hvor mange gange hver user, level, event og status forekommer. Dette gemmes i en dictionary som til sidst returneres
    for x in range(len(everyUser)):
        Instance = 0
        for z in range(len(records)):
            if records[z].user == everyUser[x]:
                Instance = Instance +1
        UserDict[everyUser[x]] = Instance
    for x in range(len(everyLevel)):
        Instance = 0
        for z in range(len(records)):
            if records[z].level == everyLevel[x]:
                Instance = Instance +1
        LevelDict[everyLevel[x]] = Instance
    for x in range(len(everyEvent)):
        Instance = 0
        for z in range(len(records)):
            if records[z].event == everyEvent[x]:
                Instance = Instance +1
        EventDict[everyEvent[x]] = Instance
    for x in range(len(everyStatus)):
        Instance = 0
        for z in range(len(records)):
            if records[z].status == everyStatus[x]:
                Instance = Instance +1
        StatusDict[everyStatus[x]] = Instance
    #Sammel alle dicts med data i en liste som returneres sammen med procentdelen af login failures
    everyDict.append(UserDict)   
    everyDict.append(LevelDict) 
    everyDict.append(EventDict)
    everyDict.append(StatusDict)
    LoginSucces = EventDict.get("LOGIN_SUCCESS")
    LoginFail = EventDict.get("LOGIN_FAILED")
    LoginTotal = LoginSucces + LoginFail
    LoginProcent = LoginFail/LoginTotal
    return everyDict, LoginProcent