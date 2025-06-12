# modules/rds_checker.py
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting RDS diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        rds = session.client("rds")
        instances = rds.describe_db_instances().get("DBInstances", [])

        if not instances:
            print("  No RDS instances found.")
            return

        print(f"  {len(instances)} RDS instance(s) found.")

        for db in instances:
            db_id = db["DBInstanceIdentifier"]
            status = db["DBInstanceStatus"]
            engine = db["Engine"]
            print(f"\n  Instance: {db_id}")
            print(f"   Status: {status}")
            print(f"   Engine: {engine}")

            # Encryption check
            if db.get("StorageEncrypted"):
                print("   Storage Encryption: ENABLED")
            else:
                print("   [WARN] Storage Encryption: DISABLED")

            # Public accessibility
            if db.get("PubliclyAccessible"):
                print("   [WARN] Publicly Accessible: YES")
            else:
                print("   Publicly Accessible: NO")

            # Multi-AZ
            if db.get("MultiAZ"):
                print("   Multi-AZ Deployment: ENABLED")
            else:
                print("   [INFO] Multi-AZ Deployment: DISABLED")

            # Backup retention
            retention = db.get("BackupRetentionPeriod", 0)
            print(f"   Backup Retention: {retention} day(s)")

            # Auto minor version upgrade
            if db.get("AutoMinorVersionUpgrade"):
                print("   Auto Minor Version Upgrade: ENABLED")
            else:
                print("   Auto Minor Version Upgrade: DISABLED")

            # Deletion protection
            if db.get("DeletionProtection"):
                print("   Deletion Protection: ENABLED")
            else:
                print("   [WARN] Deletion Protection: DISABLED")

            # Monitoring interval
            interval = db.get("MonitoringInterval", 0)
            if interval >= 1:
                print(f"   Enhanced Monitoring Interval: {interval} seconds")
            else:
                print("   Enhanced Monitoring: DISABLED")

    except Exception as e:
        print(f"[ERROR] Failed to run RDS diagnostics: {e}")
