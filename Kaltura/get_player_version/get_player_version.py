import time,hashlib,sys
from datetime import datetime,timedelta
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from csv import writer,QUOTE_MINIMAL,reader


def get_uiconf(uiconftype):
    filter = KalturaUiConfFilter()
    filter.objTypeIn = uiconftype
    pager = KalturaFilterPager()
    pager.pageSize=500
    pager.pageIndex=1

    uiconf_array = client.uiConf.list(filter, pager)
    totalcount = uiconf_array.totalCount

    nid=1
    body=[]
    while nid < totalcount:
        for uiconf_entry in uiconf_array.objects:
            player=[str(uiconf_entry.id),uiconf_entry.name,uiconf_entry.html5Url]
            nid = nid + 1
            body.append(player)
        pager.pageIndex = pager.pageIndex + 1
    return body

def write_csv_file(write_body,filename):
    with open(filename, 'a', newline='') as csvfile:
        print("printing categories!")
        write_categories = writer(csvfile, delimiter=',',
                                quotechar=',', quoting=QUOTE_MINIMAL)
        write_categories.writerow(['id'] + ['player_name'] + ['html5Url'])


    with open(filename, 'a', newline='') as csvfile:
        write = writer(csvfile, delimiter=',')
        write.writerows(write_body)

# SESSION CONFIG APPTOKEN
partner_id="your partner ID"
config = KalturaConfiguration(partner_id)
config.serviceUrl = "https://api.kaltura.nordu.net/"
client = KalturaClient(config)

id="apptokenid"
token="apptoken"
userId=""

# GENERATE SESSION

widgetId = "_"+str(partner_id)
expiry = 86400
result = client.session.startWidgetSession(widgetId, expiry)
client.setKs(result.ks)
tokenHash = hashlib.sha256(result.ks.encode('ascii')+token.encode('ascii')).hexdigest()
type = KalturaSessionType.ADMIN 

result = client.appToken.startSession(id, tokenHash, userId, type, expiry)
client.setKs(result.ks)

result=get_uiconf("1,8")
write_csv_file(result,"players.csv")