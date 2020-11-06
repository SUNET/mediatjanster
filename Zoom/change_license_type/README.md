# change_license_type
This code has two functions.
1. Generate csv file with zoom users not logged in for [n] days
2. Parse a csv file of users and change their license type (basic/licensed/on-prem)

## 1 generate csv file
Generate a csv file of users in your account that have not been logged in for [n] days
The file will be namned **date+time.csv**
Users that have not logged in for n days will have *"Change license type"* in the status column of the csv file
Users that never have logged in will have *"Check manually"* in the status column of the csv file

## 2 parse csv file
Parse a csv file with users and let you change their license type to basic/licensed/on-prem
You will get to review them one by one and make a decision

# install and configure
Install Python3 *[https://www.python.org/downloads/](https://www.python.org/downloads/)*
Install pyJWT `pip3 install pyjwt`
On *[Zoom Marketplace](https://marketplace.zoom.us/docs/guides/build/jwt-app)* create a JWT App
Edit config.json and paste API key and secret from your Zoom JWT App

# usage
usage: change_license_type [-e days] [-f filename] [-b] [-l] [-o] [-h]

-h or --help
Show syntax

-e [n] or --export [n]
Export a csv file of users in your account that have not been logged in for n days

-f [filename] or --file [filename]
Give csv file of users to parse as input

-b or --basic
Change license type to basic

-l or --licensed
Change license type to licensed

-o or --onprem
Change license type to on-prem

-a or --assume-yes")
Assume yes, necessary for running headless\n")

-j [filename] or --json-file [filename]")
Add optional filepath for config.json\n")

-c [filename] or --csv-file [filename]")
exported filename of csv-file\n")
