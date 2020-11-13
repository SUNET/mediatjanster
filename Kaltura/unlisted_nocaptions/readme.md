# unlisted media without captions
Create csvfile of media:  
1. publihsed after 2020-09-23  
2. containing specific category tag  
3. lacking captions  

## info

This code will list media with a specified category tag published after 2020-09-23.  
It will then check if every the entry has captions.  
Entries that lack captions will be written to a csvfile.  
Before exiting a semicolon separated list of user emails will be written to `Stdout`.  

## install and configure  
[Install Python3](https://www.python.org/downloads/)   
Install KalturaApiClient library `pip3 install KalturaApiClient`  
[Create apptoken](https://developer.kaltura.com/api-docs/VPaaS-API-Getting-Started/application-tokens.html)  

modify `config.json`

    partner_id="your partner ID"  
    id="your apptokenid"  
    token="your apptoken"
    unlisted_id="categoryId of your unlisted category"  

To change the start search date from 2020-09-23:  
modify the line: `wd_date = datetime(2020,9,23,0,0)`  

## usage

Run:  `python3 unlisted_nocaptions.py` 