
# change owner
Change owner of KalturaBaseEntry clipped from a live event less than 4 minutes ago.   

## install and configure  
[Install Python3](https://www.python.org/downloads/)   
Install KalturaApiClient library `pip3 install KalturaApiClient`  
[Create apptoken](https://developer.kaltura.com/api-docs/VPaaS-API-Getting-Started/application-tokens.html)  

code adds "@gu.se" to userid. change to reflect your own user database  

## usage
`python3 change_owner.py userid baseentryid entryid apptokenid apptoken`
