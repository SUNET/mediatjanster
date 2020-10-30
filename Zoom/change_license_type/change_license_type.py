import json, sys, http.client, time, getopt, jwt
from datetime import datetime,timedelta
from csv import writer,QUOTE_MINIMAL,reader
from pathlib import Path

# Default config path (relative to where script is run)
config="config.json"


# FUNCTIONS

# Get a jwt (json web token) from Zoom using API key and API secret generated at zoom marketplace
def get_jwt():
	payload = {
	"iss": zoom_api_key,
	"exp": datetime.now() + timedelta(seconds = jwt_valid_seconds)
	}
	result=str(jwt.encode(payload, zoom_api_secret))
	result=result[2:-1]
	return result

# Get the page count for list of Zoom users in your account
def api_get_pagecount():
    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
    'authorization': "Bearer "+get_jwt(),
    'content-type': "application/json"
    }

    conn.request("GET", "/v2/users?page_size=300", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    raw_data = json.loads(data.decode('utf-8'))
    print('number of pages in API user import: '+str(raw_data['page_count']))
    return (raw_data['page_count'])

# Get all users (300) from a specific page
def api_get_users(pagenumber):
    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
    'authorization': "Bearer "+get_jwt(),
    'content-type': "application/json"
    }
 
    conn.request("GET", "/v2/users?page_number="+str(pagenumber)+"&page_size=300", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode('utf-8'))
    time.sleep(2)

# Print change_license_type syntax
def help():
    # Print out instructions for usage
    print("\nusage: change_license_type [-e days] [-f filename] [-b] [-l] [-o] [-h]\n")
    print("                  Syntax:\n")
    print("                  -h or --help")
    print("                  Show syntax\n")
    print("                  -e [n] or --export [n]")
    print("                  Export a csv file of users in your account that have not been logged in for n days\n")
    print("                  -f [filename] or --file [filename]")
    print("                  Give csv file of users to parse as input\n")
    print("                  -b or --basic")
    print("                  Change license type to basic\n")
    print("                  -l or --licensed")
    print("                  Change license type to licensed\n")
    print("                  -o or --onprem")
    print("                  Change license type to on-prem\n")
    print("                  Append your Zoom API key and secret to config.json\n")
    print("                  -a or --assume-yes")
    print("                  Assume yes, necessary for running headless\n")
    print("                  -j [filename] or --json-file [filename]")
    print("                  Add optional filepath for config.json\n")

# Write list of users not logged in for [n] days to csv file
def write_csv_file(filename):
    pagecount=api_get_pagecount()
    page_number=1
    user_count=0
    with open(filename, 'a', newline='') as csvfile:
        print("printing categories!")
        writecategories = writer(csvfile, delimiter=',',
                                quotechar=',', quoting=QUOTE_MINIMAL)
        writecategories.writerow(['e-mail'] + ['last login time'] + ['status'])

    while page_number <= pagecount:
        print("printing page: "+str(page_number))
        with open(filename, 'a', newline='') as csvfile:
            writeusers = writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=QUOTE_MINIMAL)    
            raw_data=api_get_users(page_number)
            for user in raw_data['users']:
                user_count=user_count+1
                if "@" not in user['email']:
                    email = user['id']
                else:
                    email = user['email']
                # license type. Basic=1, Licensed=2, On-premise=3
                license_type = (user['type'])
                
                if license_type == 1:
                    continue
                try:
                    user['last_login_time']
                except:
                    last_login_time_append = "Never logged in"
                    if license_type != 1:
                        login_status = "Check manually"
                        writeusers.writerow([email] + [last_login_time_append] + [login_status])
                    else:
                        continue
                else:
                    last_login_time = datetime.strptime((user['last_login_time']), '%Y-%m-%dT%H:%M:%SZ')
                    last_login_time_append = last_login_time.strftime("%Y-%m-%d %H:%M:%S")
                    if license_type != 1 and last_login_time < last_login_days_setting:
                        login_status = "Change license type"
                        writeusers.writerow([email] + [last_login_time_append] + [login_status])
            print(" "+str(user_count))
        page_number=page_number+1

# Change user type. Available type parameters: 1=basic, 2=licensed, 3=onpremise
def api_change_license_type(email,type):
    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
    'authorization': "Bearer "+get_jwt(),
    'content-type': "application/json"
    }
    payload = "{\"type\":\""+str(type)+"\"}"    
 
    conn.request("PATCH", "/v2/users/"+email, payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    print (data.decode("utf-8"))

# Parse csv file
def parse_csv_file(csv_file):
    with open(csv_file, newline='') as csvfile:
        users = reader(csvfile)
        i=0
        for row in users:
            if row[0] != "e-mail":
                global answer_all
                try:
                    print(row[0])
                    if answer_all == "y" or answer_all == "Y":
                        api_change_license_type(row[0],change_to)
                        continue
                except:
                    # dont change all
                    pass
                try:
                    if row[2] == "Check manually":
                        answer=None
                        while answer not in ("y", "Y", "n", "N"):
                            print(row[0]+" should be checked manually. ")
                            answer = input("Change to "+change_to_text+" anyway? (y/n): ")
                            if answer == "y" or answer == "Y":
                                api_change_license_type(row[0],change_to)
                                answer_all = input("Answer yes to all? (y/n): ")
                            elif answer =="n" or answer == "N":
                                continue
                            else:
                                print("Please enter y/n")
                except:
                    print('no status')
                try:
                    if row[2] == "Change license type":
                        answer=None
                        while answer not in ("y", "Y", "n", "N"):
                            print("User: "+row[0])
                            answer = input("Change to "+change_to_text+"? (y/n): ")
                            if answer == "y" or answer == "Y":
                                api_change_license_type(row[0],change_to)
                                answer_all = input("Answer yes to all? (y/n): ")
                            elif answer =="n" or answer == "N":
                                continue
                            else:
                                print("Please enter y/n")
                except:
                    print('no status')
                i=i+1

# MAIN CODE



if __name__ == "__main__":

    # examine options given by user
    try:
        opts, args = getopt.getopt(sys.argv[1:],"e:f:j:c:bloha",["export=","file=","basic","licensed","onprem","help","assume-yes","json-file=","csv-file="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()
        elif opt in ("-e", "--export"):
            last_login_days_setting = datetime.now() - timedelta(days=int(arg))
        elif opt in ("-b", "--basic"):
            change_to=1
            change_to_text="basic"
        elif opt in ("-l", "--licensed"):
            change_to=2
            change_to_text="licensed"
        elif opt in ("-o", "--onprem"):
            change_to=3
            change_to_text="on-prem"
        elif opt in ("-f", "--file"):
            csv_input_file=arg
        elif opt in ("-j", "--json-file"):
            config=arg
        elif opt in ("-c", "--csv-file"):
            csv_output_file=arg
        elif opt in ("-a", "--assume-yes"):
            answer_all="y"
        else:
            usage()
            sys.exit(2)

# Get variables for API auth from configuration file config.json
with open(config) as json_data_file:
    data = json.load(json_data_file)
    zoom_api_key = data['zoom_api_key']
    zoom_api_secret = data['zoom_api_secret']
    jwt_valid_seconds = data['jwt_valid_seconds']

    # are we going to create csv file?
    try:
        last_login_days_setting
    except NameError:
        # variable last_login_days_setting not defined. moving on!
        pass
    else:
        # Create variable with current date+time unless predefined
        print(csv_output_file)
        try: 
            csv_output_file
            output_filename=csv_output_file
        except NameError:
            output_filename = '{}.csv'.format( datetime.now().strftime('%Y%m%d%H%M%S') )
        print('List of users will be written to: '+output_filename)
        api_get_pagecount()    
        write_csv_file(output_filename)
    try:
        change_to
    except NameError:
        # we're not going to change anyones license type
        pass
    else:
        # was a csv file created? parse it
        try:
            output_filename
        except NameError:
            # No csv file has been created
            pass
        else:
            parse_csv_file(output_filename)

        # was a csv file given by user? parse it           
        try:
            csv_input_file
        except NameError:
            # variable csv_input_file not defined. moving on!
            pass
        else:
            parse_csv_file(csv_input_file)
