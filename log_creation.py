#Laver dictionary, som der indeholder alle de værdiger, som den indhenter gennem parser
def Memory(name,timestamp,event,user,level,src,dest,port,status,msg):
    name=dict(
    time=timestamp,
    event=event,
    who=user,
    level=level,
    src=src,
    dest=dest,
    port=port,
    status=status,
    msg=msg,
    )
    return name