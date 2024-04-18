import json
import xml.etree.ElementTree as ET
import requests
import xmljson as xmljson
import os

from bus_station_map import add_bus_stops, add_buses, add_stations

project_home = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
route_file_path = os.path.join(project_home, 'datas', 'route.json')
red_bus_file_path = os.path.join(project_home, 'datas', 'red_bus.json')

def save_bus_stops():
    # Load the route_map from file
    with open(route_file_path, "r") as f:
        route_map = json.load(f)

    with open(red_bus_file_path, "r") as f:
        red_bus_map = json.load(f)

    red_buses = []
    stations = []

    print(red_bus_map)

    for route_id, route_name in route_map.items():
        if route_name in red_bus_map:
            red_buses.append([route_id, route_name, 1])

    base_url = "http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=1234567890&routeId={}"
    result = []
    for red_bus in red_buses:
        route_id = red_bus[0]
        route_name = red_bus[1]
        url = base_url.format(route_id)
        response = requests.get(url)
        xml_str = response.text

        # Convert the response from xml to json
        xml_element = ET.fromstring(xml_str)
        json_data = xmljson.parker.data(xml_element)

        order = 1

        if json_data.get("msgBody") is None:
            continue

        isPass = False
        for data in json_data["msgBody"]["busRouteStationList"]:
            isPass = True
            result.append(
                [route_id, route_name, data["stationId"], data["stationName"], order]
            )
            stations.append([data["stationId"], data["stationName"]])
            order += 1

        if not isPass:
            print(route_name, " don't contain")
        else:
            print(route_name, " pass")
    # Bulk add bus data to db
    add_bus_stops(result)
    add_buses(red_buses)
    add_stations(stations)


save_bus_stops()
