"""
Example script showing how to use a saved Random Forest model for predictions
"""

from Random_Forest_Regression import AirlineConsumptionPredictor
import pandas as pd

def main():
    # Load the model
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    if predictor is None:
        print("❌ Failed to load model. Make sure to run Random_Forest_Regression.py first to train and save the model.")
        return
    
    current_prediction = predictor.predict_consumption(
        origin='DOH',
        flight_type='medium-haul',
        service_type='Retail',
        passenger_count=272,
        product_name='Bread Roll Pack',
        unit_cost=0.35,
        has_issues=0
    )

    print(f"✅ Prediction successful! Estimated consumption: {current_prediction:.2f} units")

if __name__ == "__main__":
    main()