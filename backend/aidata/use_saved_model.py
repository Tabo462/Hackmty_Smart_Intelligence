"""
Example script showing how to use a saved Random Forest model for predictions
"""

from Random_Forest_Regression import AirlineConsumptionPredictor
import pandas as pd

def make_predictions_with_saved_model():
    """
    Demonstrate how to load and use a saved model
    """
    print("="*60)
    print("USING SAVED AIRLINE CONSUMPTION PREDICTION MODEL")
    print("="*60)
    
    # Method 1: Load model into existing instance
    print("\n1. Loading saved model...")
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    
    if predictor is None:
        print("❌ Failed to load model. Make sure to run Random_Forest_Regression.py first to train and save the model.")
        return
    
    print("\n2. Making predictions for different scenarios...")
    
    # Example predictions for different flight scenarios
    scenarios = [
        {
            'name': 'DOH Medium-haul Retail - Water',
            'origin': 'DOH',
            'flight_type': 'medium-haul',
            'service_type': 'Retail',
            'passenger_count': 250,
            'product_name': 'Still Water 500ml',
            'unit_cost': 0.5
        },
        {
            'name': 'JFK Long-haul Pick&Pack - Snacks',
            'origin': 'JFK',
            'flight_type': 'long-haul',
            'service_type': 'Pick & Pack',
            'passenger_count': 320,
            'product_name': 'Mixed Nuts 30g',
            'unit_cost': 0.65
        },
        {
            'name': 'LHR Short-haul Retail - Coffee',
            'origin': 'LHR',
            'flight_type': 'short-haul',
            'service_type': 'Retail',
            'passenger_count': 150,
            'product_name': 'Instant Coffee Stick',
            'unit_cost': 0.08
        },
        {
            'name': 'NRT Long-haul Pick&Pack - Juice',
            'origin': 'NRT',
            'flight_type': 'long-haul',
            'service_type': 'Pick & Pack',
            'passenger_count': 300,
            'product_name': 'Juice 200ml',
            'unit_cost': 0.55
        }
    ]
    
    # Make predictions and create results table
    results = []
    for scenario in scenarios:
        prediction = predictor.predict_consumption(
            origin=scenario['origin'],
            flight_type=scenario['flight_type'],
            service_type=scenario['service_type'],
            passenger_count=scenario['passenger_count'],
            product_name=scenario['product_name'],
            unit_cost=scenario['unit_cost']
        )
        
        results.append({
            'Scenario': scenario['name'],
            'Origin': scenario['origin'],
            'Flight_Type': scenario['flight_type'],
            'Service_Type': scenario['service_type'],
            'Passengers': scenario['passenger_count'],
            'Product': scenario['product_name'],
            'Unit_Cost': f"${scenario['unit_cost']:.2f}",
            'Predicted_Consumption': f"{prediction} units"
        })
        
        print(f"\n📊 {scenario['name']}:")
        print(f"   Flight: {scenario['origin']} {scenario['flight_type']} ({scenario['service_type']})")
        print(f"   Passengers: {scenario['passenger_count']}")
        print(f"   Product: {scenario['product_name']} (${scenario['unit_cost']:.2f})")
        print(f"   🎯 Predicted consumption: {prediction} units")
    
    # Create summary DataFrame
    print("\n" + "="*60)
    print("PREDICTION SUMMARY TABLE")
    print("="*60)
    
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))
    
    # Calculate consumption per passenger for insights
    print("\n📈 INSIGHTS:")
    for i, result in enumerate(results):
        consumption = int(result['Predicted_Consumption'].split()[0])
        passengers = result['Passengers']
        per_passenger = consumption / passengers
        print(f"• {result['Scenario']}: {per_passenger:.2f} units per passenger")

def batch_predictions_from_csv():
    """
    Example of how to make batch predictions from a CSV file
    """
    print("\n" + "="*60)
    print("BATCH PREDICTIONS FROM CSV")
    print("="*60)
    
    # Load the saved model
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    
    if predictor is None:
        print("❌ Failed to load model.")
        return
    
    # Create example new data (in real scenario, this would be from a CSV file)
    new_data = pd.DataFrame([
        {'origin': 'DOH', 'flight_type': 'medium-haul', 'service_type': 'Retail', 
         'passenger_count': 280, 'product_name': 'Sparkling Water 330ml', 'unit_cost': 0.45},
        {'origin': 'JFK', 'flight_type': 'long-haul', 'service_type': 'Pick & Pack', 
         'passenger_count': 350, 'product_name': 'Bread Roll Pack', 'unit_cost': 0.35},
        {'origin': 'ZRH', 'flight_type': 'short-haul', 'service_type': 'Retail', 
         'passenger_count': 140, 'product_name': 'Chocolate Bar 50g', 'unit_cost': 0.8}
    ])
    
    print("Input data for predictions:")
    print(new_data.to_string(index=False))
    
    # Make predictions for each row
    predictions = []
    for _, row in new_data.iterrows():
        pred = predictor.predict_consumption(
            origin=row['origin'],
            flight_type=row['flight_type'],
            service_type=row['service_type'],
            passenger_count=row['passenger_count'],
            product_name=row['product_name'],
            unit_cost=row['unit_cost']
        )
        predictions.append(pred)
    
    # Add predictions to the DataFrame
    new_data['predicted_consumption'] = predictions
    
    print(f"\nResults with predictions:")
    print(new_data.to_string(index=False))

def inventory_planning_example():
    """
    Example of using the model for inventory planning
    """
    print("\n" + "="*60)
    print("INVENTORY PLANNING EXAMPLE")
    print("="*60)
    
    # Load the saved model
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    
    if predictor is None:
        print("❌ Failed to load model.")
        return
    
    # Upcoming flight details
    flight_info = {
        'origin': 'JFK',
        'flight_type': 'long-haul',
        'service_type': 'Pick & Pack',
        'passenger_count': 320
    }
    
    # Products to stock
    products = [
        {'name': 'Still Water 500ml', 'cost': 0.5},
        {'name': 'Sparkling Water 330ml', 'cost': 0.45},
        {'name': 'Juice 200ml', 'cost': 0.55},
        {'name': 'Bread Roll Pack', 'cost': 0.35},
        {'name': 'Chocolate Bar 50g', 'cost': 0.8},
        {'name': 'Mixed Nuts 30g', 'cost': 0.65},
        {'name': 'Instant Coffee Stick', 'cost': 0.08}
    ]
    
    print(f"Flight: {flight_info['origin']} {flight_info['flight_type']} ({flight_info['service_type']})")
    print(f"Passengers: {flight_info['passenger_count']}")
    print("\n📦 RECOMMENDED INVENTORY:")
    print("-" * 50)
    
    total_cost = 0
    for product in products:
        predicted_demand = predictor.predict_consumption(
            origin=flight_info['origin'],
            flight_type=flight_info['flight_type'],
            service_type=flight_info['service_type'],
            passenger_count=flight_info['passenger_count'],
            product_name=product['name'],
            unit_cost=product['cost']
        )
        
        # Add no buffer for no safety stock
        recommended_stock = int(predicted_demand * 1.0)
        cost = recommended_stock * product['cost']
        total_cost += cost
        
        print(f"{product['name']:<25} | Stock: {recommended_stock:>3} units | Cost: ${cost:>6.2f}")
    
    print("-" * 50)
    print(f"{'TOTAL INVENTORY COST':<25} | {'':>11} | ${total_cost:>6.2f}")

def flight_demand_analysis():
    """
    Show predicted demand per flight and calculate totals
    """
    print("\n" + "="*60)
    print("FLIGHT DEMAND ANALYSIS - PER FLIGHT TOTALS")
    print("="*60)
    
    # Load the saved model
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    
    if predictor is None:
        print("❌ Failed to load model.")
        return
    
    # Define multiple flights to analyze
    flights = [
        {
            'flight_id': 'AM109',
            'origin': 'DOH',
            'flight_type': 'medium-haul',
            'service_type': 'Pick & Pack',
            'passenger_count': 272
        },
        {
            'flight_id': 'LX205',
            'origin': 'ZRH',
            'flight_type': 'short-haul',
            'service_type': 'Retail',
            'passenger_count': 150
        },
        {
            'flight_id': 'QR890',
            'origin': 'DOH',
            'flight_type': 'medium-haul',
            'service_type': 'Retail',
            'passenger_count': 280
        },
        {
            'flight_id': 'NH456',
            'origin': 'NRT',
            'flight_type': 'long-haul',
            'service_type': 'Pick & Pack',
            'passenger_count': 300
        }
    ]
    
    # All available products
    products = [
        {'name': 'Still Water 500ml', 'cost': 0.5},
        {'name': 'Sparkling Water 330ml', 'cost': 0.45},
        {'name': 'Juice 200ml', 'cost': 0.55},
        {'name': 'Bread Roll Pack', 'cost': 0.35},
        {'name': 'Chocolate Bar 50g', 'cost': 0.8},
        {'name': 'Butter Cookies 75g', 'cost': 0.75},
        {'name': 'Mixed Nuts 30g', 'cost': 0.65},
        {'name': 'Instant Coffee Stick', 'cost': 0.08},
        {'name': 'Herbal Tea Bag', 'cost': 0.06},
        {'name': 'Snack Box Economy', 'cost': 2.1}
    ]
    
    flight_results = []
    grand_total_units = 0
    grand_total_cost = 0
    
    # Analyze each flight
    for flight in flights:
        print(f"\n🛫 FLIGHT {flight['flight_id']}")
        print(f"   Route: {flight['origin']} {flight['flight_type']} ({flight['service_type']})")
        print(f"   Passengers: {flight['passenger_count']}")
        print("   " + "-" * 55)
        
        flight_total_units = 0
        flight_total_cost = 0
        flight_products = []
        
        # Predict demand for each product on this flight
        for product in products:
            predicted_demand = predictor.predict_consumption(
                origin=flight['origin'],
                flight_type=flight['flight_type'],
                service_type=flight['service_type'],
                passenger_count=flight['passenger_count'],
                product_name=product['name'],
                unit_cost=product['cost']
            )
            
            cost = predicted_demand * product['cost']
            flight_total_units += predicted_demand
            flight_total_cost += cost
            
            flight_products.append({
                'product': product['name'],
                'demand': predicted_demand,
                'unit_cost': product['cost'],
                'total_cost': cost
            })
            
            print(f"   {product['name']:<23} | {predicted_demand:>3} units | ${cost:>6.2f}")
        
        print("   " + "-" * 55)
        print(f"   {'FLIGHT TOTAL':<23} | {flight_total_units:>3} units | ${flight_total_cost:>6.2f}")
        
        # Add to grand totals
        grand_total_units += flight_total_units
        grand_total_cost += flight_total_cost
        
        # Store flight results
        flight_results.append({
            'flight_id': flight['flight_id'],
            'origin': flight['origin'],
            'flight_type': flight['flight_type'],
            'service_type': flight['service_type'],
            'passengers': flight['passenger_count'],
            'total_units': flight_total_units,
            'total_cost': flight_total_cost,
            'units_per_passenger': flight_total_units / flight['passenger_count'],
            'cost_per_passenger': flight_total_cost / flight['passenger_count'],
            'products': flight_products
        })
    
    # Summary table
    print("\n" + "="*80)
    print("FLIGHT SUMMARY TABLE")
    print("="*80)
    
    print(f"{'Flight':<8} {'Origin':<6} {'Type':<11} {'Service':<11} {'Pax':<4} {'Units':<6} {'Cost':<8} {'U/Pax':<5} {'$/Pax':<6}")
    print("-" * 80)
    
    for result in flight_results:
        print(f"{result['flight_id']:<8} {result['origin']:<6} {result['flight_type']:<11} "
              f"{result['service_type']:<11} {result['passengers']:<4} {result['total_units']:<6} "
              f"${result['total_cost']:<7.2f} {result['units_per_passenger']:<5.2f} ${result['cost_per_passenger']:<5.2f}")
    
    print("-" * 80)
    print(f"{'TOTALS':<8} {'':>28} {sum(r['passengers'] for r in flight_results):<4} "
          f"{grand_total_units:<6} ${grand_total_cost:<7.2f}")
    
    # Analysis insights
    print("\n📊 ANALYSIS INSIGHTS:")
    print(f"• Total passengers across all flights: {sum(r['passengers'] for r in flight_results):,}")
    print(f"• Total predicted consumption: {grand_total_units:,} units")
    print(f"• Total inventory cost: ${grand_total_cost:,.2f}")
    print(f"• Average units per passenger: {grand_total_units / sum(r['passengers'] for r in flight_results):.2f}")
    print(f"• Average cost per passenger: ${grand_total_cost / sum(r['passengers'] for r in flight_results):.2f}")
    
    # Top products across all flights
    print("\n🏆 TOP PRODUCTS ACROSS ALL FLIGHTS:")
    product_totals = {}
    for result in flight_results:
        for product in result['products']:
            if product['product'] not in product_totals:
                product_totals[product['product']] = {'units': 0, 'cost': 0}
            product_totals[product['product']]['units'] += product['demand']
            product_totals[product['product']]['cost'] += product['total_cost']
    
    # Sort by total units
    sorted_products = sorted(product_totals.items(), key=lambda x: x[1]['units'], reverse=True)
    
    print(f"{'Rank':<4} {'Product':<25} {'Total Units':<12} {'Total Cost'}")
    print("-" * 55)
    for i, (product, data) in enumerate(sorted_products[:5], 1):
        print(f"{i:<4} {product:<25} {data['units']:<12} ${data['cost']:.2f}")

def compare_service_types():
    """
    Compare predicted demand between Retail and Pick & Pack services
    """
    print("\n" + "="*60)
    print("SERVICE TYPE COMPARISON")
    print("="*60)
    
    # Load the saved model
    predictor = AirlineConsumptionPredictor.load_trained_model("airline_consumption_model")
    
    if predictor is None:
        print("❌ Failed to load model.")
        return
    
    # Same flight conditions, different service types
    base_flight = {
        'origin': 'JFK',
        'flight_type': 'long-haul',
        'passenger_count': 300
    }
    
    products = [
        {'name': 'Still Water 500ml', 'cost': 0.5},
        {'name': 'Juice 200ml', 'cost': 0.55},
        {'name': 'Bread Roll Pack', 'cost': 0.35},
        {'name': 'Mixed Nuts 30g', 'cost': 0.65},
        {'name': 'Instant Coffee Stick', 'cost': 0.08}
    ]
    
    print(f"Flight: {base_flight['origin']} {base_flight['flight_type']} | Passengers: {base_flight['passenger_count']}")
    print("\n" + "-" * 75)
    print(f"{'Product':<25} {'Retail':<10} {'Pick&Pack':<10} {'Difference':<12} {'% Increase'}")
    print("-" * 75)
    
    total_retail = 0
    total_pick_pack = 0
    
    for product in products:
        # Retail prediction
        retail_demand = predictor.predict_consumption(
            origin=base_flight['origin'],
            flight_type=base_flight['flight_type'],
            service_type='Retail',
            passenger_count=base_flight['passenger_count'],
            product_name=product['name'],
            unit_cost=product['cost']
        )
        
        # Pick & Pack prediction
        pick_pack_demand = predictor.predict_consumption(
            origin=base_flight['origin'],
            flight_type=base_flight['flight_type'],
            service_type='Pick & Pack',
            passenger_count=base_flight['passenger_count'],
            product_name=product['name'],
            unit_cost=product['cost']
        )
        
        difference = pick_pack_demand - retail_demand
        percent_increase = (difference / retail_demand * 100) if retail_demand > 0 else 0
        
        total_retail += retail_demand
        total_pick_pack += pick_pack_demand
        
        print(f"{product['name']:<25} {retail_demand:<10} {pick_pack_demand:<10} "
              f"{difference:>+4} units   {percent_increase:>+6.1f}%")
    
    print("-" * 75)
    total_difference = total_pick_pack - total_retail
    total_percent = (total_difference / total_retail * 100) if total_retail > 0 else 0
    print(f"{'TOTALS':<25} {total_retail:<10} {total_pick_pack:<10} "
          f"{total_difference:>+4} units   {total_percent:>+6.1f}%")
    
    print(f"\n📈 KEY INSIGHTS:")
    print(f"• Pick & Pack service increases demand by {total_percent:.1f}% on average")
    print(f"• Total difference: {total_difference} units for {base_flight['passenger_count']} passengers")
    print(f"• Per passenger increase: {total_difference/base_flight['passenger_count']:.2f} units")

if __name__ == "__main__":
    # Run all examples
    make_predictions_with_saved_model()
    batch_predictions_from_csv()
    inventory_planning_example()
    flight_demand_analysis()
    compare_service_types()