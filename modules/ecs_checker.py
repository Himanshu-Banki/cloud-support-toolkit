import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting ECS diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        ecs = session.client("ecs")

        clusters_arns = ecs.list_clusters().get("clusterArns", [])
        if not clusters_arns:
            print("  No ECS clusters found.")
            return

        print(f"  Found {len(clusters_arns)} cluster(s).")

        for cluster_arn in clusters_arns:
            cluster = ecs.describe_clusters(clusters=[cluster_arn])["clusters"][0]
            cluster_name = cluster["clusterName"]
            print(f"\n  Cluster: {cluster_name}")
            print(f"   → Status: {cluster['status']}, Active Services: {cluster['activeServicesCount']}, Running Tasks: {cluster['runningTasksCount']}")

            # List services
            service_arns = ecs.list_services(cluster=cluster_arn).get("serviceArns", [])
            if not service_arns:
                print("   No services found in this cluster.")
                continue

            services = ecs.describe_services(cluster=cluster_arn, services=service_arns).get("services", [])
            for service in services:
                name = service["serviceName"]
                desired = service["desiredCount"]
                running = service["runningCount"]
                launch_type = service.get("launchType", "Unknown")
                print(f"   - Service: {name}, Desired: {desired}, Running: {running}, Launch Type: {launch_type}")

            # List task definitions used by services
            for service in services:
                task_def = service.get("taskDefinition")
                if task_def:
                    td_desc = ecs.describe_task_definition(taskDefinition=task_def)
                    container_defs = td_desc["taskDefinition"]["containerDefinitions"]
                    print(f"     Task Definition: {task_def.split('/')[-1]}")
                    for container in container_defs:
                        print(f"       → Container: {container['name']}, Image: {container['image']}")

    except Exception as e:
        print(f"[ERROR] Failed to run ECS diagnostics: {e}")
