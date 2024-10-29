"""
Functions related to obtaining data from wikipedia about SpaceX launches.
"""

import re
import requests
import sys
import unicodedata

from bs4 import BeautifulSoup
import pandas as pd

# Utility functions
def populate_launch_dict(launch_dict, soup):
    extracted_row = 0

    # Function that processes each table in the soup
    for table_number, table in enumerate(soup.find_all('table', "wikitable plainrowheaders collapsible")):
        # Get table rows
        for rows in table.find_all("tr"):
            # Check to see if first table heading is a number corresponding to a launch number
            if rows.th:
                if rows.th.string:
                    flight_number = rows.th.string.strip()
                    flag = flight_number.isdigit()
            else:
                flag = False
            
            # Get table elements
            row = rows.find_all('td')

            # If it's a number, save cells in a dictionary
            if flag:
                extracted_row += 1

                # Append the flight_number into launch_dict with key `Flight No.`
                launch_dict['Flight No.'].append(flight_number)

                # Date and Time values
                datatimelist = date_time(row[0])
                
                # Append the date into launch_dict with key `Date`
                date = datatimelist[0].strip(',')
                launch_dict['Date'].append(date)
                
                # Append the time into launch_dict with key `Time`
                time = datatimelist[1]
                launch_dict['Time'].append(time)

                # Booster version
                bv = booster_version(row[1])
                if not bv:
                    bv = row[1].a.string
                launch_dict['Version Booster'].append(bv)

                # Append the launch site into launch_dict with key `Launch site`
                launch_site = row[2].a.string
                launch_dict['Launch site'].append(launch_site)

                # Append the payload into launch_dict with key `Payload`
                payload = row[3].a.string
                launch_dict['Payload'].append(payload)

                # Append the payload_mass into launch_dict with key `Payload mass`
                payload_mass = get_mass(row[4])
                launch_dict['Payload mass'].append(payload_mass)

                # Append the orbit into launch_dict with key `Orbit`
                orbit = row[5].a.string
                launch_dict['Orbit'].append(orbit)

                # Append the customer into launch_dict with key `Customer`
                # Note: we check for existance because some of the values are null.  We handle this by inserting a None value
                if row[6].a:
                    customer = row[6].a.string
                    launch_dict['Customer'].append(customer)
                else:
                    launch_dict['Customer'].append(None)

                # Append the launch outcome into launch_dict with key `Launch outcome`
                launch_outcome = list(row[7].strings)[0]
                launch_dict['Launch outcome'].append(launch_outcome)

                # Append the booster_landing into launch_dict with key `Booster landing`
                booster_landing = landing_status(row[8])
                launch_dict['Booster landing'].append(booster_landing)

    return launch_dict

def init_launch_dict():
    launch_dict = {}
    launch_dict['Flight No.'] = []
    launch_dict['Launch site'] = []
    launch_dict['Payload'] = []
    launch_dict['Payload mass'] = []
    launch_dict['Orbit'] = []
    launch_dict['Customer'] = []
    launch_dict['Launch outcome'] = []
    launch_dict['Version Booster']= []
    launch_dict['Booster landing']= []
    launch_dict['Date']= []
    launch_dict['Time']= []

    return launch_dict

def get_tables(soup):
    html_tables = soup.find_all('table')
    
    return html_tables

def get_soup_object(url):
    """
    Takes a URL and returns a beautiful soup object of it.
    Input: String of URL.
    """
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        return soup
    else:
        raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

def date_time(table_cells):
    """
    This function returns the data and time from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out

def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass

def extract_column_from_header(row):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    if (row.br):
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
        
    colunm_name = ' '.join(row.contents)
    
    # Filter the digit and empty names
    if not(colunm_name.strip().isdigit()):
        colunm_name = colunm_name.strip()
        return colunm_name
    
    

if __name__ == '__main__':
    # Using a snapshot URL for consistency in testing.
    static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

    soup = get_soup_object(static_url)
    html_tables = get_tables(soup)
    first_table = html_tables[2].find_all('th')
    column_names = [extract_column_from_header(th) for th in first_table]
    launch_dict = init_launch_dict()
    launch_dict = populate_launch_dict(launch_dict, soup)
    df = pd.DataFrame(launch_dict)
    df.to_csv(f'data/spacex_web_scraped.csv', index=False)
