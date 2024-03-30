import json
import os

import requests
import xml.etree.ElementTree as ET
import xmljson as xmljson

from fastapi import HTTPException
from collections import OrderedDict

from app.models.domain.bus_arrival import (
    BusArrivalDto,
    BusLocationDto,
    BusArrivalResponseDto,
    BusLocationResponseDto,
)


class BusArrivalRepository:
    def __init__(self):
        route_map_path = os.path.join(os.path.dirname(__file__), "route.json")
        station_map_path = os.path.join(os.path.dirname(__file__), "station.json")
        bus_stop_path = os.path.join(os.path.dirname(__file__), "bus_stop.json")
        with open(route_map_path, "r") as f:
            self.route_map = json.load(f)
        with open(station_map_path, "r") as f:
            self.station_map = json.load(f)
        with open(bus_stop_path, "r") as f:
            self.bus_stop_map = json.load(f)

    def get_bus_arrival_list(
        self, service_key, station_id, route_id=None, sta_order=None
    ) -> BusArrivalResponseDto:
        url = "http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalList"
        params = {
            "serviceKey": service_key,
            "stationId": station_id,
        }
        if route_id:
            params["routeId"] = route_id
        if sta_order:
            params["staOrder"] = sta_order

        response = requests.get(url, params=params)

        xml_str = response.text

        # Convert the response from xml to json
        xml_element = ET.fromstring(xml_str)
        json_data = xmljson.parker.data(xml_element)
        print(json_data)
        if json_data["msgHeader"]["resultCode"] == 4:
            return []

        print(self.bus_stop_map.get("227000016", {}).get("227000205"))

        print(self.bus_stop_map.get("208000027").get(station_id))
        result = []
        if isinstance(json_data["msgBody"]["busArrivalList"], list):
            # 데이터가 리스트인 경우
            for data in json_data["msgBody"]["busArrivalList"]:
                if data is None:
                    continue

                bus_id = str(data["routeId"])
                bus_name = self.route_map.get(str(bus_id))
                if bus_name is None:
                    continue

                next_stop = self.bus_stop_map.get(bus_id).get(station_id)

                predictTime1 = data["predictTime1"]
                predictTime2 = data["predictTime2"]
                remainSeatCnt1 = data["remainSeatCnt1"]
                remainSeatCnt2 = data["remainSeatCnt2"]

                result.append(
                    {
                        "bus_id": bus_id,
                        "bus_name": bus_name,
                        "next_stop": next_stop,
                        "predictTime1": predictTime1,
                        "predictTime2": predictTime2,
                        "remainSeatCnt1": remainSeatCnt1,
                        "remainSeatCnt2": remainSeatCnt2,
                    }
                )

        elif isinstance(json_data["msgBody"]["busArrivalList"], OrderedDict):
            # 데이터가 OrderedDict인 경우
            data = json_data["msgBody"]["busArrivalList"]
            if data is None:
                return result

            bus_id = str(data["routeId"])
            bus_name = self.route_map.get(str(bus_id))
            if bus_name is None:
                return result

            next_stop = self.bus_stop_map.get(bus_id).get(station_id)

            predictTime1 = data["predictTime1"]
            predictTime2 = data["predictTime2"]
            remainSeatCnt1 = data["remainSeatCnt1"]
            remainSeatCnt2 = data["remainSeatCnt2"]

            result.append(
                {
                    "bus_id": bus_id,
                    "bus_name": bus_name,
                    "next_stop": next_stop,
                    "predictTime1": predictTime1,
                    "predictTime2": predictTime2,
                    "remainSeatCnt1": remainSeatCnt1,
                    "remainSeatCnt2": remainSeatCnt2,
                }
            )

        return result

    def get_bus_location(self, bus_id: str) -> BusLocationResponseDto:
        url = "http://openapi.gbis.go.kr/ws/rest/buslocationservice"
        params = {"serviceKey": "1234567890", "routeId": bus_id}

        response = requests.get(url, params=params)
        xml_str = response.text

        # Convert the response from xml to json
        xml_element = ET.fromstring(xml_str)
        json_data = xmljson.parker.data(xml_element)

        print(json_data)
        result = []
        for data in json_data["msgBody"]["busLocationList"]:
            if data is None:
                continue

            if isinstance(data, str):
                print("continue")
                continue

            end_bus = data["endBus"]
            plateType = data["plateType"]
            plateNo = data["plateNo"]
            remainSeatCnt = data["remainSeatCnt"]
            bus_id = data["routeId"]
            bus_name = self.route_map[str(bus_id)]
            station_id = data["stationId"]
            station_name = self.station_map[str(station_id)]
            stationSeq = data["stationSeq"]
            result.append(
                BusLocationDto(
                    end_bus=end_bus,
                    plateType=plateType,
                    plateNo=plateNo,
                    remainSeatCnt=remainSeatCnt,
                    bus_id=bus_id,
                    bus_name=bus_name,
                    station_id=station_id,
                    station_name=station_name,
                    stationSeq=stationSeq,
                )
            )
        return result
