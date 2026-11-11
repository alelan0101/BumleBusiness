def getHighestUser(UnholyList):
    if not UnholyList:
        return None  # Return None if the list is empty

    highestUser = max(UnholyList, key=lambda x: x.get("LOGIN_FAILED", 0))
    return highestUser