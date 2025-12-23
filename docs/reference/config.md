# Configuration Files Reference

## Dataset Configuration

### `data_balanced.yaml`

Complete dataset configuration for training.

```yaml
# Dataset root path
path: ./datasets/ppe_balanced

# Training and validation paths (relative to 'path')
train: train/images
val: valid/images

# Number of classes
nc: 4

# Class names
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

**Fields:**
- `path`: Root directory of dataset
- `train`: Training images directory
- `val`: Validation images directory
- `nc`: Number of object classes
- `names`: List of class names (must match label indices)

### `data_subset.yaml`

Subset configuration for quick testing.

```yaml
path: ./datasets/ppe_balanced

# Point to subset text files instead of directories
train: train_subset.txt
val: val_subset.txt

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

**Subset files format:**
```
train/images/image1.jpg
train/images/image2.jpg
train/images/image3.jpg
...
```

## SageMaker Configuration

### `training_job_config.json`

SageMaker training job parameters.

```json
{
  "job_name": "yolo11-ppe-training",
  "role_arn": "arn:aws:iam::123456789012:role/SageMakerRole",
  
  "instance_type": "ml.g4dn.2xlarge",
  "instance_count": 1,
  "volume_size": 50,
  
  "max_run": 86400,
  "use_spot_instances": true,
  "max_wait": 90000,
  
  "hyperparameters": {
    "epochs": "50",
    "batch": "16",
    "imgsz": "640",
    "data": "data_balanced.yaml",
    "patience": "10"
  },
  
  "input_data": {
    "training": {
      "s3_uri": "s3://your-bucket/datasets/ppe_balanced/",
      "content_type": "application/x-directory"
    }
  },
  
  "output_data": {
    "s3_uri": "s3://your-bucket/output/"
  },
  
  "vpc_config": {
    "security_group_ids": [],
    "subnets": []
  },
  
  "tags": [
    {
      "Key": "Project",
      "Value": "YOLO-PPE"
    }
  ]
}
```

**Key fields:**

#### Job Configuration
- `job_name`: Unique training job name
- `role_arn`: IAM role with SageMaker permissions

#### Instance Configuration
- `instance_type`: EC2 instance type (e.g., ml.g4dn.2xlarge)
- `instance_count`: Number of instances (1 for single-GPU)
- `volume_size`: EBS volume size in GB

#### Training Configuration
- `max_run`: Maximum runtime in seconds (24h = 86400)
- `use_spot_instances`: Use cheaper spot instances
- `max_wait`: Maximum wait time for spot instances

#### Hyperparameters
Passed as string key-value pairs to training script:
- `epochs`: Number of training epochs
- `batch`: Batch size
- `imgsz`: Input image size
- `data`: Dataset YAML file
- `patience`: Early stopping patience

#### Data Configuration
- `input_data.training.s3_uri`: S3 path to training data
- `output_data.s3_uri`: S3 path for outputs

## Training Output Configuration

### `args.yaml`

Generated automatically during training, stores all training arguments.

```yaml
task: detect
mode: train
model: yolo11n.pt
data: data_balanced.yaml
epochs: 50
batch: 16
imgsz: 640
device: 0
workers: 8
project: ppe_training
name: yolo11_balanced
exist_ok: false
pretrained: true
optimizer: AdamW
lr0: 0.01
lrf: 0.01
momentum: 0.937
weight_decay: 0.0005
patience: 10
# ... many more parameters
```

## Environment Configuration

### `.env` (Example)

Store sensitive configuration:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET=your-bucket-name
S3_PREFIX=datasets/ppe_balanced

# SageMaker Configuration
SAGEMAKER_ROLE=arn:aws:iam::123456789012:role/SageMakerRole
SAGEMAKER_INSTANCE_TYPE=ml.g4dn.2xlarge

# Training Configuration
EPOCHS=50
BATCH_SIZE=16
IMAGE_SIZE=640
```

**Note:** Never commit `.env` to version control!

### `requirements.txt`

Python dependencies:

```txt
ultralytics>=8.0.0
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
pillow>=10.0.0
pyyaml>=6.0
tqdm>=4.65.0
boto3>=1.28.0
sagemaker>=2.180.0
```

### `requirements-docs.txt`

Documentation dependencies:

```txt
mkdocs>=1.5.0
mkdocs-material>=9.4.0
pymdown-extensions>=10.3.0
```

## GitHub Actions Configuration

### `.github/workflows/deploy-docs.yml`

Automated documentation deployment:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: 3.x
      
      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install pymdown-extensions
      
      - name: Build documentation
        run: mkdocs build
      
      - name: Deploy to S3
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          S3_BUCKET: ${{ secrets.S3_BUCKET_NAME }}
        run: |
          pip install awscli
          aws s3 sync site/ s3://$S3_BUCKET --region us-east-1 --delete
      
      - name: Invalidate CloudFront
        if: ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          DISTRIBUTION_ID: ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}
        run: |
          aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*"
```

## VS Code Configuration

### `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "venv/": true,
    "site/": true
  }
}
```

## Next Steps

- [Scripts Reference](scripts.md)
- [Training Guide](../training/model.md)
- [SageMaker Setup](../sagemaker/configuration.md)
