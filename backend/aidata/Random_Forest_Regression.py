import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import joblib
import pickle
import os
warnings.filterwarnings('ignore')

class AirlineConsumptionPredictor:
    def __init__(self, csv_file_path):
        """
        Initialize the predictor with the dataset path
        """
        self.csv_file_path = csv_file_path
        self.df = None
        self.df_processed = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.model = None
        self.feature_importance = None
        
    def load_and_explore_data(self):
        """
        Load the dataset and perform initial exploration
        """
        print("Loading dataset...")
        self.df = pd.read_csv(self.csv_file_path)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        print("\nFirst few rows:")
        print(self.df.head())
        
        print("\nDataset info:")
        print(self.df.info())
        
        print("\nMissing values:")
        print(self.df.isnull().sum())
        
        print("\nTarget variable (Quantity_Consumed) statistics:")
        print(self.df['Quantity_Consumed'].describe())
        
        return self.df
    
    def preprocess_data(self):
        """
        Comprehensive data preprocessing for Random Forest regression
        """
        print("\n" + "="*50)
        print("STARTING DATA PREPROCESSING")
        print("="*50)
        
        # Create a copy for processing
        self.df_processed = self.df.copy()
        
        # 1. Handle missing values and data cleaning
        print("\n1. Data Cleaning...")
        
        # Remove rows with zero consumption (not meaningful for prediction)
        initial_rows = len(self.df_processed)
        self.df_processed = self.df_processed[self.df_processed['Quantity_Consumed'] > 0]
        print(f"   - Removed {initial_rows - len(self.df_processed)} rows with zero consumption")
        
        # Clean crew feedback (remove problematic entries if needed)
        problematic_feedback = ['drawer incomplete', 'ran out early', 'low demand']
        clean_data = self.df_processed[~self.df_processed['Crew_Feedback'].isin(problematic_feedback)]
        problematic_data = self.df_processed[self.df_processed['Crew_Feedback'].isin(problematic_feedback)]
        
        print(f"   - Found {len(problematic_data)} rows with operational issues")
        print(f"   - Keeping all data for analysis (can be filtered later)")
        
        # 2. Feature Engineering
        print("\n2. Feature Engineering...")
        
        # Add consumption efficiency metrics
        self.df_processed['Consumption_Rate'] = (
            self.df_processed['Quantity_Consumed'] / 
            self.df_processed['Standard_Specification_Qty']
        )
        
        self.df_processed['Return_Rate'] = (
            self.df_processed['Quantity_Returned'] / 
            self.df_processed['Standard_Specification_Qty']
        )
        
        # Add per-passenger consumption
        self.df_processed['Consumption_Per_Passenger'] = (
            self.df_processed['Quantity_Consumed'] / 
            self.df_processed['Passenger_Count']
        )
        
        # Add binary features for operational issues
        self.df_processed['Has_Issues'] = self.df_processed['Crew_Feedback'].isin(problematic_feedback).astype(int)
        
        print(f"   - Added consumption rate, return rate, and per-passenger metrics")
        print(f"   - Will use actual Product Names instead of categories")
        
        # 3. Encode categorical variables
        print("\n3. Encoding Categorical Variables...")
        
        categorical_features = ['Origin', 'Flight_Type', 'Service_Type', 'Product_Name']
        
        for feature in categorical_features:
            le = LabelEncoder()
            self.df_processed[f'{feature}_encoded'] = le.fit_transform(self.df_processed[feature])
            self.label_encoders[feature] = le
            print(f"   - Encoded {feature}: {dict(zip(le.classes_, le.transform(le.classes_)))}")
        
        # 4. Select features for the model
        print("\n4. Feature Selection...")
        
        # Define feature columns for the model - EXCLUDING Standard_Specification_Qty 
        # to predict actual demand based on flight characteristics
        self.feature_columns = [
            'Origin_encoded', 'Flight_Type_encoded', 'Service_Type_encoded', 
            'Passenger_Count', 'Product_Name_encoded', 'Unit_Cost', 'Has_Issues'
        ]
        
        self.target_column = 'Quantity_Consumed'
        
        print(f"   - Selected features: {self.feature_columns}")
        print(f"   - Target variable: {self.target_column}")
        print(f"   - Note: Excluded Standard_Specification_Qty to predict actual demand")
        print(f"   - Model will predict consumption based on flight characteristics only")
        
        # 5. Create final dataset
        print("\n5. Creating Final Dataset...")
        
        # Ensure no missing values in selected features
        self.df_final = self.df_processed[self.feature_columns + [self.target_column]].copy()
        
        # Remove any remaining NaN values
        initial_rows = len(self.df_final)
        self.df_final = self.df_final.dropna()
        print(f"   - Removed {initial_rows - len(self.df_final)} rows with missing values")
        
        print(f"\nFinal dataset shape: {self.df_final.shape}")
        print("Feature distributions:")
        print(self.df_final[self.feature_columns].describe())
        
        return self.df_final
    
    def create_visualizations(self):
        """
        Create visualizations to understand the data better
        """
        print("\n" + "="*50)
        print("CREATING DATA VISUALIZATIONS")
        print("="*50)
        
        plt.figure(figsize=(20, 15))
        
        # 1. Target variable distribution
        plt.subplot(3, 4, 1)
        plt.hist(self.df_processed['Quantity_Consumed'], bins=50, alpha=0.7, color='skyblue')
        plt.title('Distribution of Quantity Consumed')
        plt.xlabel('Quantity Consumed')
        plt.ylabel('Frequency')
        
        # 2. Consumption by Flight Type
        plt.subplot(3, 4, 2)
        self.df_processed.groupby('Flight_Type')['Quantity_Consumed'].mean().plot(kind='bar', color='lightcoral')
        plt.title('Average Consumption by Flight Type')
        plt.xticks(rotation=45)
        
        # 3. Consumption by Service Type
        plt.subplot(3, 4, 3)
        self.df_processed.groupby('Service_Type')['Quantity_Consumed'].mean().plot(kind='bar', color='lightgreen')
        plt.title('Average Consumption by Service Type')
        plt.xticks(rotation=45)
        
        # 4. Consumption by Origin
        plt.subplot(3, 4, 4)
        self.df_processed.groupby('Origin')['Quantity_Consumed'].mean().plot(kind='bar', color='gold')
        plt.title('Average Consumption by Origin')
        plt.xticks(rotation=45)
        
        # 5. Consumption by Product Name
        plt.subplot(3, 4, 5)
        product_consumption = self.df_processed.groupby('Product_Name')['Quantity_Consumed'].mean().sort_values(ascending=False)
        product_consumption.head(10).plot(kind='bar', color='purple', alpha=0.7)
        plt.title('Top 10 Products by Average Consumption')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 6. Passenger Count vs Consumption
        plt.subplot(3, 4, 6)
        plt.scatter(self.df_processed['Passenger_Count'], self.df_processed['Quantity_Consumed'], alpha=0.6)
        plt.title('Passenger Count vs Quantity Consumed')
        plt.xlabel('Passenger Count')
        plt.ylabel('Quantity Consumed')
        
        # 7. Unit Cost vs Consumption
        plt.subplot(3, 4, 7)
        plt.scatter(self.df_processed['Unit_Cost'], self.df_processed['Quantity_Consumed'], alpha=0.6, color='red')
        plt.title('Unit Cost vs Quantity Consumed')
        plt.xlabel('Unit Cost')
        plt.ylabel('Quantity Consumed')
        
        # 8. Consumption Rate Distribution
        plt.subplot(3, 4, 8)
        plt.hist(self.df_processed['Consumption_Rate'], bins=50, alpha=0.7, color='orange')
        plt.title('Distribution of Consumption Rate')
        plt.xlabel('Consumption Rate')
        plt.ylabel('Frequency')
        
        # 9. Heatmap of correlations (updated to exclude Standard_Specification_Qty)
        plt.subplot(3, 4, 9)
        correlation_features = ['Passenger_Count', 'Unit_Cost', 
                              'Quantity_Consumed', 'Consumption_Rate', 'Return_Rate']
        corr_matrix = self.df_processed[correlation_features].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Feature Correlations (Excl. Std Qty)')
        
        # 10. Per-passenger consumption by flight type
        plt.subplot(3, 4, 10)
        self.df_processed.groupby('Flight_Type')['Consumption_Per_Passenger'].mean().plot(kind='bar', color='teal')
        plt.title('Per-Passenger Consumption by Flight Type')
        plt.xticks(rotation=45)
        
        # 11. Issues impact on consumption
        plt.subplot(3, 4, 11)
        issue_comparison = self.df_processed.groupby('Has_Issues')['Quantity_Consumed'].mean()
        plt.bar(['No Issues', 'Has Issues'], issue_comparison.values, color=['green', 'red'], alpha=0.7)
        plt.title('Consumption: Normal vs Issues')
        plt.ylabel('Average Quantity Consumed')
        
        # 12. Flight type distribution
        plt.subplot(3, 4, 12)
        self.df_processed['Flight_Type'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Flight Type Distribution')
        
        plt.tight_layout()
        plt.show()
        
        # Summary statistics by key categories
        print("\nSummary Statistics by Categories:")
        print("\n1. By Flight Type:")
        print(self.df_processed.groupby('Flight_Type')['Quantity_Consumed'].agg(['mean', 'std', 'count']))
        
        print("\n2. By Service Type:")
        print(self.df_processed.groupby('Service_Type')['Quantity_Consumed'].agg(['mean', 'std', 'count']))
        
        print("\n3. By Origin:")
        print(self.df_processed.groupby('Origin')['Quantity_Consumed'].agg(['mean', 'std', 'count']))
        
        print("\n4. By Product Name (Top 10):")
        product_stats = self.df_processed.groupby('Product_Name')['Quantity_Consumed'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)
        print(product_stats.head(10))
    
    def train_random_forest(self, test_size=0.2, random_state=42):
        """
        Train the Random Forest regression model
        """
        print("\n" + "="*50)
        print("TRAINING RANDOM FOREST MODEL")
        print("="*50)
        
        # Prepare features and target
        X = self.df_final[self.feature_columns]
        y = self.df_final[self.target_column]
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # Train baseline model
        print("\nTraining baseline Random Forest...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Calculate metrics
        train_mse = mean_squared_error(y_train, y_pred_train)
        test_mse = mean_squared_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        print(f"\nBaseline Model Performance:")
        print(f"Training R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        print(f"Training RMSE: {np.sqrt(train_mse):.4f}")
        print(f"Test RMSE: {np.sqrt(test_mse):.4f}")
        print(f"Training MAE: {train_mae:.4f}")
        print(f"Test MAE: {test_mae:.4f}")
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nFeature Importance:")
        print(self.feature_importance)
        
        # Cross-validation
        print(f"\nPerforming 5-fold cross-validation...")
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='r2')
        print(f"CV R² scores: {cv_scores}")
        print(f"Mean CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Additional insights for demand-based model
        print(f"\n" + "-"*30)
        print("DEMAND-BASED MODEL INSIGHTS")
        print("-"*30)
        print("This model predicts actual consumption demand based on:")
        print("• Flight characteristics (origin, type, service)")
        print("• Passenger count")
        print("• Product type and cost")
        print("• Operational issues")
        print("\nKey advantages:")
        print("• Predicts true demand regardless of stock levels")
        print("• Helps optimize inventory planning")
        print("• Identifies demand patterns by route and service type")
        
        # Calculate demand vs supply insights
        self.df_final['Demand_vs_Supply'] = self.df_final['Quantity_Consumed'] / self.df_processed.loc[self.df_final.index, 'Standard_Specification_Qty']
        avg_utilization = self.df_final['Demand_vs_Supply'].mean()
        print(f"\nAverage demand utilization: {avg_utilization:.2%}")
        print(f"This suggests typical demand is {avg_utilization:.1%} of stocked quantity")
        
        # Store datasets for further analysis
        self.X_train, self.X_test = X_train, X_test
        self.y_train, self.y_test = y_train, y_test
        self.y_pred_train, self.y_pred_test = y_pred_train, y_pred_test
        
        return self.model
    
    def hyperparameter_tuning(self):
        """
        Perform hyperparameter tuning using GridSearchCV
        """
        print("\n" + "="*50)
        print("HYPERPARAMETER TUNING")
        print("="*50)
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['auto', 'sqrt', 'log2']
        }
        
        # Prepare data
        X = self.df_final[self.feature_columns]
        y = self.df_final[self.target_column]
        
        # Grid search
        print("Performing Grid Search (this may take a while)...")
        grid_search = GridSearchCV(
            RandomForestRegressor(random_state=42, n_jobs=-1),
            param_grid,
            cv=3,  # Reduced for faster execution
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        print(f"\nBest parameters: {grid_search.best_params_}")
        print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
        
        # Train final model with best parameters
        self.model_tuned = grid_search.best_estimator_
        
        # Evaluate tuned model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        y_pred_tuned = self.model_tuned.predict(X_test)
        tuned_r2 = r2_score(y_test, y_pred_tuned)
        tuned_rmse = np.sqrt(mean_squared_error(y_test, y_pred_tuned))
        
        print(f"\nTuned Model Performance:")
        print(f"Test R²: {tuned_r2:.4f}")
        print(f"Test RMSE: {tuned_rmse:.4f}")
        
        return self.model_tuned
    
    def create_model_visualizations(self):
        """
        Create visualizations for model performance
        """
        print("\n" + "="*50)
        print("MODEL PERFORMANCE VISUALIZATIONS")
        print("="*50)
        
        plt.figure(figsize=(15, 10))
        
        # 1. Feature Importance
        plt.subplot(2, 3, 1)
        self.feature_importance.plot(x='feature', y='importance', kind='barh', ax=plt.gca())
        plt.title('Feature Importance')
        plt.xlabel('Importance')
        
        # 2. Predicted vs Actual (Training)
        plt.subplot(2, 3, 2)
        plt.scatter(self.y_train, self.y_pred_train, alpha=0.6)
        plt.plot([self.y_train.min(), self.y_train.max()], [self.y_train.min(), self.y_train.max()], 'r--', lw=2)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title('Training: Predicted vs Actual')
        
        # 3. Predicted vs Actual (Test)
        plt.subplot(2, 3, 3)
        plt.scatter(self.y_test, self.y_pred_test, alpha=0.6, color='orange')
        plt.plot([self.y_test.min(), self.y_test.max()], [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title('Test: Predicted vs Actual')
        
        # 4. Residuals (Training)
        plt.subplot(2, 3, 4)
        residuals_train = self.y_train - self.y_pred_train
        plt.scatter(self.y_pred_train, residuals_train, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted')
        plt.ylabel('Residuals')
        plt.title('Training Residuals')
        
        # 5. Residuals (Test)
        plt.subplot(2, 3, 5)
        residuals_test = self.y_test - self.y_pred_test
        plt.scatter(self.y_pred_test, residuals_test, alpha=0.6, color='orange')
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted')
        plt.ylabel('Residuals')
        plt.title('Test Residuals')
        
        # 6. Error Distribution
        plt.subplot(2, 3, 6)
        plt.hist(residuals_test, bins=30, alpha=0.7, color='skyblue')
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.title('Test Residuals Distribution')
        
        plt.tight_layout()
        plt.show()
    
    def predict_consumption(self, origin, flight_type, service_type, passenger_count, 
                          product_name, unit_cost, has_issues=0):
        """
        Predict consumption for new data based on flight characteristics
        Note: No longer requires standard_qty as input - predicts actual demand
        """
        # Encode categorical variables
        try:
            origin_encoded = self.label_encoders['Origin'].transform([origin])[0]
            flight_type_encoded = self.label_encoders['Flight_Type'].transform([flight_type])[0]
            service_type_encoded = self.label_encoders['Service_Type'].transform([service_type])[0]
            product_name_encoded = self.label_encoders['Product_Name'].transform([product_name])[0]
        except ValueError as e:
            print(f"Error: Unknown category value - {e}")
            return None
        
        # Create feature array (without standard_qty)
        features = np.array([[
            origin_encoded, flight_type_encoded, service_type_encoded,
            passenger_count, product_name_encoded, unit_cost, has_issues
        ]])
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        
        return max(0, round(prediction))  # Ensure non-negative and integer result
    
    def save_model(self, model_dir="airline_model"):
        """
        Save the trained model and all necessary components for later use
        """
        # Create directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        if self.model is None:
            print("Error: No trained model to save. Please train the model first.")
            return False
        
        try:
            # Save the trained Random Forest model
            model_path = os.path.join(model_dir, "random_forest_model.pkl")
            joblib.dump(self.model, model_path)
            
            # Save label encoders
            encoders_path = os.path.join(model_dir, "label_encoders.pkl")
            with open(encoders_path, 'wb') as f:
                pickle.dump(self.label_encoders, f)
            
            # Save feature columns and other metadata
            metadata = {
                'feature_columns': self.feature_columns,
                'target_column': self.target_column,
                'feature_importance': self.feature_importance.to_dict() if self.feature_importance is not None else None
            }
            metadata_path = os.path.join(model_dir, "model_metadata.pkl")
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            print(f"✅ Model saved successfully in '{model_dir}' directory!")
            print(f"   - Model: {model_path}")
            print(f"   - Label encoders: {encoders_path}")
            print(f"   - Metadata: {metadata_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def load_model(self, model_dir="airline_model"):
        """
        Load a previously saved model and all necessary components
        """
        model_path = os.path.join(model_dir, "random_forest_model.pkl")
        encoders_path = os.path.join(model_dir, "label_encoders.pkl")
        metadata_path = os.path.join(model_dir, "model_metadata.pkl")
        
        # Check if all required files exist
        required_files = [model_path, encoders_path, metadata_path]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"❌ Error: Missing required files: {missing_files}")
            return False
        
        try:
            # Load the model
            self.model = joblib.load(model_path)
            
            # Load label encoders
            with open(encoders_path, 'rb') as f:
                self.label_encoders = pickle.load(f)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.feature_columns = metadata['feature_columns']
                self.target_column = metadata['target_column']
                if metadata['feature_importance'] is not None:
                    self.feature_importance = pd.DataFrame(metadata['feature_importance'])
            
            print(f"✅ Model loaded successfully from '{model_dir}' directory!")
            print(f"   - Features: {self.feature_columns}")
            print(f"   - Available categories:")
            for feature, encoder in self.label_encoders.items():
                print(f"     • {feature}: {list(encoder.classes_)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    @classmethod
    def load_trained_model(cls, model_dir="airline_model"):
        """
        Class method to create a new instance with a pre-trained model
        Usage: predictor = AirlineConsumptionPredictor.load_trained_model("my_model")
        """
        # Create instance without CSV file (for prediction only)
        instance = cls(csv_file_path=None)
        
        if instance.load_model(model_dir):
            return instance
        else:
            return None

def main():
    """
    Main function to run the complete analysis
    """
    # Initialize the predictor
    #csv_path = r"(HackMTY2025)_ConsumptionPrediction_Dataset_v1.csv"
    current_dir = os.path.dirname(__file__)
    print(current_dir)
    relative_path = os.path.join(current_dir, '(HackMTY2025)_ConsumptionPrediction_Dataset_v1.csv')
    print(f"Using dataset path: {relative_path}")
    predictor = AirlineConsumptionPredictor(relative_path)
    
    # Load and explore data
    df = predictor.load_and_explore_data()
    
    # Preprocess data
    df_processed = predictor.preprocess_data()
    
    # Create visualizations
    predictor.create_visualizations()
    
    # Train model
    model = predictor.train_random_forest()
    
    # Create model visualizations
    predictor.create_model_visualizations()
    
    # Save the trained model
    print("\n" + "="*50)
    print("SAVING TRAINED MODEL")
    print("="*50)
    predictor.save_model("airline_consumption_model")
    
    # Optional: Hyperparameter tuning (uncomment if needed)
    # tuned_model = predictor.hyperparameter_tuning()
    
    # Example prediction
    print("\n" + "="*50)
    print("EXAMPLE PREDICTION - DEMAND-BASED MODEL")
    print("="*50)
    print("Predicting actual consumption demand based on flight characteristics only")
    
    example_prediction = predictor.predict_consumption(
        origin='DOH',
        flight_type='medium-haul',
        service_type='Retail',
        passenger_count=250,
        product_name='Sparkling Water 330ml',
        unit_cost=0.45,
        has_issues=0
    )
    
    print(f"Predicted consumption demand: {example_prediction} units")
    print("Note: This represents actual demand, regardless of standard quantity stocked")
    
    return predictor

if __name__ == "__main__":
    predictor = main()