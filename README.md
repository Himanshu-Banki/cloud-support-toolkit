# Cloud Support Toolkit ☁️🔧

A lightweight cloud diagnostics and support automation toolkit built with Python and AWS SDK (Boto3). Designed to help businesses and cloud teams get quick visibility and resolution across AWS services.

## 🚀 Features

- S3 bucket diagnostics (public access check, encryption, lifecycle rules)
- EC2 instance scanner (status, missing tags, insecure ports)
- Auto-generated reports
- Modular and extensible structure

## 🛠️ Technologies

- Python 3.x
- AWS Boto3 SDK
- Logging & argparse
- Future scope: Terraform integration, SNS/SES alerts

## 📁 Structure

cloud-support-toolkit/
│
├── modules/ # All diagnostic modules (S3, EC2, etc.)
├── utils/ # Logging, shared utilities
├── main.py # Entry script
├── requirements.txt # Dependencies
└── .env # AWS credentials (ignored by git)

## 📅 Development Timeline (15 Days)

**Week 1:**
- Day 1–2: Project setup, S3 checker
- Day 3–5: EC2 checker, Logging, .env config

**Week 2:**
- Day 6–9: Reports, CLI integration, utils
- Day 10–12: Testing + Error handling
- Day 13–15: Polish, deploy, demo video

## 🤝 Contributing

PRs welcome! Or fork it and customize it for your team.

## 📜 License

MIT License
