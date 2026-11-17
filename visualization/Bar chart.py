import plotly.express as px


def bar_chart_events():
    Labels = ['LOGIN_SUCCESS', 'PASSWORD_RESET', 'VPN_CONNECT', 'PORT_SCAN_DETECTED', 'MALWARE_SIGNATURE_MATCH',
             'FILE_ACCESS_DENIED', 'VPN_DISCONNECT', 'LOGIN_FAILED', 'ACCOUNT_LOCKED', 'PRIVILEGE_ESCALATION_ATTEMPT',
             'CONFIG_CHANGE', 'USB_DEVICE_ATTACHED']
    Values = [140, 26, 67, 27, 17, 38, 57, 105, 14, 15, 22, 13]

    fig = px.bar(
        x = Labels,
        y = Values,
        labels = {
            "x" : "Event Type",
            "y" : "antal hændelse"
        },
        title = "Hændelse pr.Event Type"

    )
    fig.show()
bar_chart_events()

