import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting CloudTrail diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        ct = session.client("cloudtrail")
        trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])

        if not trails:
            print("  [WARN] No CloudTrails found.")
            return

        print(f"  Found {len(trails)} trail(s).")

        for trail in trails:
            name = trail.get("Name")
            home_region = trail.get("HomeRegion")
            s3_bucket = trail.get("S3BucketName")
            is_multi_region = trail.get("IsMultiRegionTrail", False)
            log_validation = trail.get("LogFileValidationEnabled", False)
            cloudwatch_logs_log_group = trail.get("CloudWatchLogsLogGroupArn")
            kms_key = trail.get("KmsKeyId")

            print(f"\n  Trail: {name}")
            print(f"   Home Region: {home_region}")
            print(f"   Multi-region: {'Yes' if is_multi_region else 'No'}")
            print(f"   Log File Validation: {'Enabled' if log_validation else 'Disabled'}")
            print(f"   Logging to S3: {s3_bucket}")
            print(f"   CloudWatch Logs Integration: {'ENABLED' if cloudwatch_logs_log_group else 'NOT enabled'}")
            print(f"   KMS Encryption: {'Enabled' if kms_key else 'Not Enabled'}")

            # Check insight selectors
            try:
                insights = ct.get_insight_selectors(TrailName=name).get("InsightSelectors", [])
                if insights:
                    insight_types = [sel.get("InsightType") for sel in insights]
                    print(f"   Insight Selectors: {', '.join(insight_types)}")
                else:
                    print("   Insight Selectors: None")
            except ct.exceptions.InsightNotEnabledException:
                print("   Insight Selectors: Not enabled")

            # Check event selectors
            selectors = ct.get_event_selectors(TrailName=name).get("EventSelectors", [])
            if not selectors:
                print("   [WARN] No event selectors configured.")
            for sel in selectors:
                include_management = sel.get("IncludeManagementEvents", True)
                read_write_type = sel.get("ReadWriteType", "All")
                data_resources = sel.get("DataResources", [])
                print(f"   Management Events: {'Included' if include_management else 'Not included'}")
                print(f"   Read/Write Type: {read_write_type}")
                if data_resources:
                    for res in data_resources:
                        print(f"     - {res.get('Type')}: {', '.join(res.get('Values', []))}")
                else:
                    print("     - No specific data resources tracked.")

    except Exception as e:
        print(f"[ERROR] Failed to run CloudTrail diagnostics: {e}")
