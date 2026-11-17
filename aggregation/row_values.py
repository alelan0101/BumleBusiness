"""Udtræk af værdier fra de grupperede rækker."""


# Trækker bestemte værdier ud af de grupperede rækker.
# Eksempel: med Keys = ["User", "LOGIN_FAILED"] fås en liste med brugernavne og deres antal fejlede logins.
def convert_from_Complied_Data(UnholyList,Keys):

    SearchList = []

    # Gå gennem alle rækker og hent de nøgler der bliver spurgt efter
    for i in range(len(UnholyList)):
        for key in Keys:
            # Spring rækker over hvor nøglen ikke findes, fx har rækkerne for IP'er og porte hverken "User" eller "LOGIN_FAILED"
            if key in UnholyList[i]:
                SearchList.append(UnholyList[i][key])
    return SearchList
