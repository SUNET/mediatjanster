# list player versions
Uses apptoken to list versions from the `html5Url` member of `KalturaUiConf` object and write them to `players.csv`    

## Info

Please note that players configured as auto-update will give you:  
`/html5/html5lib/{latest}/mwEmbedLoader.php`    
instead of the actual player version:  
e.g. `/html5/html5lib/v2.80/mwEmbedLoader.php`

Player version can also be seen in the browser dev-tools `console` tab on any page where a player is embedded.  

## install and configure  
[Install Python3](https://www.python.org/downloads/)   
Install KalturaApiClient library `pip3 install KalturaApiClient`  
[Create apptoken](https://developer.kaltura.com/api-docs/VPaaS-API-Getting-Started/application-tokens.html)  

## Usage
change session config in code 

    partner_id="your partner ID"  
    id="your apptokenid"  
    token="your apptoken"  

Run:  `python3 get_player_version.py` 