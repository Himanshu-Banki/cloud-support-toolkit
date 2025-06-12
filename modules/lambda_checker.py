import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting Lambda diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        lambda_client = session.client("lambda")

        paginator = lambda_client.get_paginator("list_functions")
        page_iterator = paginator.paginate()

        function_count = 0
        for page in page_iterator:
            for fn in page["Functions"]:
                function_count += 1
                name = fn["FunctionName"]
                runtime = fn.get("Runtime", "Unknown")
                timeout = fn["Timeout"]
                memory = fn["MemorySize"]
                last_modified = fn["LastModified"]
                role = fn["Role"]
                env_vars = fn.get("Environment", {}).get("Variables", {})
                vpc_config = fn.get("VpcConfig", {})
                dlq = fn.get("DeadLetterConfig", {}).get("TargetArn", "None")
                signing_config = fn.get("CodeSigningConfigArn", None)

                print(f"\n  [Function] {name}")
                print(f"   Runtime: {runtime} | Timeout: {timeout}s | Memory: {memory}MB")
                print(f"   Last Modified: {last_modified}")
                print(f"   IAM Role: {role}")
                
                if "AWS_ACCESS_KEY_ID" in str(env_vars) or "SECRET" in str(env_vars):
                    print("   [WARN] Potential secret in environment variables.")
                else:
                    print(f"   Env Vars: {len(env_vars)} variable(s) configured.")

                if vpc_config.get("VpcId"):
                    print(f"   VPC Configured: Yes (VPC ID: {vpc_config['VpcId']})")
                else:
                    print("   VPC Configured: No")

                if dlq != "None":
                    print(f"   Dead Letter Queue: {dlq}")
                else:
                    print("   DLQ: Not configured")

                # Concurrency settings
                try:
                    concurrency = lambda_client.get_function_concurrency(FunctionName=name)
                    reserved = concurrency.get("ReservedConcurrentExecutions")
                    print(f"   Reserved Concurrency: {reserved if reserved is not None else 'Not set'}")
                except:
                    print("   Reserved Concurrency: Not set")

                if signing_config:
                    print("   Code Signing Config: ENABLED")
                else:
                    print("   Code Signing Config: Not enabled")

                # Triggers
                ev_sources = lambda_client.list_event_source_mappings(FunctionName=name).get("EventSourceMappings", [])
                if ev_sources:
                    for src in ev_sources:
                        src_arn = src.get("EventSourceArn", "Unknown")
                        print(f"   Trigger: {src_arn}")
                else:
                    print("   Triggers: None found")

        if function_count == 0:
            print("  No Lambda functions found.")

    except Exception as e:
        print(f"[ERROR] Failed to run Lambda diagnostics: {e}")
