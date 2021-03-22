"""
this code is intended to assist you during a domain change
it let you export information about media and users to csv
then you can update your user and mediaentries in Kaltura

example:

change userId from 'user1@old-org.org' to user1@new-org.org'
and transfer ownership of media entries
"""

import argparse
from csv import writer, QUOTE_MINIMAL, reader
from datetime import date
from collections import Counter
import logging
import os
import sys
from math import ceil
from rich.console import Console
from rich.progress import track
from rich.table import Table
from KalturaClient import KalturaConfiguration, KalturaClient
from KalturaClient.Plugins.Core import (
    KalturaMediaEntryFilter,
    KalturaFilterPager,
    KalturaUserFilter,
    KalturaUser,
    KalturaMediaEntry,
)


# logging configuration
FILENAME = "change_domain_" + str(date.today()) + ".log"
logging.basicConfig(
    filename=FILENAME,
    format=" %(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
)


def kaltura_session():
    """ get kaltura_session from user """
    kaltura_session = input("Enter ks: ")
    config = KalturaConfiguration()
    config.serviceUrl = "https://api.kaltura.nordu.net/"
    client = KalturaClient(config)
    client.clientConfiguration["clientTag"] = "change_domain-helper"
    client.setKs(kaltura_session)
    return client


def write_to_csv(filename, export_data):
    """ write export to csv """

    with open(filename, "a", newline="") as csvfile:
        write_to_file = writer(
            csvfile, delimiter=",", quotechar=",", quoting=QUOTE_MINIMAL
        )
        # _count = len(export_data.keys())

        for key, value in track(export_data.items(), description="Writing " + filename):
            write_to_file.writerow([key] + value)


def get_total_count(client, type):
    """ get totalcount int """

    pager = KalturaFilterPager()
    pager.pageSize = 1
    if type.lower() == "users":
        filter = KalturaUserFilter()
        result = client.user.list(filter, pager)
        total_count = result.totalCount
    if type.lower() == "media":
        filter = KalturaMediaEntryFilter()
        result = client.media.list(filter, pager)
        total_count = result.totalCount
    return total_count


def print_overview(total_count):
    """ Print initial overview to console """
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Totalcount", style="dim", width=12)
    table.add_column("Pages")
    table.add_row(str(total_count), str(ceil(total_count / 300)))
    console.print(table)


def export_users(client, total_count):
    """
    export users and returns python dictionary
    kmc users are stored as a dictionary in kmc key
    kms users are stored as a dictionary in kms key
    """

    filter = KalturaUserFilter()
    pager = KalturaFilterPager()
    pager.pageSize = 300
    page_count = 1
    user_return_dict = {"kmc": {}, "kms": {}}
    domain_list = []
    user_type_count_kms = 0
    user_type_count_kmc = 0
    print_overview(total_count)

    # Iterate on KalturaUserListResponse objects
    while page_count <= ceil(total_count / 300):
        pager.pageIndex = page_count
        result = client.user.list(filter, pager)
        for user_entry in track(
            result.objects, description="Exporting page " + str(page_count)
        ):
            domain = user_entry.id
            domain = domain.split("@", 1)
            if len(domain) < 2:
                # We disregard KalturaUser objects without domain in userId
                continue
            domain_list.append(domain[1])

            if user_entry.isAdmin is True:
                user_type = "kmc"
                user_type_count_kmc += 1

            else:
                user_type = "kms"
                user_type_count_kms += 1

            user_return_dict[user_type][user_entry.id] = [user_entry.email]

        # output summary to console
        domain_list_tmp = Counter(domain_list)
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Domain", style="dim", width=12)
        table.add_column("count")
        for domain, count in domain_list_tmp.items():
            table.add_row(domain, str(count))
        console.print(table)

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Users", style="dim", width=12)
        table.add_column("Count")
        table.add_row("Total", str(user_type_count_kms + user_type_count_kmc))
        table.add_row("KMS", str(user_type_count_kms))
        table.add_row("KMC", str(user_type_count_kmc))
        console.print(table)

        page_count += 1

    return user_return_dict


def export_media(client, total_count):
    """
    export and returns python dictionary
    key = media owners
    value = list of entryId
    """

    filter = KalturaMediaEntryFilter()
    pager = KalturaFilterPager()
    pager.pageSize = 300
    page_count = 1
    media_return_dict = {}
    domain_list = []
    print_overview(total_count)

    # Iterate on KalturaMediaListResponse objects
    while page_count <= ceil(total_count / 300):
        pager.pageIndex = page_count
        result = client.media.list(filter, pager)
        for media_entry in track(
            result.objects, description="Exporting page " + str(page_count)
        ):
            domain = media_entry.userId
            domain = domain.split("@", 1)
            if len(domain) < 2:
                # We disregard KalturaMediaEntry objects owned by userId without domain
                continue
            domain_list.append(domain[1])
            if media_entry.userId not in media_return_dict:
                media_return_dict[media_entry.userId] = [media_entry.id]
            else:
                media_return_dict[media_entry.userId].append(media_entry.id)

            # Look for Kaltura Capture entryId if mediaType = VIDEO
            media_type_check = media_entry.mediaType
            if media_type_check.value not in [2, 5, 201, 202, 203, 204]:
                logging.debug(
                    media_entry.id + ": mediaType is VIDEO. Check if multi_video"
                )
                multi_video_filter = KalturaMediaEntryFilter()
                multi_video_filter.parentEntryIdEqual = media_entry.id
                multi_video_pager = KalturaFilterPager()
                multi_video_search = client.media.list(
                    multi_video_filter, multi_video_pager
                )
                if len(multi_video_search.objects) > 0:
                    for multi_video_entry in multi_video_search.objects:
                        media_return_dict[media_entry.userId].append(
                            multi_video_entry.id
                        )
            else:
                logging.debug(
                    media_entry.id
                    + ": mediaType is not VIDEO. Don't check if multi_video"
                )

        # Output summary to console
        domain_list_tmp = Counter(domain_list)
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Domain", style="dim", width=12)
        table.add_column("count")
        for domain, count in domain_list_tmp.items():
            table.add_row(domain, str(count))
        console.print(table)
        page_count += 1

    return media_return_dict


def file_len(filename):
    """ get line count of file """

    with open(filename) as csvfile_linecount:
        for line, content in enumerate(csvfile_linecount):
            pass
    return line + 1


def change_user_object(client, filename, newdomain, subdomains):
    """ change user objects to new domain """

    with open(filename, "r") as csvfile:
        logging.debug("parsing " + filename)
        line_count = file_len(filename)
        change_data = reader(csvfile)
        for user in track(
            change_data, total=line_count, description="Updating users objects"
        ):
            logging.debug(user)
            new_id = exchange_domain(user[0], newdomain, subdomains)
            update_body = KalturaUser()
            update_body.id = new_id
            if user[1] != "":
                new_email = exchange_domain(user[1], newdomain, subdomains)
                update_body.email = new_email

            try:
                client.user.update(user[0], update_body)
            except Exception as error:
                logging.error("error: ", exc_info=error)


def change_mediaentry_objects(client, filename, newdomain, subdomains):
    """ change mediaEntry objects to new domain """

    with open(filename, "r") as csvfile:
        logging.debug("parsing " + filename)
        line_count = file_len(filename)
        change_data = reader(csvfile)
        for user in track(
            change_data, total=line_count, description="Updating mediaEntry objects"
        ):
            logging.debug(user)
            new_id = exchange_domain(user[0], newdomain, subdomains)
            for media_entry in user[1:]:
                if media_entry == "":
                    continue
                update_body = KalturaMediaEntry()
                update_body.userId = new_id
                try:
                    client.media.update(media_entry, update_body)
                except Exception as error:
                    logging.error("error: ", exc_info=error)


def readable_file(filename):
    """ check if a readable file was provided as argument """
    if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
        raise argparse.ArgumentTypeError("File not found (or nor readable)")
    return filename


def exchange_domain(old_domain, newdomain, subdomains):
    old_domain = old_domain.split("@", 1)

    # subdomain handler
    if subdomains is True and len(old_domain[1].split(".")) > 2:
        full_suffix = old_domain[1].split(".")
        append_domain = "."
        append_domain = append_domain.join(full_suffix[:-2]) + "." + newdomain
    else:
        append_domain = newdomain
    new_id = old_domain[0] + "@" + append_domain

    return new_id


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="change_domain", description="Helper for kaltura domain change"
    )
    subparsers = parser.add_subparsers(dest="function", help="sub-commands")
    subparsers.required = True
    parser_export = subparsers.add_parser("export", help="export current state to csv")
    parser_export.add_argument(
        "-t",
        "--type",
        action="append",
        help="export users and/or media to csv",
        metavar="users,media",
        required=True,
    )
    parser_change = subparsers.add_parser("change", help="perform changes")
    parser_change.add_argument(
        "-f",
        "--file",
        action="append",
        help="csv file to parse",
        metavar="file",
        type=readable_file,
        required=True,
    )
    parser_change.add_argument(
        "-u",
        "--users",
        action="store_true",
        help="change userId and email",
    )
    parser_change.add_argument(
        "-m",
        "--media",
        help="change media ownership",
        action="store_true",
    )
    parser_change.add_argument(
        "-s", "--subdomains", action="store_true", help="keep subdomains"
    )
    parser_change.add_argument(
        "-n",
        "--newdomain",
        action="append",
        metavar="domain",
        required=True,
        help="new domain, e.g. newdomain.org",
    )

    args = parser.parse_args()

    if args.function == "export":
        logging.debug("doing export")
        client = kaltura_session()
        if "media" in args.type:
            total_count = get_total_count(client, "media")
            logging.debug("exporting media")
            export_data = export_media(client, total_count)
            write_to_csv("media_export_" + str(date.today()) + ".csv", export_data)

        if "users" in args.type:
            total_count = get_total_count(client, "users")
            logging.debug("exporting users")
            export_data = export_users(client, total_count)
            write_to_csv(
                "kmc_user_export_" + str(date.today()) + ".csv", export_data["kmc"]
            )
            write_to_csv(
                "kms_user_export_" + str(date.today()) + ".csv", export_data["kms"]
            )

    if args.function == "change":
        if args.users is False and args.media is False:
            print(
                "Atleast one of --users or --media is required when doing domain change."
            )
            sys.exit(1)

        logging.debug("doing change")
        client = kaltura_session()

        if args.media is True and args.file is not None:
            logging.debug("changing media")
            change_mediaentry_objects(
                client, args.file[0], args.newdomain[0], args.subdomains
            )

        if args.users is True and args.file is not None:
            logging.debug("changing users")
            change_user_object(
                client, args.file[0], args.newdomain[0], args.subdomains
            )
