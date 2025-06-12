import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def check_tags(instance):
    tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
    if "Name" not in tags:
        print("   [WARN] Instance missing 'Name' tag")


def check_security_groups(ec2, instance):
    for sg in instance["SecurityGroups"]:
        sg_id = sg["GroupId"]
        sg_data = ec2.describe_security_groups(GroupIds=[sg_id])
        for perm in sg_data["SecurityGroups"][0]["IpPermissions"]:
            for ip_range in perm.get("IpRanges", []):
                cidr = ip_range.get("CidrIp")
                if cidr == "0.0.0.0/0":
                    port = perm.get("FromPort")
                    if port in [22, 3389]:
                        print(f"   [WARN] Port {port} open to world in SG {sg_id}")


def check_volume_encryption(ec2, instance):
    for mapping in instance.get("BlockDeviceMappings", []):
        ebs = mapping.get("Ebs", {})
        volume_id = ebs.get("VolumeId")
        if volume_id:
            volume = ec2.describe_volumes(VolumeIds=[volume_id])["Volumes"][0]
            if not volume.get("Encrypted", False):
                print(f"   [WARN] Volume {volume_id} is not encrypted")


def check_monitoring(instance):
    monitoring = instance.get("Monitoring", {})
    if not monitoring.get("State") == "enabled":
        print("   [INFO] Detailed monitoring is NOT enabled")


def run_check():
    print("\n[INFO] Starting EC2 diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        ec2 = session.client("ec2")
        instances = ec2.describe_instances()

        found = False

        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                found = True
                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]

                print(f"\n[INFO] Instance: {instance_id}")
                print(f"   State: {state}")

                check_tags(instance)
                check_security_groups(ec2, instance)
                check_volume_encryption(ec2, instance)
                check_monitoring(instance)

        if not found:
            print("[INFO] No EC2 instances found.")

    except Exception as e:
        print(f"[ERROR] Failed to run EC2 diagnostics: {e}")
