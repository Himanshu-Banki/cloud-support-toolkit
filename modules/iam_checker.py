import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

def policy_allows_admin(policy):
    # Simple heuristic: look for "*" in Action and Resource to detect admin privileges
    statements = policy.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]
    for stmt in statements:
        if stmt.get("Effect") != "Allow":
            continue
        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])
        if not isinstance(actions, list):
            actions = [actions]
        if not isinstance(resources, list):
            resources = [resources]
        if "*" in actions and "*" in resources:
            return True
    return False

def run_check():
    print("\n[INFO] Starting IAM diagnostics...")

    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        iam = session.client("iam")

        # Check root MFA
        try:
            resp = iam.get_account_summary()
            if resp["SummaryMap"].get("AccountMFAEnabled", 0) == 1:
                print("  Root account MFA is enabled.")
            else:
                print("  [WARN] Root account MFA is NOT enabled!")
        except Exception as e:
            print(f"  Could not check root MFA: {e}")

        # Check password policy
        try:
            pw_policy = iam.get_account_password_policy()
            policy = pw_policy["PasswordPolicy"]
            print("  Password policy is set with the following settings:")
            for k, v in policy.items():
                print(f"    - {k}: {v}")
        except iam.exceptions.NoSuchEntityException:
            print("  [WARN] No password policy set. Consider enforcing a strong password policy for your AWS account!")
        except Exception as e:
            print(f"  Could not retrieve password policy: {e}")

        # Get all users
        paginator = iam.get_paginator('list_users')
        ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
        found_users = False

        for page in paginator.paginate():
            users = page['Users']
            for user in users:
                found_users = True
                username = user['UserName']
                print(f"\n  User: {username}")

                # Check inline policies
                inline_policies = iam.list_user_policies(UserName=username)["PolicyNames"]
                if not inline_policies:
                    print("   No inline policies.")
                else:
                    print(f"   Inline policies: {inline_policies}")

                # Check managed policies
                managed_policies = iam.list_attached_user_policies(UserName=username)["AttachedPolicies"]
                managed_policy_names = [p["PolicyName"] for p in managed_policies]
                if managed_policy_names:
                    print(f"   Attached managed policies: {managed_policy_names}")
                else:
                    print("   No managed policies attached.")

                # Warn if any admin policies attached
                if "AdministratorAccess" in managed_policy_names:
                    print("    [WARN] User has AdministratorAccess managed policy attached!")

                # Check access keys
                keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]
                if keys:
                    for key in keys:
                        key_id = key["AccessKeyId"]
                        create_date = key["CreateDate"]
                        age_days = (datetime.now(timezone.utc) - create_date).days
                        print(f"   Access key {key_id} created on {create_date.date()} (age: {age_days} days)")
                        if age_days > 90:
                            print(f"    [WARN] Access key {key_id} is older than 90 days.")
                else:
                    print("   No access keys.")

                # Check if user has console login
                try:
                    login_profile = iam.get_login_profile(UserName=username)
                    has_console_access = True
                except iam.exceptions.NoSuchEntityException:
                    has_console_access = False

                # Check MFA devices
                mfa_devices = iam.list_mfa_devices(UserName=username)["MFADevices"]
                if mfa_devices:
                    print("   MFA device(s) enabled.")
                else:
                    print("   [WARN] No MFA device enabled.")

                # Check last login (can be None if never logged in)
                last_login = user.get("PasswordLastUsed")
                if last_login is None:
                    print("   No console login detected yet.")
                else:
                    days_since_login = (datetime.now(timezone.utc) - last_login).days
                    print(f"   Last console login: {last_login.date()} ({days_since_login} days ago)")
                    if days_since_login > 90:
                        print("    [WARN] Console login older than 90 days.")

                # Warn about users without console login but have active access keys (potential risk)
                if not has_console_access and keys:
                    print("    [WARN] User has no console login but has active access keys - review for security.")

        if not found_users:
            print("  No IAM users found.")

    except Exception as e:
        print(f"[ERROR] Failed to run IAM diagnostics: {e}")
