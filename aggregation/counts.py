"""Optælling af events pr. level, event, status og bruger."""


# Tæller hvor mange gange hver bruger, level, event og status optræder i loggen.
# Returnerer en liste med fire dictionaries og andelen af login-forsøg der fejlede.
def count_by_field(records):
    # Fire lister til at samle de unikke værdier, og fire dictionaries til at tælle hvor mange gange hver værdi optræder
    everyUser = []
    everyLevel = []
    everyEvent = []
    everyStatus = []
    everyDict = []
    UserDict = {}
    LevelDict = {}
    EventDict = {}
    StatusDict = {}

    # Første gennemløb: saml de unikke værdier i listerne
    for i in range(len(records)):
        if not records[i].user in everyUser:
            everyUser.append(records[i].user)
        if not records[i].level in everyLevel:
            everyLevel.append(records[i].level)
        if not records[i].event in everyEvent:
            everyEvent.append(records[i].event)
        if not records[i].status in everyStatus:
            everyStatus.append(records[i].status)

    # Sorter de unikke værdier, så dictionaries bliver i alfabetisk rækkefølge
    everyUser.sort()
    everyLevel.sort()
    everyEvent.sort()
    everyStatus.sort()
    # For hver unik værdi går vi gennem alle records og tæller, hvor mange der har den værdi. Det er to løkker: en over de unikke værdier og en over alle records.
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
    # Læg de fire dictionaries i en liste, så de kan returneres samlet: først brugere, så levels, events og til sidst statusser
    everyDict.append(UserDict)
    everyDict.append(LevelDict)
    everyDict.append(EventDict)
    everyDict.append(StatusDict)
    # Andelen af login-forsøg der fejlede. get(..., 0) bruges, fordi loggen måske slet ikke indeholder den slags event.
    LoginSucces = EventDict.get("LOGIN_SUCCESS", 0)
    LoginFail = EventDict.get("LOGIN_FAILED", 0)
    LoginTotal = LoginSucces + LoginFail

    # Undgå division med nul, hvis loggen ikke har nogen login-forsøg
    LoginProcent = LoginFail/LoginTotal if LoginTotal else 0.0

    return everyDict, LoginProcent
