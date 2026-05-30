import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')

FILES = {
    'customers':     'data/raw/customers.csv',
    'subscriptions': 'data/raw/subscriptions.csv',
    'invoices':      'data/raw/invoices.csv',
}

# ─── STEP 1: UPLOAD TO AZURE BLOB STORAGE ─────────────
def upload_to_azure():
    print("\n📤 Uploading CSVs to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    
    for name, filepath in FILES.items():
        blob_name = f"{name}.csv"
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_CONTAINER_NAME, 
            blob=blob_name
        )
        with open(filepath, 'rb') as f:
            blob_client.upload_blob(f, overwrite=True)
        print(f"  ✓ Uploaded {blob_name}")
    
    print("✅ All files uploaded to Azure!")

# ─── STEP 2: LOAD FROM AZURE INTO SNOWFLAKE ───────────
def load_to_snowflake():
    print("\n❄️  Loading data into Snowflake RAW schema...")
    
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema='RAW'
    )
    cursor = conn.cursor()
    
    # Set context
    cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cursor.execute("USE SCHEMA RAW")
    
    for name, filepath in FILES.items():
        print(f"\n  Loading {name}...")
        
        # Read CSV
        df = pd.read_csv(filepath)
        
        # Clean column names — Snowflake prefers uppercase
        df.columns = [col.upper() for col in df.columns]
        
        # Drop table if exists and recreate
        table_name = name.upper()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Write to Snowflake
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            database=SNOWFLAKE_DATABASE,
            schema='RAW',
            auto_create_table=True,
            overwrite=True
        )
        
        if success:
            print(f"  ✓ {table_name}: {nrows} rows loaded")
        else:
            print(f"  ✗ Failed to load {table_name}")
    
    cursor.close()
    conn.close()
    print("\n✅ All tables loaded into Snowflake RAW schema!")

# ─── STEP 3: VERIFY ───────────────────────────────────
def verify_snowflake():
    print("\n🔍 Verifying row counts in Snowflake...")
    
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema='RAW'
    )
    cursor = conn.cursor()
    cursor.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")
    
    for name in FILES.keys():
        table = name.upper()
        cursor.execute(f"SELECT COUNT(*) FROM SAAS_REVENUE_DB.RAW.{table}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table}: {count} rows")
    
    cursor.close()
    conn.close()

# ─── MAIN ─────────────────────────────────────────────
if __name__ == '__main__':
    upload_to_azure()
    load_to_snowflake()
    verify_snowflake()
    print("\n🎉 ETL pipeline complete!")
    