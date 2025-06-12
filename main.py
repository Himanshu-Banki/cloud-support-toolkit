from modules import (
    ec2_checker,
    s3_checker,
    lambda_checker,
    rds_checker,
    dynamodb_checker,
    ebs_checker,
    cloudtrail_checker,
    cloudwatch_checker,
    api_gateway_checker,
    vpc_checker,
    iam_checker,
    ecs_checker,
    eks_checker
)

def main():
    while True:
        print("\nCloud Support Toolkit - AWS Diagnostics")
        print("========================================")
        print("Select a service to run diagnostics:")
        print(" 1. EC2")
        print(" 2. S3")
        print(" 3. Lambda")
        print(" 4. RDS")
        print(" 5. DynamoDB")
        print(" 6. EBS")
        print(" 7. CloudTrail")
        print(" 8. CloudWatch")
        print(" 9. API Gateway")
        print("10. VPC")
        print("11. IAM")
        print("12. ECS")
        print("13. EKS")
        print("14. Run ALL")
        print(" 0. Exit")

        choice = input("\nEnter your choice (0-14): ").strip()

        options = {
            "1": ec2_checker.run_check,
            "2": s3_checker.run_check,
            "3": lambda_checker.run_check,
            "4": rds_checker.run_check,
            "5": dynamodb_checker.run_check,
            "6": ebs_checker.run_check,
            "7": cloudtrail_checker.run_check,
            "8": cloudwatch_checker.run_check,
            "9": api_gateway_checker.run_check,
            "10": vpc_checker.run_check,
            "11": iam_checker.run_check,
            "12": ecs_checker.run_check,
            "13": eks_checker.run_check
        }

        if choice == "0":
            print("Exiting... Goodbye!")
            break
        elif choice == "14":
            for check in options.values():
                check()
        elif choice in options:
            options[choice]()
        else:
            print("[ERROR] Invalid choice. Please select a number between 0 and 14.")

if __name__ == "__main__":
    main()
exit
