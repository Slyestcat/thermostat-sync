project_id = '#'
client_id = '#'
client_secret = '#'
redirect_uri = 'https://slyestcat.com/'
refresh_token = '#'

url = 'https://nestservices.google.com/partnerconnections/'+project_id+'/auth?redirect_uri='+redirect_uri+'&access_type=offline&prompt=consent&client_id='+client_id+'&response_type=code&scope=https://www.googleapis.com/auth/sdm.service'

code = '$'

import requests
import time
from datetime import datetime

params = (
    ('client_id', client_id),
    ('client_secret', client_secret),
    ('refresh_token', refresh_token),
    ('grant_type', 'refresh_token'),
)

response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)

response_json = response.json()
access_token = response_json['token_type'] + ' ' + response_json['access_token']

url_structures = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + project_id + '/structures'

headers = {
    'Content-Type': 'application/json',
    'Authorization': access_token,
}

response = requests.get(url_structures, headers=headers)

# Get devices
url_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + project_id + '/devices'

headers = {
    'Content-Type': 'application/json',
    'Authorization': access_token,
}

response = requests.get(url_get_devices, headers=headers)

response_json = response.json()
device_0_name = response_json['devices'][0]['name'] #Downstairs
device_1_name = response_json['devices'][1]['name'] #Upstairs


def tokenRefresh():
    params = (
        ('client_id', client_id),
        ('client_secret', client_secret),
        ('refresh_token', refresh_token),
        ('grant_type', 'refresh_token'),
    )

    response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)

    response_json = response.json()
    access_token = response_json['token_type'] + ' ' + response_json['access_token']
    return access_token

def getTimestamp():
    now = datetime.now()
    timestampGross = datetime.timestamp(now)
    timestamp = datetime.fromtimestamp(timestampGross)
    return timestamp

# Get device stats
def getDownstairsTemp():
    access_token = tokenRefresh()
    url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    response = requests.get(url_get_device, headers=headers)
    response_json = response.json()
    coolingMode = response_json['traits']['sdm.devices.traits.ThermostatMode']['mode']
    if coolingMode == 'COOL':
        jsonDataDownstairs = response_json['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']
    elif coolingMode == 'HEAT':
        jsonDataDownstairs = response_json['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']
    else:
        return
    return jsonDataDownstairs

def getUpstairsTemp():
    access_token = tokenRefresh()
    url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device_1_name
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    response = requests.get(url_get_device, headers=headers)
    response_json = response.json()
    coolingMode = response_json['traits']['sdm.devices.traits.ThermostatMode']['mode']
    if coolingMode == 'COOL':
        jsonDataUpstairs = response_json['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']
    elif coolingMode == 'HEAT':
        jsonDataUpstairs = response_json['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']
    else:
        return
    return jsonDataUpstairs

def updateCoolTempature(deviceName, jsonData):
    access_token = tokenRefresh()
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + deviceName + ':executeCommand'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "COOL" } }'
    response = requests.post(url_set_mode, headers=headers, data=data)
    #print(response.json())
    data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool", "params" : ' + str(jsonData) + ' }'
    response = requests.post(url_set_mode, headers=headers, data=data)
    #print(response.json())
    return

def updateHeatTempature(deviceName, jsonData):
    access_token = tokenRefresh()
    url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + deviceName + ':executeCommand'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "HEAT" } }'
    response = requests.post(url_set_mode, headers=headers, data=data)
    #print(response.json())
    data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : ' + str(jsonData) + ' }'
    response = requests.post(url_set_mode, headers=headers, data=data)
    #print(response.json())
    return

def getCoolMode(deviceName):
    access_token = tokenRefresh()
    url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + deviceName
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }

    response = requests.get(url_get_device, headers=headers)

    response_json = response.json()
    mode = response_json['traits']['sdm.devices.traits.ThermostatMode']['mode']
    return mode



def syncTemp():
    initialDownstairsTemp = getDownstairsTemp()
    initialUpstairsTemp = getUpstairsTemp()
    #print("Initial set tempatures, Downstairs: " + initialDownstairsTemp + " Upstairs: " + initialUpstairsTemp)
    currentDownstairsTemp = getDownstairsTemp()
    currentUpstairsTemp = getUpstairsTemp()
    if currentUpstairsTemp == currentDownstairsTemp:
        timestamp = getTimestamp()
        print(timestamp, "Tempatures sync'd! Continuting to monitor")
        time.sleep(600.0)
        pass
    else:
        timestamp = getTimestamp()
        print(timestamp, "Tempatures not sync'd! Syncing to Downstairs to Upstairs by default")
        if getCoolMode(device_1_name) == 'COOL':
            updateCoolTempature(device_0_name, currentUpstairsTemp)
            initialDownstairsTemp = currentUpstairsTemp
            initialUpstairsTemp = currentUpstairsTemp
        else:
            updateHeatTempature(device_0_name, currentUpstairsTemp)
            initialDownstairsTemp = currentUpstairsTemp
            initialUpstairsTemp = currentUpstairsTemp
        time.sleep(600.0)
    while True:
        currentDownstairsTemp = getDownstairsTemp()
        currentUpstairsTemp = getUpstairsTemp()
        if currentUpstairsTemp == initialUpstairsTemp:
            if currentDownstairsTemp == initialDownstairsTemp:
                timestamp = getTimestamp()
                print(timestamp(), "Nothing has changed...")
                time.sleep(600.0)
                pass
            else:
                timestamp = getTimetamp()
                print(timestamp, "Downstairs Tempature Changed! Syncing Upstairs")
                if getCoolMode(device_0_name) == 'COOL':
                    updateCoolTempature(device_1_name, currentDownstairsTemp)
                    initialUpstairsTemp = currentDownstairsTemp
                    initialDownstairsTemp = currentDownstairsTemp
                else:
                    updateHeatTempature(device_1_name, currentDownstairsTemp)
                    initialUpstairsTemp = currentDownstairsTemp
                    initialDownstairsTemp = currentDownstairsTemp
                time.sleep(600.0)
        else:
            timestamp = getTimetamp()
            print(timestamp, "Upstairs Tempature Changed! Syncing Downstairs")
            if getCoolMode(device_1_name) == 'COOL':
                updateCoolTempature(device_0_name, currentUpstairsTemp)
                initialDownstairsTemp = currentUpstairsTemp
                initialUpstairsTemp = currentUpstairsTemp
            else:
                updateHeatTempature(device_0_name, currentUpstairsTemp)
                initialDownstairsTemp = currentUpstairsTemp
                initialUpstairsTemp = currentUpstairsTemp
            time.sleep(600.0)
    return

syncTemp()
