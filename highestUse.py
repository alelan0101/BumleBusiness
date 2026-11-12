def getHighestUser(UnholyList):
    users = [record for record in UnholyList if "User" in record]
    if not users:
        return None  # Return None if the list is empty

    highestUser = max(users, key=lambda x: x.get("LOGIN_FAILED", 0))
    return highestUser