import requests

#function to save measurements on HTTP protocol in the cloud
#in input the api key and temperature and humidity detected.
# the data are then visible on this url -> https://thingspeak.com/channels/
def StoreNewTemperature(config,temp,humidity,weather):
    apiID = config['temperature']
    url = "https://api.thingspeak.com/update?api_key="+apiID+"&field1="+temp+"&field2="+humidity+"&field3="+weather
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return True