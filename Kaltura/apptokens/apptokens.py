import json,time,hashlib,sys
from datetime import datetime,timedelta
from KalturaClient import *
from KalturaClient.Plugins.Core import *

def add_token(desc,priv):
    appToken = KalturaAppToken()
    appToken.description = desc
    appToken.hashType = KalturaAppTokenHashType.SHA256
    appToken.sessionType = KalturaSessionType.ADMIN
    appToken.sessionPrivileges = "setrole:"+priv
    client.appToken.add(appToken)

def list_apptoken(from_date):
    filter =  	KalturaAppTokenFilter()
    filter.createdAtGreaterThanOrEqual = from_date
    appToken = KalturaAppToken()
    result = client.appToken.list(filter)
    count=result.totalCount
    print('total apptokens created after '+datetime.fromtimestamp(from_date).strftime('%c')+': '+str(count))
    time.sleep(3)
    nid=0
    while nid < count:
        for i in result.objects:
            skapad=datetime.fromtimestamp(i.createdAt).strftime('%c')
            print(skapad)
            print(i.description)
            print(i.token)
            print(i.id)
            nid=nid +1

def delete_apptoken(id):
    delete=client.appToken.delete(id)

# SESSION CONFIG
kaltura_partner_id = ""
kaltura_admin_secret = ""
kaltura_admin_userid = ""
config = KalturaConfiguration()
config.serviceUrl = "https://api.kaltura.nordu.net/"
client = KalturaClient(config)
ks = client.session.start(
	kaltura_admin_secret,
	kaltura_admin_userid,
	KalturaSessionType.ADMIN,
	kaltura_partner_id)
client.setKs(ks)

# LIST APPTOKENS
# uncomment to list apptokens created from a certain datetime
#list_apptoken(datetime(2020, 6, 19, 0, 0).timestamp())

# ADD APPTOKEN
# uncomment to add apptoken
#apptoken_description="description of apptoken"
#kmcroleid="123456789"
#add_token(apptoken_description,kmcroleid)

# DELETE APPTOKEN
# uncomment to delete apptoken
#apptokenid=""
#delete_apptoken(apptokenid)

# LIST KMC ROLES
# uncomment to list your KMC roles to get kmcroleid
#filter=KalturaUserRoleFilter()
#pager=KalturaFilterPager()
#pager.pageIndex=1
#pager.pageSize=500
#listroles=client.userRole.list(filter,pager)
#print(listroles)
#for i in listroles.objects:
#    print(i.name+" "+str(i.id))
