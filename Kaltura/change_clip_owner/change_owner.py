# Change owner for the latest entry clipped from a live event
# The clip must have been created within 4 minutes
# argv1= userid, argv2=base entryid for live event (clipped from), argv3=partnerid, argv4=apptoken id, argv5=apptoken 

import time,hashlib,sys
from datetime import datetime,timedelta
from KalturaClient import *
from KalturaClient.Plugins.Core import *

def change_media_owner(entryId,new_owner):
    mediaEntry=KalturaMediaEntry()
    mediaEntry.userId=new_owner
    change=client.media.update(entryId,mediaEntry)

def get_latest_clipped_media(base_entry):
    # Check if entry was created within 4 minutes
    filter=KalturaMediaEntryFilter()
    filter.sourceTypeIn=36
    filter.createdAtGreaterThanOrEqual=time.time()-240
    pager=KalturaFilterPager()
    pager.pageIndex=1
    result=client.media.list(filter,pager)
    for i in result.objects:
        if i.rootEntryId == base_entry:
            return i.id

# SESSION CONFIG APPTOKEN
partner_id=sys.argv[3]
config = KalturaConfiguration(partner_id)
config.serviceUrl = "https://api.kaltura.nordu.net/"
client = KalturaClient(config)

id=sys.argv[4]
token=sys.argv[5]
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

time.sleep(85)
entryid=get_latest_clipped_media(sys.argv[2])
new_user=sys.argv[1]+"@gu.se"
change_media_owner(entryid,new_user)
