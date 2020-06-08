# oldzoomers
This code has two functions  

## Generate csv file
It can generate a csv file with zoom users on your account that have not logged in for n days  
The file will be namned date+time.csv  
Users that havn't logged in for n days will have "Change to basic" in the status column of the csv file  
Users that never have logged in will have "Check manually" in the status column of the csv file  

## Parse csv file  
It can parse a csv file with zoom users and let you change their license type to basic  
It will go through them one by one so you can review them and make a decision  

# install and configure  
Install Python3 *[https://www.python.org/downloads/](https://www.python.org/downloads/)*  
Install pyJWT
     pip3 install pyjwt  
On *[Zoom Marketplace](https://marketplace.zoom.us/docs/guides/build/jwt-app)* create a JWT App  
Edit config.json and paste API key and secret from your Zoom JWT App  

# usage
usage: oldzoomers [-l days] [-b csvfile]  

syntax:  

-l [n] or --list [n]  
Creates a csv file of users that have not logged into the service for n days  

-b [filename] or --basic [filename]  
Change license type to basic of users in a given csv file  

Enter your Zoom API key and secret to config.json  
