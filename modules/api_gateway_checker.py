import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting API Gateway diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        client = session.client("apigateway")
        waf_client = session.client("waf-regional")

        apis = client.get_rest_apis(limit=500)["items"]
        if not apis:
            print("  No API Gateways found.")
            return

        print(f"  {len(apis)} REST API(s) found.")

        for api in apis:
            api_id = api["id"]
            name = api["name"]
            created = api["createdDate"]
            print(f"\n  → API: {name} (ID: {api_id}, Created: {created})")

            # Deployment stages
            stages = client.get_stages(restApiId=api_id)["item"]
            if stages:
                print(f"   {len(stages)} stage(s): {[stage['stageName'] for stage in stages]}")
            else:
                print("   [WARN] No deployment stages found.")

            for stage in stages:
                stage_name = stage["stageName"]

                # Logging check
                logging_level = stage.get("methodSettings", {}).get("*/GET", {}).get("loggingLevel", "OFF")
                print(f"   Logging level for stage '{stage_name}': {logging_level}")

                # Throttling check
                throttle = stage.get("methodSettings", {}).get("*/GET", {}).get("throttlingRateLimit")
                if throttle:
                    print(f"   Throttling rate limit for GET: {throttle}")
                else:
                    print("   No throttling configured.")

            # Resource-level check for authorizers & API key requirements
            resources = client.get_resources(restApiId=api_id)["items"]
            for resource in resources:
                for method in resource.get("resourceMethods", {}):
                    method_info = client.get_method(
                        restApiId=api_id,
                        resourceId=resource["id"],
                        httpMethod=method
                    )
                    auth_type = method_info.get("authorizationType", "NONE")
                    api_key_required = method_info.get("apiKeyRequired", False)
                    print(f"   Method {method} on {resource['path']} → Auth: {auth_type}, API Key Required: {api_key_required}")

            # Usage plans (linked to stages)
            usage_plans = client.get_usage_plans()["items"]
            found = False
            for plan in usage_plans:
                for api_stage in plan.get("apiStages", []):
                    if api_stage["apiId"] == api_id:
                        found = True
                        print(f"   Usage Plan: {plan['name']} → Throttle: {plan.get('throttle')}, Quota: {plan.get('quota')}")
            if not found:
                print("   No usage plan linked.")

            # WAF check
            wafs = waf_client.list_web_acls()["WebACLs"]
            associated_waf = None
            for waf in wafs:
                resources = waf_client.list_resources_for_web_acl(
                    WebACLId=waf["WebACLId"],
                    ResourceType="API_GATEWAY"
                )
                if any(api_id in arn for arn in resources.get("ResourceArns", [])):
                    associated_waf = waf["Name"]
                    break

            if associated_waf:
                print(f"   WAF protection enabled: {associated_waf}")
            else:
                print("   [WARN] No WAF protection associated.")

    except Exception as e:
        print(f"[ERROR] Failed to run API Gateway diagnostics: {e}")
