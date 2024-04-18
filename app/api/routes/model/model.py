from fastapi import APIRouter, Depends, HTTPException
from app.services.model import ModelService
from app.core.config import get_app_settings
import httpx

router = APIRouter()

async def call_lambda_api(input_data, route_id, lambda_endpoint):
    with httpx.Client() as client:
        response = client.post(
            lambda_endpoint,
            json={"input_data": input_data, "route_id": route_id}
        )
        response.raise_for_status()
        return response.json()

@router.post("/model/predict")
async def predict(
    route_id: str,
    model_service: ModelService = Depends(ModelService),
    settings = Depends(get_app_settings)
):
    bus_window_data = model_service.get_bus_window_data(route_id=route_id)
    predictions = {}

    for plate_no, plate_no_values in bus_window_data.items():
        input_data = [value[:6] for value in plate_no_values]
        station_id = plate_no_values[-1][6]
        station_seq = plate_no_values[-1][0]
        prediction_values = await call_lambda_api(input_data, route_id, settings.LAMBDA_ENDPOINT)
        predictions[plate_no] = [{
            "predictions": prediction_values,
            "station_id": station_id,
            "station_seq": station_seq
        }]

    return {"predictions": predictions}