from fastapi import APIRouter, Depends, HTTPException
from app.services.model import ModelService
from app.core.config import get_app_settings
import httpx

router = APIRouter()

async def call_lambda_api(pre_values, route_id, lambda_endpoint):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            lambda_endpoint, 
            json={"pre_values": pre_values, "route_id": route_id})
        response.raise_for_status()
        return response.json()

@router.post("/predict")
async def predict(
    route_id: str,
    model_service: ModelService = Depends(ModelService),
    settings = Depends(get_app_settings)
):
    result = model_service.get_bus_window_data(route_id=route_id)
    
    station_datas = model_service.get_station_data(route_id=route_id)
    station_sequences = [[] for _ in range(station_datas["length"])]
    for plate_no, values in result.items():
        pre_values = [value[:6] for value in values]

        print(plate_no, values)
        station_id = values[-1][6]
        station_seq = values[-1][0]
        prediction_values = await call_lambda_api(pre_values, route_id, settings.LAMBDA_ENDPOINT)

        for i, v in enumerate(prediction_values):
            if station_seq+i >= station_datas["length"]:
                break
            station_sequences[station_seq+i].insert(0, v)    
            
    for i, station_sequence in enumerate(station_sequences):
        if not station_sequence: 
            station_sequences[i] = [None]

    return station_sequences

@router.post("/predict_ver2")
async def predict(
    route_id: str,
    model_service: ModelService = Depends(ModelService),
    settings = Depends(get_app_settings)
):
    result = model_service.get_bus_window_data(route_id=route_id)
    
    predictions = {}
    for plate_no, values in result.items():
        pre_values = [value[:6] for value in values]

        print(plate_no, values)
        station_id = values[-1][6]
        station_seq = values[-1][0]
        
        prediction_values = await call_lambda_api(pre_values, route_id, settings.LAMBDA_ENDPOINT)
        
        predictions[plate_no] = [{
            "predictions": prediction_values,
            "station_id": station_id,
            "station_seq": station_seq
        }]
        
    return {"predictions": predictions}