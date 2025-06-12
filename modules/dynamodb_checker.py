import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting DynamoDB diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        dynamodb = session.client("dynamodb")

        tables = dynamodb.list_tables().get("TableNames", [])
        if not tables:
            print("  No DynamoDB tables found.")
            return

        print(f"  {len(tables)} table(s) found.")

        for table_name in tables:
            print(f"\n  [TABLE] {table_name}")
            table_info = dynamodb.describe_table(TableName=table_name)["Table"]

            # Table status
            status = table_info["TableStatus"]
            print(f"   → Status: {status}")

            # Billing mode
            billing_mode = table_info.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
            print(f"   → Billing Mode: {billing_mode}")

            # Auto-scaling
            if billing_mode == "PROVISIONED":
                autoscaling = session.client("application-autoscaling")
                scalable_targets = autoscaling.describe_scalable_targets(
                    ServiceNamespace="dynamodb",
                    ResourceIds=[f"table/{table_name}"],
                ).get("ScalableTargets", [])
                if scalable_targets:
                    print("   → Auto-scaling: ENABLED")
                else:
                    print("   → Auto-scaling: NOT enabled")

            # Encryption
            encryption = table_info.get("SSEDescription", {}).get("Status", "DISABLED")
            print(f"   → Encryption at Rest: {encryption}")

            # PITR
            pitr = dynamodb.describe_continuous_backups(TableName=table_name)["ContinuousBackupsDescription"]
            pitr_status = pitr.get("PointInTimeRecoveryDescription", {}).get("PointInTimeRecoveryStatus", "DISABLED")
            print(f"   → Point-in-Time Recovery: {pitr_status}")

            # Streams
            stream_spec = table_info.get("StreamSpecification", {})
            stream_enabled = stream_spec.get("StreamEnabled", False)
            print(f"   → Streams Enabled: {'Yes' if stream_enabled else 'No'}")

            # TTL
            ttl = dynamodb.describe_time_to_live(TableName=table_name).get("TimeToLiveDescription", {})
            ttl_status = ttl.get("TimeToLiveStatus", "DISABLED")
            print(f"   → TTL: {ttl_status}")

            # Global Table (replication)
            replicas = table_info.get("Replicas", [])
            if replicas:
                regions = [rep["RegionName"] for rep in replicas]
                print(f"   → Global Table Replication: {', '.join(regions)}")
            else:
                print("   → Global Table Replication: Not configured")

    except Exception as e:
        print(f"[ERROR] Failed to run DynamoDB diagnostics: {e}")
