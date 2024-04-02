import time

import requests
import xmljson
import xml.etree.ElementTree as ET
import json
import datetime

from app.db.models.bus_data import BusData

from fastapi import FastAPI

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
app = FastAPI()

# Define the database connection and create the engine
db_url = "postgresql://myuser:mypassword@localhost/mydb"
engine = create_engine(db_url)

# Define the ORM Base object
Base = declarative_base()

# Create the table in the database
Base.metadata.create_all(engine)

# Create a session object
Session = sessionmaker(bind=engine)


def store_bus_data():
    with open("../datas/route.json", "r") as f:
        route_map = json.load(f)

    with open("../datas/station.json", "r") as f:
        station_map = json.load(f)

    with open("../datas/red_bus.json", "r") as f:
        red_bus_list = json.load(f)

    result = [
        ["현재 시간", "차량 번호", "차량 아이디", "차량 번호", "남은 좌석", "정류소 id", "정류소 이름", "정류소 순서"]
    ]
    base_url = "http://openapi.gbis.go.kr/ws/rest/buslocationservice?serviceKey=1234567890&routeId={}"
    for route_id, route_name in route_map.items():
        if route_name not in red_bus_list:
            continue

        url = base_url.format(route_id)
        response = requests.get(url)
        xml_str = response.text

        # Convert the response from xml to json
        xml_element = ET.fromstring(xml_str)
        json_data = xmljson.parker.data(xml_element)

        # Handle a situation in which the request is ignored
        if len(json_data) == 1:
            continue

        # resultCode is not 0
        if json_data["msgHeader"]["resultCode"] != 0:
            continue
        for data in json_data["msgBody"]["busLocationList"]:
            try:
                if "remainSeatCnt" in data:
                    if data == "remainSeatCnt":
                        continue
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    plate_no = data["plateNo"]
                    plate_type = data["plateType"]
                    remain_seat_cnt = data["remainSeatCnt"]
                    if remain_seat_cnt == -1 or remain_seat_cnt == "-1":
                        continue
                    station_id = data["stationId"]
                    station_name = station_map[str(station_id)]
                    station_seq = data["stationSeq"]

                    bus_data = BusData(
                        date_time=now,
                        plate_no=plate_no,
                        plate_type=plate_type,
                        route_id=route_id,
                        route_name=route_name,
                        remaining_seats=remain_seat_cnt,
                        station_id=station_id,
                        station_name=station_name,
                        station_order=station_seq,
                    )

                    print(
                        [
                            now,
                            plate_no,
                            plate_type,
                            route_id,
                            route_name,
                            remain_seat_cnt,
                            station_id,
                            station_name,
                            station_seq,
                        ]
                    )

                    session = Session()
                    session.add(bus_data)
                    session.commit()
                    session.close()
                    print(
                        [
                            now,
                            plate_no,
                            plate_type,
                            route_id,
                            route_name,
                            remain_seat_cnt,
                            station_id,
                            station_name,
                            station_seq,
                        ]
                    )
            except:
                print("crawling error cause")


while True:
    store_bus_data()
    time.sleep(30)
