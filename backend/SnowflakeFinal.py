"""
Snowflake API Example with .env Configuration
============================================

This script demonstrates comprehensive Snowflake operations using
credentials from your .env file. It includes:
- Connection management
- Table operations (CREATE, INSERT, UPDATE, DELETE)
- Data queries and analytics
- Pandas integration
- Real-world airline data examples
- Error handling and best practices

Requirements:
- pip install snowflake-connector-python python-dotenv pandas sqlalchemy snowflake-sqlalchemy
"""

import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()



class SnowflakeConnection:
    """
    Snowflake connection manager using .env configuration
    """
    
    def __init__(self):
        """Initialize with credentials from .env file"""
        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        }
        
        self.connection = None
        self.cursor = None
        self.engine = None
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required credentials are present"""
        required_fields = ['account', 'user', 'password', 'warehouse', 'database']
        missing_fields = [field for field in required_fields if not self.config[field]]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in .env file: {missing_fields}")
        
        print("✅ Configuration loaded from .env file:")
        print(f"   Account: {self.config['account']}")
        print(f"   User: {self.config['user']}")
        print(f"   Database: {self.config['database']}")
        print(f"   Warehouse: {self.config['warehouse']}")
        print(f"   Schema: {self.config['schema']}")
    
    def connect(self):
        """Establish connection to Snowflake"""
        try:
            print("\n🔌 Connecting to Snowflake...")
            
            # Create main connection
            self.connection = snowflake.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            
            # Create SQLAlchemy engine for pandas operations
            connection_string = (f"snowflake://{self.config['user']}:{self.config['password']}"
                               f"@{self.config['account']}/{self.config['database']}"
                               f"/{self.config['schema']}?warehouse={self.config['warehouse']}")
            
            self.engine = create_engine(connection_string)
            
            print("✅ Successfully connected to Snowflake!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close all connections"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            if self.engine:
                self.engine.dispose()
            print("🔌 Disconnected from Snowflake")
        except Exception as e:
            print(f"⚠️  Error during disconnect: {e}")
    
    def execute_query(self, sql, fetch=True, params=None):
        """
        Execute SQL query with optional parameters and auto-reconnect
        
        Args:
            sql: SQL query string
            fetch: Whether to fetch results
            params: Optional parameters for the query
            
        Returns:
            Query results if fetch=True, None otherwise
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            if fetch:
                results = self.cursor.fetchall()
                return results
            else:
                return None
                
        except Exception as e:
            error_message = str(e)
            # Check if it's an authentication/token expiration error
            if "390114" in error_message or "Authentication token has expired" in error_message or "Invalid access token" in error_message:
                print("⚠️  Snowflake token expired. Reconnecting...")
                self.disconnect()
                if self.connect():
                    print("✅ Reconnected successfully. Retrying query...")
                    # Retry the query once after reconnection
                    try:
                        if params:
                            self.cursor.execute(sql, params)
                        else:
                            self.cursor.execute(sql)
                        
                        if fetch:
                            results = self.cursor.fetchall()
                            return results
                        else:
                            return None
                    except Exception as retry_error:
                        print(f"❌ Query failed after reconnection: {retry_error}")
                        return None
                else:
                    print("❌ Failed to reconnect to Snowflake")
                    return None
            else:
                print(f"❌ Query execution failed: {e}")
                print(f"   SQL: {sql[:100]}...")
                return None
    
    def query_to_dataframe(self, sql):
        """Execute query and return as pandas DataFrame"""
        try:
            df = pd.read_sql(sql, self.engine)
            return df
        except Exception as e:
            print(f"❌ DataFrame query failed: {e}")
            return None
    
    def upload_dataframe(self, df, table_name, if_exists='replace'):
        """Upload pandas DataFrame to Snowflake table"""
        try:
            df.to_sql(
                name=table_name.upper(),
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            print(f"✅ Uploaded {len(df)} rows to table {table_name.upper()}")
            return True
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def add_product_data(self, product_data):
        """
        Add new product data to the PRODUCT_DATA table
        
        Args:
            product_data: Can be either:
                - Single tuple: (barcode, product_id, product_name, lot_number, quantity, exp_date)
                - List of tuples: [(barcode1, product_id1, ...), (barcode2, product_id2, ...)]
                - Dictionary: {'barcode': '...', 'product_id': '...', etc.}
                - List of dictionaries: [{'barcode': '...', 'product_id': '...'}, {...}]
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle different input formats
            if isinstance(product_data, dict):
                # Single dictionary
                data_tuples = [(
                    product_data['barcode'],
                    product_data['product_id'], 
                    product_data['product_name'],
                    product_data['lot_number'],
                    product_data['quantity'],
                    product_data['exp_date']
                )]
            elif isinstance(product_data, list):
                if isinstance(product_data[0], dict):
                    # List of dictionaries
                    data_tuples = [
                        (item['barcode'], item['product_id'], item['product_name'],
                         item['lot_number'], item['quantity'], item['exp_date'])
                        for item in product_data
                    ]
                else:
                    # List of tuples or single tuple
                    data_tuples = [product_data] if isinstance(product_data[0], str) else product_data
            else:
                # Single tuple
                data_tuples = [product_data]
            
            # Insert SQL
            insert_sql = """
            INSERT INTO PRODUCT_DATA (
                Barcode, ProductID, ProductName, LotNumber, Quantity, Exp_Date
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Execute insertions
            success_count = 0
            for data_tuple in data_tuples:
                result = self.execute_query(insert_sql, fetch=False, params=data_tuple)
                if result is not None or True:  # execute_query returns None for non-fetch operations
                    success_count += 1
            
            print(f"✅ Successfully added {success_count} product record(s) to PRODUCT_DATA")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add product data: {e}")
            return False
    
    def add_custom_data(self, table_name, data, columns=None):
        """
        Add data to any table in the database
        
        Args:
            table_name (str): Name of the target table
            data: Data to insert - can be tuple, list of tuples, dict, or list of dicts
            columns (list): Column names (required if using tuples)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle different input formats
            if isinstance(data, dict):
                columns = list(data.keys())
                data_tuples = [tuple(data.values())]
            elif isinstance(data, list):
                if isinstance(data[0], dict):
                    columns = list(data[0].keys())
                    data_tuples = [tuple(item.values()) for item in data]
                else:
                    if columns is None:
                        raise ValueError("Column names must be provided when using tuple format")
                    data_tuples = [data] if not isinstance(data[0], (list, tuple)) else data
            else:
                if columns is None:
                    raise ValueError("Column names must be provided when using tuple format")
                data_tuples = [data]
            
            # Build INSERT SQL
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"""
            INSERT INTO {table_name.upper()} ({columns_str})
            VALUES ({placeholders})
            """
            
            # Execute insertions
            success_count = 0
            for data_tuple in data_tuples:
                result = self.execute_query(insert_sql, fetch=False, params=data_tuple)
                if result is not None or True:
                    success_count += 1
            
            print(f"✅ Successfully added {success_count} record(s) to {table_name.upper()}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add data to {table_name}: {e}")
            return False
    
    def check_barcode_exists(self, barcode):
        """
        Check if a barcode already exists in the PRODUCT_DATA table
        
        Args:
            barcode (str): The barcode to search for
        
        Returns:
            dict: {
                'exists': bool,
                'product_info': dict or None,
                'count': int
            }
        """
        try:
            # Query to check if barcode exists and get product info
            search_query = """
            SELECT 
                Barcode,
                ProductID,
                ProductName,
                LotNumber,
                Quantity,
                Exp_Date,
                DATEDIFF('day', CURRENT_DATE(), Exp_Date) as days_until_expiration
            FROM PRODUCT_DATA 
            WHERE Barcode = %s
            """
            
            result = self.execute_query(search_query, fetch=True, params=(barcode,))
            
            if result and len(result) > 0:
                # Barcode exists - return product information
                product_data = result[0]
                product_info = {
                    'barcode': product_data[0],
                    'product_id': product_data[1],
                    'product_name': product_data[2],
                    'lot_number': product_data[3],
                    'quantity': product_data[4],
                    'exp_date': product_data[5],
                    'days_until_expiration': product_data[6]
                }
                
                print(f"✅ Barcode {barcode} found in database:")
                print(f"   Product: {product_info['product_name']}")
                print(f"   ID: {product_info['product_id']}")
                print(f"   Quantity: {product_info['quantity']}")
                print(f"   Expires in: {product_info['days_until_expiration']} days")
                
                return {
                    'exists': True,
                    'product_info': product_info,
                    'count': len(result)
                }
            else:
                # Barcode doesn't exist
                print(f"❌ Barcode {barcode} not found in database")
                return {
                    'exists': False,
                    'product_info': None,
                    'count': 0
                }
                
        except Exception as e:
            print(f"❌ Error checking barcode {barcode}: {e}")
            return {
                'exists': False,
                'product_info': None,
                'count': 0
            }
    
    def search_barcodes(self, barcodes):
        """
        Search for multiple barcodes at once
        
        Args:
            barcodes (list): List of barcodes to search for
        
        Returns:
            dict: {
                'found': list of product info dicts,
                'not_found': list of barcodes not found,
                'summary': dict with counts
            }
        """
        try:
            if isinstance(barcodes, str):
                barcodes = [barcodes]
            
            found_products = []
            not_found_barcodes = []
            
            print(f"\n🔍 Searching for {len(barcodes)} barcode(s)...")
            
            for barcode in barcodes:
                result = self.check_barcode_exists(barcode)
                if result['exists']:
                    found_products.append(result['product_info'])
                else:
                    not_found_barcodes.append(barcode)
            
            summary = {
                'total_searched': len(barcodes),
                'found_count': len(found_products),
                'not_found_count': len(not_found_barcodes),
                'success_rate': round((len(found_products) / len(barcodes)) * 100, 2)
            }
            
            print(f"\n📊 Search Summary:")
            print(f"   Total searched: {summary['total_searched']}")
            print(f"   Found: {summary['found_count']}")
            print(f"   Not found: {summary['not_found_count']}")
            print(f"   Success rate: {summary['success_rate']}%")
            
            return {
                'found': found_products,
                'not_found': not_found_barcodes,
                'summary': summary
            }
            
        except Exception as e:
            print(f"❌ Error in batch barcode search: {e}")
            return {
                'found': [],
                'not_found': barcodes,
                'summary': {'total_searched': len(barcodes), 'found_count': 0, 'not_found_count': len(barcodes), 'success_rate': 0}
            }
    
    def update_existing_product(self, barcode, **kwargs):
        """
        Update an existing product in the PRODUCT_DATA table using barcode as identifier
        
        Args:
            barcode (str): The barcode of the product to update
            **kwargs: Fields to update. Possible fields:
                - product_id: New product ID
                - product_name: New product name
                - lot_number: New lot number
                - quantity: New quantity
                - exp_date: New expiration date
        
        Returns:
            dict: {
                'success': bool,
                'updated_fields': list,
                'old_values': dict,
                'new_values': dict
            }
        """
        try:
            # First check if the product exists
            check_result = self.check_barcode_exists(barcode)
            if not check_result['exists']:
                print(f"❌ Cannot update: Barcode {barcode} not found in database")
                return {
                    'success': False,
                    'updated_fields': [],
                    'old_values': {},
                    'new_values': {},
                    'error': 'Product not found'
                }
            
            # Get current product info
            old_product = check_result['product_info']
            
            # Map kwargs to database column names
            field_mapping = {
                'product_id': 'ProductID',
                'product_name': 'ProductName',
                'lot_number': 'LotNumber',
                'quantity': 'Quantity',
                'exp_date': 'Exp_Date'
            }
            
            # Build the UPDATE query
            update_fields = []
            update_values = []
            updated_field_names = []
            
            for field, value in kwargs.items():
                if field in field_mapping:
                    db_field = field_mapping[field]
                    update_fields.append(f"{db_field} = %s")
                    update_values.append(value)
                    updated_field_names.append(field)
                else:
                    print(f"⚠️  Warning: Unknown field '{field}' ignored")
            
            if not update_fields:
                print("❌ No valid fields provided for update")
                return {
                    'success': False,
                    'updated_fields': [],
                    'old_values': {},
                    'new_values': {},
                    'error': 'No valid fields to update'
                }
            
            # Construct and execute UPDATE query
            update_sql = f"""
            UPDATE PRODUCT_DATA 
            SET {', '.join(update_fields)}
            WHERE Barcode = %s
            """
            
            # Add barcode to the end of values list
            update_values.append(barcode)
            
            # Execute the update
            result = self.execute_query(update_sql, fetch=False, params=update_values)
            
            # Verify the update was successful
            new_check = self.check_barcode_exists(barcode)
            if new_check['exists']:
                new_product = new_check['product_info']
                
                # Prepare old and new values for comparison
                old_values = {}
                new_values = {}
                
                for field in updated_field_names:
                    old_key = field
                    if old_key == 'exp_date':
                        old_values[field] = str(old_product['exp_date'])
                        new_values[field] = str(new_product['exp_date'])
                    else:
                        old_values[field] = old_product[old_key]
                        new_values[field] = new_product[old_key]
                
                print(f"✅ Successfully updated product with barcode {barcode}")
                print(f"   Updated fields: {', '.join(updated_field_names)}")
                
                # Show what changed
                for field in updated_field_names:
                    print(f"   {field}: {old_values[field]} → {new_values[field]}")
                
                return {
                    'success': True,
                    'updated_fields': updated_field_names,
                    'old_values': old_values,
                    'new_values': new_values
                }
            else:
                print(f"❌ Update verification failed for barcode {barcode}")
                return {
                    'success': False,
                    'updated_fields': updated_field_names,
                    'old_values': {},
                    'new_values': {},
                    'error': 'Update verification failed'
                }
                
        except Exception as e:
            print(f"❌ Error updating product with barcode {barcode}: {e}")
            return {
                'success': False,
                'updated_fields': [],
                'old_values': {},
                'new_values': {},
                'error': str(e)
            }
    
    def update_product_quantity(self, barcode, new_quantity, operation='set'):
        """
        Update product quantity with different operation modes
        
        Args:
            barcode (str): Product barcode
            new_quantity (int): Quantity value
            operation (str): 'set' (replace), 'add' (increase), 'subtract' (decrease)
        
        Returns:
            dict: Update result with old and new quantities
        """
        try:
            # Check if product exists
            check_result = self.check_barcode_exists(barcode)
            if not check_result['exists']:
                print(f"❌ Cannot update quantity: Barcode {barcode} not found")
                return {'success': False, 'error': 'Product not found'}
            
            current_quantity = check_result['product_info']['quantity']
            
            # Calculate new quantity based on operation
            if operation == 'set':
                final_quantity = new_quantity
            elif operation == 'add':
                final_quantity = current_quantity + new_quantity
            elif operation == 'subtract':
                final_quantity = max(0, current_quantity - new_quantity)  # Prevent negative
            else:
                print(f"❌ Invalid operation: {operation}")
                return {'success': False, 'error': 'Invalid operation'}
            
            # Update the quantity
            result = self.update_existing_product(barcode, quantity=final_quantity)
            
            if result['success']:
                print(f"📦 Quantity update for {check_result['product_info']['product_name']}:")
                print(f"   Operation: {operation}")
                print(f"   Previous: {current_quantity}")
                print(f"   Change: {new_quantity}")
                print(f"   New total: {final_quantity}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error updating quantity for barcode {barcode}: {e}")
            return {'success': False, 'error': str(e)}

def demonstrate_basic_operations(sf):
    """Demonstrate basic Snowflake operations"""
    print("\n📊 BASIC OPERATIONS DEMO")
    print("=" * 40)
    
    # 1. Get system information
    print("\n1️⃣ System Information")
    print("-" * 25)
    
    system_query = """
    SELECT 
        CURRENT_USER() as current_user,
        CURRENT_VERSION() as snowflake_version,
        CURRENT_WAREHOUSE() as warehouse,
        CURRENT_DATABASE() as database,
        CURRENT_SCHEMA() as schema,
        CURRENT_TIMESTAMP() as current_time
    """
    
    system_info = sf.execute_query(system_query)
    if system_info:
        info = system_info[0]
        print(f"👤 User: {info[0]}")
        print(f"📦 Version: {info[1]}")
        print(f"🏭 Warehouse: {info[2]}")
        print(f"🗄️  Database: {info[3]}")
        print(f"📂 Schema: {info[4]}")
        print(f"🕐 Time: {info[5]}")
    
    # 2. Create sample table
    print("\n2️⃣ Creating Sample Table")
    print("-" * 25)
    
    create_table_sql = """
    CREATE OR REPLACE TABLE PRODUCT_DATA(
        Barcode VARCHAR(13),
        ProductID VARCHAR(6),
        ProductName VARCHAR(40),
        LotNumber VARCHAR(7),
        Quantity INTEGER,
        Exp_Date DATE
    )
    """
    
    sf.execute_query(create_table_sql, fetch=False)
    print("✅ Created PRODUCT_DATA table")

    return True

def insert_sample_data(sf):
    """Insert comprehensive sample product data"""
    print("\n3️⃣ Inserting Sample Data")
    print("-" * 25)

    # Sample product data
    sample_data = [
        ('7501040093135', '000001', 'Beverage A', 'L00123', 100, '2025-11-06'),
        ('7501040093136', '000002', 'Beverage B', 'L00124', 150, '2025-12-20'),
        ('7501040093137', '000003', 'Beverage C', 'L00125', 200, '2025-12-31'),
        ('7501040093138', '000004', 'Beverage D', 'L00126', 250, '2025-12-30'),
        ('7501040093139', '000005', 'Beverage E', 'L00127', 300, '2025-12-21'),
        ('7501040093140', '000006', 'Beverage F', 'L00128', 120, '2025-12-15'),
        ('7501040093141', '000007', 'Beverage G', 'L00129', 180, '2025-12-25'),
        ('7501040093142', '000008', 'Beverage H', 'L00130', 220, '2025-12-18'),
        ('7501040093143', '000009', 'Beverage I', 'L00131', 130, '2025-12-28'),
        ('7501040093144', '000010', 'Beverage J', 'L00132', 160, '2025-12-22')
    ]
    
    insert_sql = """
    INSERT INTO PRODUCT_DATA (
        Barcode, ProductID, ProductName, LotNumber, Quantity, Exp_Date
    ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    for product_data in sample_data:
        sf.execute_query(insert_sql, fetch=False, params=product_data)

    print(f"✅ Inserted {len(sample_data)} product records")


def query_oldest_items(sf):
    """Query to get the 10 oldest items based on expiration date"""
    print("\n🔍 Finding 10 Oldest Items")
    print("-" * 25)
    
    oldest_items_query = """
    SELECT 
        ProductID,
        ProductName,
        Barcode,
        LotNumber,
        Quantity,
        Exp_Date,
        DATEDIFF('day', CURRENT_DATE(), Exp_Date) as days_until_expiration
    FROM PRODUCT_DATA
    ORDER BY Exp_Date ASC
    LIMIT 10
    """
    
    oldest_items_df = sf.query_to_dataframe(oldest_items_query)
    if oldest_items_df is not None:
        print("📦 10 Oldest Items (by expiration date):")
        print(oldest_items_df)
        
        # Additional analysis
        #expiring_soon = oldest_items_df[oldest_items_df['DAYS_UNTIL_EXPIRATION'] <= 30]
        expiring_soon = oldest_items_df[oldest_items_df['days_until_expiration'] <= 30]
        if len(expiring_soon) > 0:
            print(f"\n⚠️  Warning: {len(expiring_soon)} items expire within 30 days!")
            print(expiring_soon[['productname', 'exp_date', 'days_until_expiration']])
    else:
        print("❌ Could not retrieve oldest items data")

def demonstrate_adding_new_data(sf):
    """Demonstrate how to add new data using the class methods"""
    print("\n➕ Adding New Data Demo")
    print("-" * 25)
    
    # Method 1: Add single product using tuple
    print("\n1️⃣ Adding single product (tuple format):")
    single_product = ('7501040093145', '000011', 'Energy Drink A', 'L00133', 75, '2025-11-15')
    sf.add_product_data(single_product)
    
    # Method 2: Add single product using dictionary
    print("\n2️⃣ Adding single product (dictionary format):")
    single_product_dict = {
        'barcode': '7501040093146',
        'product_id': '000012',
        'product_name': 'Sports Drink B',
        'lot_number': 'L00134',
        'quantity': 200,
        'exp_date': '2025-11-20'
    }
    sf.add_product_data(single_product_dict)
    
    # Method 3: Add multiple products using list of tuples
    print("\n3️⃣ Adding multiple products (list of tuples):")
    multiple_products = [
        ('7501040093147', '000013', 'Juice C', 'L00135', 150, '2025-11-25'),
        ('7501040093148', '000014', 'Water D', 'L00136', 300, '2025-12-05'),
        ('7501040093149', '000015', 'Soda E', 'L00137', 180, '2025-11-30')
    ]
    sf.add_product_data(multiple_products)
    
    # Method 4: Add multiple products using list of dictionaries
    print("\n4️⃣ Adding multiple products (list of dictionaries):")
    multiple_products_dict = [
        {
            'barcode': '7501040093150',
            'product_id': '000016',
            'product_name': 'Tea F',
            'lot_number': 'L00138',
            'quantity': 120,
            'exp_date': '2025-12-10'
        },
        {
            'barcode': '7501040093151',
            'product_id': '000017',
            'product_name': 'Coffee G',
            'lot_number': 'L00139',
            'quantity': 90,
            'exp_date': '2025-12-08'
        }
    ]
    sf.add_product_data(multiple_products_dict)
    
    # Method 5: Using the generic add_custom_data method
    print("\n5️⃣ Using generic add_custom_data method:")
    custom_data = {
        'Barcode': '7501040093152',
        'ProductID': '000018',
        'ProductName': 'Smoothie H',
        'LotNumber': 'L00140',
        'Quantity': 65,
        'Exp_Date': '2025-12-12'
    }
    sf.add_custom_data('PRODUCT_DATA', custom_data)
    
    # Verify all additions
    print("\n🔍 Verifying additions - Current product count:")
    count_query = "SELECT COUNT(*) as total_products FROM PRODUCT_DATA"
    result = sf.execute_query(count_query)
    if result:
        print(f"   Total products in database: {result[0][0]}")
    
    # Show the newest products
    print("\n📦 Newest 5 products added:")
    newest_query = """
    SELECT ProductID, ProductName, Quantity, Exp_Date 
    FROM PRODUCT_DATA 
    ORDER BY ProductID DESC 
    LIMIT 5
    """
    newest_df = sf.query_to_dataframe(newest_query)
    if newest_df is not None:
        print(newest_df)

def demonstrate_barcode_search(sf):
    """Demonstrate barcode search functionality"""
    print("\n🔍 Barcode Search Demo")
    print("-" * 25)
    
    # Test 1: Search for an existing barcode
    print("\n1️⃣ Searching for existing barcode:")
    existing_barcode = "7501040093135"  # This should exist from our sample data
    result = sf.check_barcode_exists(existing_barcode)
    
    # Test 2: Search for a non-existing barcode
    print("\n2️⃣ Searching for non-existing barcode:")
    non_existing_barcode = "9999999999999"
    result2 = sf.check_barcode_exists(non_existing_barcode)
    
    # Test 3: Batch search for multiple barcodes
    print("\n3️⃣ Batch search for multiple barcodes:")
    search_barcodes = [
        "7501040093135",  # Should exist
        "7501040093136",  # Should exist
        "7501040093150",  # Should exist (added in previous demo)
        "1111111111111",  # Should NOT exist
        "2222222222222"   # Should NOT exist
    ]
    
    batch_result = sf.search_barcodes(search_barcodes)
    
    # Display found products
    if batch_result['found']:
        print(f"\n✅ Found Products ({len(batch_result['found'])}):")
        for i, product in enumerate(batch_result['found'], 1):
            print(f"   {i}. {product['product_name']} (ID: {product['product_id']})")
            print(f"      Barcode: {product['barcode']}")
            print(f"      Quantity: {product['quantity']}")
            print(f"      Expires in: {product['days_until_expiration']} days")
            print()
    
    # Display not found barcodes
    if batch_result['not_found']:
        print(f"❌ Not Found Barcodes ({len(batch_result['not_found'])}):")
        for barcode in batch_result['not_found']:
            print(f"   • {barcode}")
    
    # Test 4: Advanced search with duplicate prevention
    print("\n4️⃣ Duplicate prevention example:")
    new_product_barcode = "7501040093135"  # Existing barcode
    check_result = sf.check_barcode_exists(new_product_barcode)
    
    if check_result['exists']:
        print(f"⚠️  Warning: Barcode {new_product_barcode} already exists!")
        print("   Cannot add duplicate product. Consider updating existing product instead.")
        
        # Show existing product details
        existing_product = check_result['product_info']
        print(f"   Existing product: {existing_product['product_name']}")
        print(f"   Current quantity: {existing_product['quantity']}")
    else:
        print(f"✅ Barcode {new_product_barcode} is available for new product")
        # Here you could proceed with adding the new product

def demonstrate_product_updates(sf):
    """Demonstrate product update functionality"""
    print("\n🔄 Product Update Demo")
    print("-" * 25)
    
    # Test 1: Update a single field (product name)
    print("\n1️⃣ Updating product name:")
    test_barcode = "7501040093135"  # Should exist from sample data
    
    # Show current product info
    current = sf.check_barcode_exists(test_barcode)
    if current['exists']:
        print(f"   Current name: {current['product_info']['product_name']}")
    
    # Update the product name
    update_result = sf.update_existing_product(
        barcode=test_barcode,
        product_name="Premium Beverage A"
    )
    
    # Test 2: Update multiple fields at once
    print("\n2️⃣ Updating multiple fields:")
    test_barcode2 = "7501040093136"
    
    update_result2 = sf.update_existing_product(
        barcode=test_barcode2,
        product_name="Enhanced Beverage B",
        quantity=175,
        lot_number="L00999"
    )
    
    # Test 3: Update expiration date
    print("\n3️⃣ Updating expiration date:")
    test_barcode3 = "7501040093137"
    
    update_result3 = sf.update_existing_product(
        barcode=test_barcode3,
        exp_date="2026-01-15"
    )
    
    # Test 4: Quantity operations
    print("\n4️⃣ Quantity operations:")
    test_barcode4 = "7501040093138"
    
    # Show current quantity
    current_info = sf.check_barcode_exists(test_barcode4)
    if current_info['exists']:
        print(f"   Current quantity: {current_info['product_info']['quantity']}")
    
    # Add to inventory (received new stock)
    print("\n   📦 Adding 50 units (new stock received):")
    sf.update_product_quantity(test_barcode4, 50, operation='add')
    
    # Subtract from inventory (sales)
    print("\n   📤 Subtracting 25 units (sales):")
    sf.update_product_quantity(test_barcode4, 25, operation='subtract')
    
    # Set exact quantity (inventory correction)
    print("\n   🔧 Setting exact quantity to 300 (inventory correction):")
    sf.update_product_quantity(test_barcode4, 300, operation='set')
    
    # Test 5: Update non-existing product (error handling)
    print("\n5️⃣ Attempting to update non-existing product:")
    fake_barcode = "9999999999999"
    
    error_result = sf.update_existing_product(
        barcode=fake_barcode,
        product_name="This Should Fail"
    )
    
    # Test 6: Batch verification - show all updated products
    print("\n6️⃣ Verification - Updated products summary:")
    verification_query = """
    SELECT 
        Barcode,
        ProductName,
        LotNumber,
        Quantity,
        Exp_Date
    FROM PRODUCT_DATA 
    WHERE Barcode IN ('7501040093135', '7501040093136', '7501040093137', '7501040093138')
    ORDER BY ProductID
    """
    
    verification_df = sf.query_to_dataframe(verification_query)
    if verification_df is not None:
        print("\n📊 Updated Products:")
        print(verification_df)
    
    # Test 7: Advanced update with business logic
    print("\n7️⃣ Advanced update with business logic:")
    test_barcode5 = "7501040093139"
    
    # Check current product
    current_product = sf.check_barcode_exists(test_barcode5)
    if current_product['exists']:
        product_info = current_product['product_info']
        
        # Business logic: Update quantity based on expiration status
        if product_info['days_until_expiration'] < 30:
            print(f"   ⚠️  Product expires in {product_info['days_until_expiration']} days")
            print("   📋 Applying clearance pricing and reducing quantity")
            
            # Update for clearance
            sf.update_existing_product(
                barcode=test_barcode5,
                product_name=f"{product_info['product_name']} - CLEARANCE",
                quantity=int(product_info['quantity'] * 0.7)  # Reduce by 30%
            )
        else:
            print(f"   ✅ Product is fresh ({product_info['days_until_expiration']} days to expiry)")

def cleanup_demo_tables(sf):
    """Clean up demo tables"""
    print("\n🧹 Cleanup")
    print("-" * 15)
    
    cleanup_tables = ['AIRLINE_OPERATIONS', 'AIRLINE_OPERATIONS_ENHANCED']
    
    for table in cleanup_tables:
        try:
            sf.execute_query(f"DROP TABLE IF EXISTS {table}", fetch=False)
            print(f"🗑️  Dropped table: {table}")
        except Exception as e:
            print(f"⚠️  Could not drop {table}: {e}")

def main():
    """Main demonstration function"""
    print("🛫 COMPREHENSIVE SNOWFLAKE API DEMONSTRATION")
    print("=" * 60)
    print("Using configuration from .env file")
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize Snowflake connection
    try:
        sf = SnowflakeConnection()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n📝 Please ensure your .env file contains:")
        print("   SNOWFLAKE_ACCOUNT=your-account")
        print("   SNOWFLAKE_USER=your-username")
        print("   SNOWFLAKE_PASSWORD=your-password")
        print("   SNOWFLAKE_WAREHOUSE=your-warehouse")
        print("   SNOWFLAKE_DATABASE=your-database")
        print("   SNOWFLAKE_SCHEMA=PUBLIC")
        return
    
    # Connect to Snowflake
    if not sf.connect():
        print("❌ Failed to connect to Snowflake. Please check your credentials.")
        return
    
    try:
        # Run all demonstrations
        demonstrate_basic_operations(sf)
        insert_sample_data(sf)
        query_oldest_items(sf)
        demonstrate_adding_new_data(sf)
        demonstrate_barcode_search(sf)
        demonstrate_product_updates(sf)
        #demonstrate_analytics_queries(sf)
        #demonstrate_pandas_integration(sf)
        #demonstrate_data_manipulation(sf)
        #demonstrate_advanced_features(sf)
        
        print("\n✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("\n🎯 What You've Learned:")
        print("   ✅ Environment-based configuration")
        print("   ✅ Connection management") 
        print("   ✅ Table creation and data insertion")
        print("   ✅ Complex analytics queries")
        print("   ✅ Pandas integration")
        print("   ✅ Data manipulation (UPDATE, INSERT)")
        print("   ✅ Advanced SQL features")
        print("   ✅ Real-world airline operations example")
        
        # Ask user if they want to keep or clean up tables
        print("\n🧹 Table Cleanup:")
        keep_tables = input("Keep demo tables for exploration? (y/n): ").lower().strip()
        
        if keep_tables != 'y':
            cleanup_demo_tables(sf)
        else:
            print("📚 Demo tables preserved. You can query them later:")
            print("   • PRODUCT_DATA")
            #print("   • AIRLINE_OPERATIONS_ENHANCED")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        
    finally:
        sf.disconnect()
        print(f"\n🏁 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    
    main()