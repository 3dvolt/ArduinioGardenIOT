import requests

#function for calling openweather bees to get weather related information
#in input the api keys for the call and the city of which you want to get the forecasts
def GetFutureTemperature(config,city):
    apiID = config['weather']
    url = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid="+apiID
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = response.json()
    return resp