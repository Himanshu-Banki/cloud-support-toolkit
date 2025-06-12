import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting EKS diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        eks = session.client("eks")

        clusters = eks.list_clusters().get("clusters", [])
        if not clusters:
            print("  No EKS clusters found.")
            return

        print(f"  Found {len(clusters)} cluster(s).")

        for cluster_name in clusters:
            print(f"\n  Cluster: {cluster_name}")
            desc = eks.describe_cluster(name=cluster_name)["cluster"]

            status = desc.get("status")
            version = desc.get("version")
            endpoint = desc.get("endpoint")
            logging = desc.get("logging", {}).get("clusterLogging", [])
            log_types_enabled = [l["types"] for l in logging if l.get("enabled")]

            print(f"   → Status: {status}")
            print(f"   → Kubernetes Version: {version}")
            print(f"   → Endpoint: {endpoint}")

            if log_types_enabled:
                print(f"   → Logging Enabled: {', '.join([t for sublist in log_types_enabled for t in sublist])}")
            else:
                print("   → Logging: Not enabled")

            # IAM role
            role_arn = desc.get("roleArn")
            print(f"   → IAM Role: {role_arn if role_arn else 'Not Configured'}")

            # VPC config
            vpc_config = desc.get("resourcesVpcConfig", {})
            subnet_ids = vpc_config.get("subnetIds", [])
            sg_ids = vpc_config.get("securityGroupIds", [])
            print(f"   → VPC Subnets: {', '.join(subnet_ids)}")
            print(f"   → Security Groups: {', '.join(sg_ids)}")

    except Exception as e:
        print(f"[ERROR] Failed to run EKS diagnostics: {e}")
