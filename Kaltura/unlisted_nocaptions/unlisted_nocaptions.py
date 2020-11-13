import sys, json
import os.path
from os import path
from datetime import timedelta, datetime
from csv import writer,QUOTE_MINIMAL,reader
import KalturaClient
from KalturaClient import *
from KalturaClient.Client import *
from KalturaClient.Base import *
from KalturaClient.Plugins import *
from KalturaClient.Plugins.Core import * 
from KalturaClient.Plugins.CaptionSearch import *
from KalturaClient.Plugins.Caption import *
from KalturaClient.Plugins.Metadata import *

# Get variables for API auth from configuration file config.json
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
    api_token_id = data['api_token_id']
    api_token = data['api_token']
    kaltura_partnerid = data['kaltura_partnerid']
    kaltura_serviceurl = data['kaltura_serviceurl']
    kaltura_userid=""
    wd_date = datetime(2020,9,23,0,0)
    today=datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename='unlisted_media_captions'+str(today)+'.csv'
    unlisted_id = data['unlisted_id']

# kalturaSession
config = KalturaConfiguration(kaltura_partnerid)
config.serviceUrl = kaltura_serviceurl
client = KalturaClient(config)
userId=""
widgetId = "_"+str(kaltura_partnerid)
expiry = 86400
result = client.session.startWidgetSession(widgetId, expiry)
client.setKs(result.ks)
tokenHash = hashlib.sha256(result.ks.encode('ascii')+api_token.encode('ascii')).hexdigest()
type = KalturaSessionType.ADMIN 
result = client.appToken.startSession(api_token_id, tokenHash, userId, type, expiry)
client.setKs(result.ks)

def unlisted_no_captions():
    filter=KalturaBaseEntryFilter()
    filter.categoriesIdsMatchAnd=unlisted_id
    from_date = datetime(wd_date.year, wd_date.month, wd_date.day, 0, 0)
    filter.createdAtGreaterThanOrEqual=from_date.timestamp()
    pager=KalturaFilterPager()
    pager.pageSize=50
    unlisted_media=client.media.list(filter,pager)
    
    totalcount=unlisted_media.totalCount
    counter=0
    page=1
    while counter<totalcount:
        pager.pageIndex=page
        unlisted_media=client.media.list(filter,pager)
        for media in unlisted_media.objects:
            caption=check_caption(media.id)
            result=[media.userId,media.id,datetime.fromtimestamp(media.createdAt)]
            try:
                label=caption.objects[0].label
                caption_amount=len(caption.objects)
                counter+=1
                continue  
            except:
                write_to_csv(result)
                get_user_email(media.userId)
                counter+=1
        page+=1

def check_caption(entryid):
    pager=KalturaFilterPager()
    pager.pageIndex=1
    pager.pageSize=50        
    assetfilter=KalturaCaptionAssetFilter()
    assetfilter.entryIdIn=entryid
    return client.caption.captionAsset.list(assetfilter,pager)
    pass

def write_to_csv(data):
    with open(filename, 'a', newline='') as csvfile:
        writefile = writer(csvfile, delimiter=',' ,quotechar=',', quoting=QUOTE_MINIMAL)
        writefile.writerow(data)

def get_user_email(id):
    result=client.user.get(id)
    global users
    if result.email in users:
        pass
    else:
        users.append(result.email)

try:
    users=[]
    unlisted_no_captions()

    users_body=""
    for user in users:
        users_body=users_body+user+";"

    if path.exists(filename):
        print(users_body)
    else:
        pass
    print("success")
except:
    print("failed")