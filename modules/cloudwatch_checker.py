import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def run_check():
    print("\n[INFO] Starting CloudWatch diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        logs = session.client("logs")
        cw = session.client("cloudwatch")
        
        # --- Log Groups ---
        log_groups = logs.describe_log_groups(limit=50).get("logGroups", [])
        print(f"  Found {len(log_groups)} log group(s).")

        for group in log_groups:
            name = group["logGroupName"]
            retention = group.get("retentionInDays", "Never Expire")
            kms = group.get("kmsKeyId", None)
            print(f"\n  Log Group: {name}")
            print(f"   Retention: {retention} days")
            print(f"   KMS Encryption: {'ENABLED' if kms else 'Not Enabled'}")

            streams = logs.describe_log_streams(logGroupName=name, orderBy="LastEventTime", descending=True).get("logStreams", [])
            if streams:
                latest = streams[0].get("lastEventTimestamp")
                if latest:
                    last_time = datetime.fromtimestamp(latest / 1000, tz=timezone.utc)
                    print(f"   Latest Log Event: {last_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   Stream Count: {len(streams)}")
            else:
                print("   No log streams found.")

        # --- Alarms ---
        alarms = cw.describe_alarms()
        total_alarms = len(alarms.get("MetricAlarms", []))
        alarm_states = {"OK": 0, "ALARM": 0, "INSUFFICIENT_DATA": 0}
        for alarm in alarms.get("MetricAlarms", []):
            state = alarm.get("StateValue")
            if state in alarm_states:
                alarm_states[state] += 1

        print("\n  CloudWatch Alarms:")
        print(f"   Total: {total_alarms}")
        for state, count in alarm_states.items():
            print(f"   {state}: {count}")

        # --- Dashboards ---
        dashboards = cw.list_dashboards().get("DashboardEntries", [])
        print(f"\n  Found {len(dashboards)} dashboard(s).")
        for dash in dashboards:
            print(f"   - {dash.get('DashboardName')}")

        # --- Metric Filters ---
        print("\n  Security-relevant Metric Filters:")
        for group in log_groups:
            name = group["logGroupName"]
            filters = logs.describe_metric_filters(logGroupName=name).get("metricFilters", [])
            for f in filters:
                pattern = f.get("filterPattern", "")
                if any(keyword in pattern for keyword in ["Unauthorized", "AccessDenied", "LoginFail"]):
                    print(f"   - {name}: {pattern}")

    except Exception as e:
        print(f"[ERROR] Failed to run CloudWatch diagnostics: {e}")
