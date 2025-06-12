import boto3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting EBS diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        ec2 = session.client("ec2")

        volumes = ec2.describe_volumes()["Volumes"]
        snapshots = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]

        snapshot_map = {}
        for snap in snapshots:
            volume_id = snap.get("VolumeId")
            if volume_id:
                if volume_id not in snapshot_map:
                    snapshot_map[volume_id] = []
                snapshot_map[volume_id].append(snap)

        print(f"  {len(volumes)} volume(s) found.")

        for vol in volumes:
            vol_id = vol["VolumeId"]
            state = vol["State"]
            vol_type = vol["VolumeType"]
            encrypted = vol["Encrypted"]
            attachments = vol.get("Attachments", [])

            print(f"\n  Volume ID: {vol_id}")
            print(f"   State: {state}")
            print(f"   Type: {vol_type}")
            print(f"   Encrypted: {'Yes' if encrypted else 'No'}")

            if not attachments:
                print("   [WARN] Volume is unattached (orphaned).")

            # Snapshot check
            recent_snap = False
            if vol_id in snapshot_map:
                for snap in snapshot_map[vol_id]:
                    start_time = snap["StartTime"]
                    if start_time > datetime.utcnow() - timedelta(days=7):
                        recent_snap = True
                        break
            if not recent_snap:
                print("   [WARN] No recent snapshot in last 7 days.")

    except Exception as e:
        print(f"[ERROR] Failed to run EBS diagnostics: {e}")
