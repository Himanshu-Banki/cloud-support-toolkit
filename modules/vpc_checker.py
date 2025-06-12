# modules/vpc_checker.py
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_check():
    print("\n[INFO] Starting VPC diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        ec2 = session.client("ec2")

        vpcs = ec2.describe_vpcs()["Vpcs"]
        if not vpcs:
            print("  No VPCs found in the region.")
            return

        print(f"  {len(vpcs)} VPC(s) found.")

        # Get all IGWs for quick lookup
        igws = ec2.describe_internet_gateways()["InternetGateways"]
        igw_map = {}
        for igw in igws:
            for attachment in igw.get("Attachments", []):
                if attachment.get("VpcId"):
                    igw_map[attachment["VpcId"]] = igw["InternetGatewayId"]

        # Get all flow logs for quick lookup
        flow_logs = ec2.describe_flow_logs()["FlowLogs"]
        flow_logs_vpc_ids = {fl["ResourceId"] for fl in flow_logs if fl["ResourceType"] == "VPC"}

        for vpc in vpcs:
            vpc_id = vpc["VpcId"]
            cidr_block = vpc["CidrBlock"]
            is_default = vpc.get("IsDefault", False)

            print(f"\n  VPC ID: {vpc_id}")
            print(f"   CIDR Block: {cidr_block}")
            print(f"   Default VPC: {'Yes' if is_default else 'No'}")

            # Internet Gateway attached?
            if vpc_id in igw_map:
                print(f"   Internet Gateway attached: {igw_map[vpc_id]}")
            else:
                print("   No Internet Gateway attached.")

            # Flow logs enabled?
            if vpc_id in flow_logs_vpc_ids:
                print("   Flow Logs: ENABLED")
            else:
                print("   Flow Logs: NOT enabled")

            # Subnets info
            subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
            print(f"   {len(subnets)} subnet(s) found:")
            for subnet in subnets:
                subnet_id = subnet["SubnetId"]
                subnet_cidr = subnet["CidrBlock"]
                az = subnet["AvailabilityZone"]
                public = subnet.get("MapPublicIpOnLaunch", False)
                print(f"     - Subnet {subnet_id} (AZ: {az}, CIDR: {subnet_cidr}, Public IP on launch: {public})")

            # Route tables
            rts = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["RouteTables"]
            print(f"   {len(rts)} route table(s) found:")
            for rt in rts:
                rt_id = rt["RouteTableId"]
                main = any(assoc.get("Main") for assoc in rt.get("Associations", []))
                print(f"     - Route Table {rt_id} {'(Main)' if main else ''}:")
                for route in rt.get("Routes", []):
                    dest = route.get("DestinationCidrBlock", route.get("DestinationIpv6CidrBlock", ""))
                    target = (
                        route.get("GatewayId")
                        or route.get("NatGatewayId")
                        or route.get("InstanceId")
                        or route.get("VpcPeeringConnectionId")
                        or "local"
                    )
                    print(f"       → Destination: {dest}  Target: {target}")

            # Security groups wide open ingress check
            sgs = ec2.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["SecurityGroups"]
            open_ports = []
            for sg in sgs:
                sg_id = sg["GroupId"]
                for perm in sg.get("IpPermissions", []):
                    for ip_range in perm.get("IpRanges", []):
                        cidr = ip_range.get("CidrIp")
                        if cidr == "0.0.0.0/0":
                            from_port = perm.get("FromPort", "All")
                            to_port = perm.get("ToPort", "All")
                            open_ports.append((sg_id, from_port, to_port))
            if open_ports:
                print("   [WARN] Security Groups with wide open ingress (0.0.0.0/0):")
                for sg_id, from_port, to_port in open_ports:
                    print(f"     - SG {sg_id} open ports: {from_port} - {to_port}")
            else:
                print("   No Security Groups with wide open ingress detected.")

    except Exception as e:
        print(f"[ERROR] Failed to run VPC diagnostics: {e}")
        