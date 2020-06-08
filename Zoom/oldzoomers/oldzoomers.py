import json, sys, http.client, time, getopt, jwt
from datetime import datetime,timedelta
from csv import writer,QUOTE_MINIMAL,reader
from pathlib import Path

# Get variables for API auth from configuration file config.json
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
    zoom_api_key = data['zoom_api_key']
    zoom_api_secret = data['zoom_api_secret']
    jwt_valid_seconds = data['jwt_valid_seconds']

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
    raw_data = json.loads(data)
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
    return json.loads(data)
    time.sleep(2)

# Print usage syntax
def help():
    # Print out instructions for usage
    print("\nusage: oldzoomers [-l days] [-b csvfile]\n")
    print("                  Syntax:\n")
    print("                  -l [n] or --list [n]")
    print("                  Creates a csv file of users that have not logged into the service for n days\n")
    print("                  -b [filename] or --basic [filename]")
    print("                  Change license type to basic of users in a given csv file\n")
    print("                  Enter your Zoom API key and secret to config.json\n")

# Write list of old users to csvfile
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
                        login_status = "Change to basic"
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


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hl:b:",["list=","basic="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-l", "--list"):
            last_login_days_setting = datetime.now() - timedelta(days=int(arg))
        elif opt in ("-b", "--basic"):
            csv_input_file=arg

    try:
        last_login_days_setting
    except NameError:
        print("variable last_login_days_setting not defined. moving on!")
    else:
        # Create variable with current date+time
        output_filename = '{}.csv'.format( datetime.now().strftime('%Y%m%d%H%M%S') )
        print('List of users will be written to: '+output_filename)
        api_get_pagecount()    
        write_csv_file(output_filename)
    try:
        csv_input_file
    except NameError:
        print("variable csv_input_file not defined. moving on!")
    else:
        with open(csv_input_file, newline='') as csvfile:
            reader = reader(csvfile)
            i=0
            for row in reader:
                if row[0] != "e-mail":
                    try:
                        if row[2] == "Check manually":
                            answer=None
                            while answer not in ("y", "Y", "n", "N"):
                                print(row[0]+" should be checked manually. ")
                                answer = input("Change to basic anyway? (y/n): ")
                                if answer == "y" or answer == "Y":
                                    api_change_license_type(row[0],1)
                                elif answer =="n" or answer == "N":
                                    continue
                                else:
                                    print("Please enter y/n")
                    except:
                        print('no status')
                    try:
                        if row[2] == "Change to basic":
                            answer=None
                            while answer not in ("y", "Y", "n", "N"):
                                print("User: "+row[0])
                                answer = input("Change to basic? (y/n): ")
                                if answer == "y" or answer == "Y":
                                    api_change_license_type(row[0],1)
                                elif answer =="n" or answer == "N":
                                    continue
                                else:
                                    print("Please enter y/n")
                    except:
                        print('no status')
                    i=i+1