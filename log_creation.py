#Laver dictionary, som der indeholder alle de værdiger, som den indhenter gennem parser
def Memory(event, user, level, src, dest, port, status, timestamp, msg, name):
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