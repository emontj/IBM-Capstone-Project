import datetime
import requests

import numpy as np
import pandas as pd

# Global variables 
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

# These functions are provided by IBM
# Takes the dataset and uses the rocket column to call the API and append the data to the list
def getBoosterVersion(data):
    for x in data['rocket']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/rockets/" + str(x)).json()
            BoosterVersion.append(response['name'])

# Takes the dataset and uses the launchpad column to call the API and append the data to the list
def getLaunchSite(data):
    for x in data['launchpad']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/launchpads/" + str(x)).json()
            Longitude.append(response['longitude'])
            Latitude.append(response['latitude'])
            LaunchSite.append(response['name'])

# Takes the dataset and uses the payloads column to call the API and append the data to the lists
def getPayloadData(data):
    for load in data['payloads']:
        if load:
            response = requests.get("https://api.spacexdata.com/v4/payloads/" + load).json()
            PayloadMass.append(response['mass_kg'])
            Orbit.append(response['orbit'])

# Takes the dataset and uses the cores column to call the API and append the data to the lists
def getCoreData(data):
    for core in data['cores']:
        if core['core'] != None:
            response = requests.get("https://api.spacexdata.com/v4/cores/" + core['core']).json()
            Block.append(response['block'])
            ReusedCount.append(response['reuse_count'])
            Serial.append(response['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)
        
        Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    # Test 1
    spacex_url = "https://api.spacexdata.com/v4/launches/past"
    response = requests.get(spacex_url)

    assert response.status_code == 200

    # Test 2
    static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'
    response = requests.get(static_json_url)

    assert response.status_code == 200

    data = pd.json_normalize(response.json())

    # Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
    data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

    # We will remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket.
    data = data[data['cores'].map(len)==1]
    data = data[data['payloads'].map(len)==1]

    # Since payloads and cores are lists of size 1 we will also extract the single value in the list and replace the feature.
    data['cores'] = data['cores'].map(lambda x : x[0])
    data['payloads'] = data['payloads'].map(lambda x : x[0])

    # We also want to convert the date_utc to a datetime datatype and then extracting the date leaving the time
    data['date'] = pd.to_datetime(data['date_utc']).dt.date

    # Using the date we will restrict the dates of the launches
    data = data[data['date'] <= datetime.date(2020, 11, 13)]

    getBoosterVersion(data)
    getLaunchSite(data)
    getPayloadData(data)
    getCoreData(data)

    launch_dict = {
        'FlightNumber': list(data['flight_number']),
        'Date': list(data['date']),
        'BoosterVersion': BoosterVersion,
        'PayloadMass': PayloadMass,
        'Orbit': Orbit,
        'LaunchSite': LaunchSite,
        'Outcome': Outcome,
        'Flights': Flights,
        'GridFins': GridFins,
        'Reused': Reused,
        'Legs': Legs,
        'LandingPad': LandingPad,
        'Block': Block,
        'ReusedCount': ReusedCount,
        'Serial': Serial,
        'Longitude': Longitude,
        'Latitude': Latitude
    }

    df = pd.DataFrame(launch_dict)

    # Quiz Question 1 - After you performed a GET request on the Space X API and convert the response  to a dataframe using pd.json_normalize. What year is located in the first row in the column static_fire_date_utc?
    print(df['Date'])

    # Quiz Question 2 - Using the API, how many Falcon 9 launches are there after we remove Falcon 1 launches?
    print(df['BoosterVersion'].value_counts())

    # Quiz Question 3 - At the end of the API data collection process, how many missing values are there for the column landingPad?
    print(df['LandingPad'].isnull().sum())

    df.to_csv(f'data/spacex_api.csv', index=False)