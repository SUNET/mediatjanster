""" Helper for kaltura apptokens """

import argparse
from datetime import datetime
from KalturaClient import KalturaConfiguration, KalturaClient
from KalturaClient.Plugins.Core import (
    KalturaAppTokenFilter,
    KalturaAppToken,
    KalturaUserRoleFilter,
    KalturaFilterPager,
    KalturaAppTokenHashType,
    KalturaSessionType,
)
from KalturaClient.exceptions import KalturaException


def kaltura_session():
    """ get ks from user """
    ks = input("Enter ks: ")
    config = KalturaConfiguration()
    config.serviceUrl = "https://api.kaltura.nordu.net/"
    client = KalturaClient(config)
    client.clientConfiguration["clientTag"] = "appToken-helper"
    client.setKs(ks)
    return client


def list_app_tokens(args):
    """ list appTokens """
    client = kaltura_session()

    if args.apptoken:
        filter = KalturaAppTokenFilter()
        if args.created_at:
            createdAtFilter = datetime(
                args.created_at[0], args.created_at[1], args.created_at[2], 0, 0
            ).timestamp()
            filter.createdAtGreaterThanOrEqual = createdAtFilter
        result = client.appToken.list(filter)
        count = result.totalCount
        print("totalcount returned: " + str(count) + "\n")

        nid = 0
        while nid < count:
            for i in result.objects:
                print("id: " + i.id)
                print("token: " + i.token)
                print(i.description)
                print(
                    "created at: "
                    + datetime.fromtimestamp(i.createdAt).strftime("%c")
                    + "\n"
                )
                nid = nid + 1
    elif args.kmcroles:
        filter = KalturaUserRoleFilter()
        pager = KalturaFilterPager()
        pager.pageIndex = 1
        pager.pageSize = 500
        listroles = client.userRole.list(filter, pager)
        for i in listroles.objects:
            print(i.name + " " + str(i.id))


def delete_app_token(args):
    """ delete appToken """
    client = kaltura_session()

    client.appToken.delete(args.apptokenid)
    try:
        client.appToken.get(args.apptokenid)
    except KalturaException as error:
        if error.code == "APP_TOKEN_ID_NOT_FOUND":
            print("appToken deleted")


def add_app_token(args):
    """ add appToken """
    client = kaltura_session()
    apptoken = KalturaAppToken()
    apptoken.description = args.desc
    apptoken.hashType = KalturaAppTokenHashType.SHA256
    apptoken.sessionType = KalturaSessionType.ADMIN
    apptoken.sessionPrivileges = "setrole:" + args.kmcrole
    result = client.appToken.add(apptoken)
    print("New appToken created at: " + str(datetime.fromtimestamp(result.createdAt)))
    print("id: " + result.id)
    print("token: " + result.token)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Helper for Kaltura apptokens")
    subparsers = parser.add_subparsers(dest="function", help="sub-command help")
    subparsers.required = True
    parser_add = subparsers.add_parser("add", help="add appToken")
    parser_add.add_argument("desc", help="appToken description", type=str)
    parser_add.add_argument("kmcrole", help="appToken description", type=str)
    parser_add.set_defaults(func=add_app_token)
    parser_list = subparsers.add_parser("list", help="list appTokens or KMC roles")
    parser_list.add_argument(
        "-a", "--apptoken", help="list appTokens", action="store_true"
    )
    parser_list.add_argument(
        "-c",
        "--created-at",
        type=int,
        help="appTokens created after",
        nargs=3,
        metavar=("YYYY", "MM", "DD"),
    )
    parser_list.add_argument(
        "-k", "--kmcroles", help="list KMC roles", action="store_true"
    )
    parser_list.set_defaults(func=list_app_tokens)
    parser_delete = subparsers.add_parser("delete", help="delete appToken")
    parser_delete.add_argument("apptokenid", help="appToken id")
    parser_delete.set_defaults(func=delete_app_token)
    args = parser.parse_args()

    args.func(args)
