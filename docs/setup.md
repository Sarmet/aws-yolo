# Setup Guide

## Prerequisites

- Python 3.8+
- AWS Account (for SageMaker training)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/USERNAME/REPO.git
cd aws-yolo
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## AWS Configuration

### Configure AWS CLI

```bash
aws configure
```

Provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `eu-central-1`)
- Output format: `json`

### Verify AWS Connection

```bash
aws s3 ls
```

## Dataset Setup

Your dataset should follow the YOLO format:

```
datasets/ppe_balanced/
├── train/
│   ├── images/
│   └── labels/
└── valid/
    ├── images/
    └── labels/
```

See [Dataset Preparation](training/dataset.md) for more details.

## Next Steps

- [Start Local Training](local-training.md)
- [Configure SageMaker](sagemaker/configuration.md)
