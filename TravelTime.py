# importing required libraries
import streamlit as st

import requests, json
import googlemaps
from bs4 import BeautifulSoup
import pandas as pd

# Import datetime class from datetime module
from datetime import datetime, date
import time

#Import dependencies required to read google sheet
import os
from Google import Create_Service

#Import dependencies required to interact with google sheet
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive

#BingAPI key
import bing_key as bk



#Format the coordinates data into dataframe
coordinates_file = pd.read_excel('Geocode_details.xlsx')


#convert to dataframe
coordinates = coordinates_file[["Place", "Coordinates"]].set_index('Place').to_dict()['Coordinates']
coord_list = {a:coordinates[a].replace(', ',',') for a in list(coordinates.keys())}



# Declare variable names for each location identified in the coordinates file
festac = coord_list['festac']
ikoyi = coord_list['ikoyi']
lekki = coord_list['lekki']
apapa = coord_list['apapa']
lagos_island = coord_list['lagos_island']
ikeja = coord_list['ikeja']
yaba = coord_list['yaba']
surulere = coord_list['surulere']
alaba = coord_list['alaba']
oshodi = coord_list['oshodi']
ketu_ojota = coord_list['ketu_ojota']
alagbado = coord_list['alagbado']
ikorodu = coord_list['ikorodu']
ojodu = coord_list['ojodu']
oworo = coord_list['oworo']
ajah = coord_list['ajah']
gbagada = coord_list['gbagada']
agege = coord_list['agege']
ojoo_iba = coord_list['ojoo_iba']
ikotun = coord_list['ikotun']
badagry = coord_list['badagry']
abule_egba = coord_list['abule_egba']
ipaja = coord_list['ipaja']
idiaraba = coord_list['idiaraba']
VI = coord_list['VI']



#BingMaps Key
bingmaps_api_key = bk.map_key

#Construct the URL as required by the API
url = f'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?\
origins={festac};{ikoyi};{lekki};{apapa};{lagos_island};{ikeja};{yaba};{surulere};{alaba};{oshodi};{ketu_ojota};{alagbado};\
{ikorodu};{ojodu};{oworo};{ajah};{gbagada};{agege};{ojoo_iba};{ikotun};{badagry};{abule_egba};{ipaja};{idiaraba};{VI}\
&destinations={festac};{ikoyi};{lekki};{apapa};{lagos_island};{ikeja};{yaba};{surulere};{alaba};{oshodi};{ketu_ojota};{alagbado};\
{ikorodu};{ojodu};{oworo};{ajah};{gbagada};{agege};{ojoo_iba};{ikotun};{badagry};{abule_egba};{ipaja};{idiaraba};{VI}\
&travelMode=driving&key={bingmaps_api_key}'


def load_traffic_data():

    #Send the request and Store data
    resp = requests.get(url)
    result = resp.content

    # Use the json module to load response into a dictionary.
    response_dict = json.loads(result)

    data = response_dict['resourceSets'][0]['resources'][0]['results']#[]


    ### 3.3) Store the Data into a Dataframe and Create a Timestamp Column
    #Convert data to dataframe and format
    df = pd.DataFrame(data)
    #df.drop(['totalWalkDuration'], axis=1)
    df = df[['destinationIndex', 'originIndex', 'travelDistance', 'travelDuration']]

    #Add date/time columns
    df['Time'] = datetime.now().strftime("%H:%M:%S")
    df['Date'] = date.today()


    #form dictionary to map destination and origin index in the API result
    location_mapping = coordinates_file['Place'].to_dict()

    #lookup the names with the index values in the API result
    df['origin'] = df['originIndex'].map(location_mapping)
    df['destination'] = df['destinationIndex'].map(location_mapping)

    #drop the destination and origin index columns
    df.drop(['originIndex','destinationIndex'], axis=1, inplace=True)

    #Rearrange columns
    df = df[['origin','destination','travelDistance','travelDuration','Date','Time',]]

    #Rename columns
    df.columns = ['origin','destination','travelDistance(km)','travelDuration(mins)','Date','Time',]


    #format column data types
    df[df['travelDistance(km)']>0]
    df['travelDuration(mins)'] = df['travelDuration(mins)'].astype('int')
    df['travelDistance(km)'] = df['travelDistance(km)'].astype('int')
    df['Date'] = df['Date'].astype('str')

    #drop rows with 'travelDistance' = 0
    df = df[df['travelDistance(km)']!=0]

    return df

if st.button('Load Traffic Data'):
    
    load_traffic_data()
    
    st.write(f'Have is your View of Lagos Traffic as at {datetime.now().strftime("%H:%M:%S")}')
else:
    st.write('Waiting for your command')

if st.button('Append Data to Database'):
    
    #Define the scopes
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

    #Create credentials
    credentials = Credentials.from_service_account_file('data/maps_project_secret_keys.json', scopes=scopes)

    #Initialize gspread with created credentials
    gc = gspread.authorize(credentials)

    #
    testsheet_key = '1jFiCMs6YdH-WPifPcuae3dxfJagDcxSjzCBzhCGbLiU'
    sheetid = '5865198'

    # Open a google sheet
    #gs = gc.open_by_key(sheets_file1['spreadsheetId'])
    gs = gc.open_by_key(testsheet_key)
    # Append

    df = load_traffic_data()

    df_values = [df.columns.values.tolist()] + df.values.tolist()

    gs.values_append('Page_1', {'valueInputOption': 'RAW'}, {'values': df_values})

    st.write('Traffic Data has been saved!')
else:
    st.write('Do you wish to save this data?')
