import math
import os
import wget
import folium
from folium.plugins import MarkerCluster
from folium.plugins import MousePosition
from folium.features import DivIcon
import pandas as pd

def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def get_csv():
    """
    Retrieves our requisite CSV and returns it as a Pandas DataFrame.  
    """

    if os.path.isfile('data/spacex_launch_geo.csv'):
        spacex_csv_file = 'data/spacex_launch_geo.csv'
    else:
        spacex_csv_file = wget.download('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv', 'data/spacex_launch_geo.csv')
    
    df = pd.read_csv(spacex_csv_file)

    # Select relevant sub-columns: `Launch Site`, `Lat(Latitude)`, `Long(Longitude)`, `class`
    df = df[['Launch Site', 'Lat', 'Long', 'class']]
    launch_sites_df = df.groupby(['Launch Site'], as_index=False).first()
    launch_sites_df = launch_sites_df[['Launch Site', 'Lat', 'Long']]
    
    return launch_sites_df, df

def add_circle_label(site_map : folium.Map, coord : list, label : str, color : str = '#d35400') -> None:
    circle = folium.Circle(coord, radius=1000, color=color, fill=True).add_child(folium.Popup(label))

    marker = folium.map.Marker(
        coord,
        icon=DivIcon(
            icon_size = (20,20),
            icon_anchor = (0,0),
            html = f'<div style="font-size: 12; color:#d35400;"><b>{label}</b></div>',
            )
        )
    site_map.add_child(circle)
    site_map.add_child(marker)

def assign_marker_color(launch_outcome):
    if launch_outcome == 1:
        return 'green'
    else:
        return 'red'

if __name__ == '__main__':
    launch_sites_df, spacex_df = get_csv()

    print(launch_sites_df)

    # Task 1: Mark Launch Sites
    label_coords = launch_sites_df.set_index('Launch Site')[['Lat', 'Long']].apply(list, axis=1).to_dict()
    label_coords['NASA JSC'] = [29.559684888503615, -95.0830971930759]

    start_coord = label_coords['NASA JSC']
    site_map = folium.Map(location = start_coord, zoom_start = 5)

    for k, v in label_coords.items():
        add_circle_label(site_map, v, k)

    # Task 2: Mark Failures
    marker_cluster = MarkerCluster().add_to(site_map)
    spacex_df['marker_color'] = spacex_df['class'].apply(assign_marker_color)

    for index, record in spacex_df.iterrows():
        marker = folium.Marker(
            location=[record['Lat'], record['Long']],
            icon=folium.Icon(color='white', icon_color = record['marker_color']),
            popup=f"Launch Site: {record['Launch Site']}<br>Outcome: {record['class']}"
        )

        marker_cluster.add_child(marker)

    # Task 3: Distances Between a Launch Site to its Proximities
    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse_position = MousePosition(
        position='topright',
        separator=' Long: ',
        empty_string='NaN',
        lng_first=False,
        num_digits=20,
        prefix='Lat:',
        lat_formatter=formatter,
        lng_formatter=formatter,
    )

    site_map.add_child(mouse_position)

    site_map.show_in_browser()
