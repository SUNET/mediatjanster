""" helper for kaltura sessions """

from datetime import datetime
import argparse
from KalturaClient import KalturaConfiguration, KalturaClient
from KalturaClient.exceptions import KalturaException


parser = argparse.ArgumentParser(description="Helper for kaltura sessions")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-s", "--start", help="start session", action="store_true")
group.add_argument("-e", "--end", help="end session", action="store_true")
group.add_argument("-g", "--get", help="get session", action="store_true")
parser.add_argument("-c", "--client-tag", help="client tag", metavar="client-tag")
args = parser.parse_args()
if args.start:
    partnerId = input("Enter partnerId: ")
    adminSecret = input("Enter adminSecret: ")
    conf = KalturaConfiguration()
    conf.serviceUrl = "https://api.kaltura.nordu.net"
    kc = KalturaClient(conf)
    kc.clientConfiguration["clientTag"] = args.client_tag
    ks = kc.session.start(adminSecret, None, 2, partnerId)
    kc.setKs(ks)
    print("New kalturaSession: " + ks)
elif args.get:
    kalturaSession = input("Enter kalturaSession: ")
    conf = KalturaConfiguration()
    conf.serviceUrl = "https://api.kaltura.nordu.net"
    kc = KalturaClient(conf)
    kc.setKs(kalturaSession)
    try:
        ks = kc.session.get(kalturaSession)
        print("\nkalturaSession:")
        print("sessionType: " + str(ks.sessionType.value))
        print("partnerId: " + str(ks.partnerId))
        if ks.userId:
            print("userId: " + ks.userId)
        print("expiry: " + str(datetime.fromtimestamp(ks.expiry)))
        print(ks.privileges)
    except KalturaException as error:
        print(error)
elif args.end:
    kalturaSession = input("Enter kalturaSession: ")
    conf = KalturaConfiguration()
    conf.serviceUrl = "https://api.kaltura.nordu.net"
    kc = KalturaClient(conf)
    kc.setKs(kalturaSession)
    try:
        ks = kc.session.get(kalturaSession)
        print("\nEnding kalturaSession:")
        print("sessionType: " + str(ks.sessionType.value))
        print("partnerId: " + str(ks.partnerId))
        if ks.userId:
            print("userId: " + ks.userId)
        print("expiry: " + str(datetime.fromtimestamp(ks.expiry)))
        print(ks.privileges)
        result = kc.session.end()
    except KalturaException as error:
        print(error)
