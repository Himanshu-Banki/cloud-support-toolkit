# Cloud Support Toolkit

A lightweight, Python-based command-line tool to automate health and compliance checks across core AWS services.  
Built to help DevOps, SysOps, and Cloud Engineers quickly diagnose misconfigurations, security gaps, and operational issues  without needing to log in to the AWS console.

---

## 🚀 Features

- ✅ Modular diagnostics for major AWS services:
  - EC2, S3, Lambda, RDS, DynamoDB  
  - IAM, VPC, API Gateway, CloudTrail, CloudWatch  
  - EBS, ECS, EKS
- ✅ Detects common issues: public S3 buckets, unencrypted volumes, disabled logging, and more
- ✅ CLI menu to run individual or full scans
- ✅ Easily extendable with new service checkers
- ✅ Built using `boto3`, `python-dotenv`, and Python scripting best practices

---

## 📂 Project Structure

cloud-support-toolkit/
├── main.py # Central menu/runner
├── requirements.txt # Python dependencies
├── .env.example # Sample AWS credentials format
├── service_checks/ # All individual AWS service checkers
│ ├── ec2_checker.py
│ ├── s3_checker.py
│ └── ...

yaml
Copy
Edit

---

## ⚙️ Installation & Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cloud-support-toolkit.git
   cd cloud-support-toolkit
2. **Install dependencies:**
pip install -r requirements.txt

3. **Set up environment variables:**
Create a .env file in the root directory:
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
AWS_DEFAULT_REGION=us-east-1

4. **Run the tool:**
python main.py

📌 **Requirements**
Python 3.7+
AWS IAM User with read-only or diagnostic permissions
boto3, python-dotenv

📖 License
This project is licensed under the MIT License.
Feel free to use, modify, or extend the toolkit in your own projects!

🙌 Contributing
Pull requests are welcome!
If you'd like to add support for a new AWS service or improve existing diagnostics, feel free to open an issue or PR.

🤝 Connect
Built with curiosity and purpose by Himanshu Singh
🔗 LinkedIn : www.linkedin.com/in/himanshu-singh-0b886b20a
Feedback, suggestions, and collaborations are always welcome!
