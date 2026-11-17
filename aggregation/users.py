"""Find brugeren med flest loginforsøg."""


# Finder den bruger i de grupperede rækker med flest LOGIN_FAILED.
# Bruges ikke af main.py, men kan kaldes direkte for at få den mest mistænkelige konto.
def getHighestUser(UnholyList):
    # Kun rækkerne for brugere har nøglen "User"
    users = [record for record in UnholyList if "User" in record]

    if not users:
        return None

    # max() med key vælger den række hvor LOGIN_FAILED er størst.
    # get(..., 0) bruges, hvis en bruger slet ikke har fejlede logins.
    highestUser = max(users, key=lambda x: x.get("LOGIN_FAILED", 0))
    return highestUser
