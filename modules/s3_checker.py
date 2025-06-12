import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("[INFO] Starting S3 diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        s3 = session.client("s3")
        buckets = s3.list_buckets()["Buckets"]

        if not buckets:
            print("[WARN] No buckets found.")
            return

        print(f"[INFO] {len(buckets)} bucket(s) found.")

        for bucket in buckets:
            name = bucket["Name"]
            print(f"\n[INFO] Checking bucket: {name}")

            # Public access block
            try:
                pab = s3.get_public_access_block(Bucket=name)
                config = pab["PublicAccessBlockConfiguration"]

                if all(config.values()):
                    print("   Public access is fully blocked.")
                else:
                    print("   Public access is NOT fully blocked!")
                    print(f"     → BlockPublicAcls: {config['BlockPublicAcls']}")
                    print(f"     → IgnorePublicAcls: {config['IgnorePublicAcls']}")
                    print(f"     → BlockPublicPolicy: {config['BlockPublicPolicy']}")
                    print(f"     → RestrictPublicBuckets: {config['RestrictPublicBuckets']}")

            except s3.exceptions.ClientError as e:
                print(f"   Could not retrieve public access settings: {e.response['Error']['Message']}")

            # Default encryption check
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                rules = enc["ServerSideEncryptionConfiguration"]["Rules"]
                algo = rules[0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
                print(f"   Default encryption is enabled ({algo}).")
            except s3.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                    print("   Default encryption is NOT enabled!")
                else:
                    print(f"   Could not retrieve encryption settings: {e.response['Error']['Message']}")

            # Bucket policy check
            try:
                policy_str = s3.get_bucket_policy(Bucket=name)['Policy']
                policy = json.loads(policy_str)

                public_access_found = False
                for statement in policy.get("Statement", []):
                    principal = statement.get("Principal", {})
                    effect = statement.get("Effect", "")

                    if effect.lower() == "allow" and (principal == "*" or principal == {"AWS": "*"}):
                        public_access_found = True
                        print("  [WARNING] Bucket policy allows public access!")
                        print(f"   → Statement ID: {statement.get('Sid', 'N/A')}")
                        break

                if not public_access_found:
                    print("  Bucket policy does not allow public access.")

            except s3.exceptions.NoSuchBucketPolicy:
                print("  No bucket policy found.")
            except s3.exceptions.ClientError as e:
                print(f"  Could not retrieve bucket policy: {e.response['Error']['Message']}")

            # 🔍 Versioning check
            try:
                versioning = s3.get_bucket_versioning(Bucket=name)
                status = versioning.get("Status", "Disabled")
                print(f"   Versioning status: {status}")
            except s3.exceptions.ClientError as e:
                print(f"   Could not retrieve versioning info: {e.response['Error']['Message']}")
                            # Lifecycle configuration check
            try:
                lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=name)
                rules = lifecycle.get("Rules", [])
                if rules:
                    print(f"   {len(rules)} lifecycle rule(s) configured:")
                    for idx, rule in enumerate(rules, start=1):
                        status = rule.get("Status", "Unknown")
                        action = "Expiration" if "Expiration" in rule else "Transition"
                        print(f"     → Rule {idx}: {action}, Status: {status}")
                else:
                    print("   No lifecycle rules configured.")
            except s3.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration":
                    print("   No lifecycle rules configured.")
                else:
                    print(f"   Could not retrieve lifecycle configuration: {e.response['Error']['Message']}")

    except Exception as e:
        print(f"[ERROR] Failed to run S3 diagnostics: {e}")
