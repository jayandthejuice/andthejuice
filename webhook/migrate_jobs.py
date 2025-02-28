from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine, MetaData, Table, Column, Unicode, Integer, PickleType, Boolean, Float
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load database URL
POSTGRES_URL = os.getenv("DATABASE_URL")
if not POSTGRES_URL:
    raise ValueError("❌ DATABASE_URL is not set")

# Connect to PostgreSQL
engine = create_engine(POSTGRES_URL)
metadata = MetaData()

# Define the APScheduler jobs table schema manually
jobs_table = Table(
    "apscheduler_jobs", metadata,
    Column("id", Unicode(191), primary_key=True),
    Column("next_run_time", Float(precision=25), index=True, nullable=True),
    Column("job_state", PickleType, nullable=False)
)

# Create the table
metadata.create_all(engine)

print("✅ PostgreSQL Job Store Table Created Successfully!")
