def convert_from_Complied_Data(UnholyList,Keys):
    #Speedrunning a filtering system
    SearchList = []
    for i in range(len(UnholyList)):
        for key in Keys:
            if key in UnholyList[i]:
                SearchList.append(UnholyList[i][key])
    return SearchList
