# oldzoomers
This code has two functions.
1. Generate csv file with old zoom users
2. Parse a csv file and change old zoom users to license type basic

## 1 generate csv file
Generates a csv file with zoom users on your account that have not logged in for n days  
The file will be namned **date+time.csv** 
Users that have not logged in for n days will have *"Change to basic"* in the status column of the csv file  
Users that never have logged in will have *"Check manually"* in the status column of the csv file  

## 2 parse csv file  
Parses a csv file with zoom users and let you change their license type to basic  
You will get to review them one by one and make a decision

# install and configure  
Install Python3 *[https://www.python.org/downloads/](https://www.python.org/downloads/)*  
Install pyJWT `pip3 install pyjwt`  
On *[Zoom Marketplace](https://marketplace.zoom.us/docs/guides/build/jwt-app)* create a JWT App  
Edit config.json and paste API key and secret from your Zoom JWT App  

# usage
usage: oldzoomers [-l days] [-b csvfile]  
    
syntax:  
-l [n] or --list [n]  
Creates a csv file of users that have not logged into the service for n days
    
-b [filename] or --basic [filename]  
Change license type to basic of users in a given csv file  
