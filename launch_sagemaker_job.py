#!/usr/bin/env python
"""Launch SageMaker training job for YOLO model.

Configures and launches a PyTorch-based SageMaker training job with
spot instances for cost optimization. Uses CPU instance (ml.m5.large)
for quick smoke testing.

Usage:
    python launch_sagemaker_job.py

Configuration:
    BUCKET: S3 bucket containing training data
    REGION: AWS region for training job
    ROLE: IAM role ARN with SageMaker execution permissions
"""

import sagemaker
from sagemaker.pytorch import PyTorch

# Configurare
BUCKET = 'radu-yolo-data'
REGION = 'us-east-1'
ROLE = "arn:aws:iam::881839984863:role/SageMakerExecutionRole"

print("=" * 60)
print("LANSARE JOB SAGEMAKER - YOLO SMOKE TEST")
print("=" * 60)

# Creare sesiune
session = sagemaker.Session()

# Configurare Estimator
estimator = PyTorch(
    entry_point='train_entrypoint.py',
    source_dir='.',
    role=ROLE,
    framework_version='2.0',
    py_version='py310',
    instance_count=1,
    instance_type='ml.m5.large',  # CPU ieftin
    
    # Spot Instances + Safety Limits
    use_spot_instances=True,
    max_run=900,       # 15 minute max
    max_wait=1800,     # 30 min max wait
    
    hyperparameters={
        'epochs': 1,
        'imgsz': 640,
        'batch': 8,
        'max_images': 500
    }
)

# Lansare
data_path = f's3://{BUCKET}/data.zip'
print(f"\nDate de intrare: {data_path}")
print("Lansare job...")
print("-" * 60)

estimator.fit({'training': data_path})

print("\n" + "=" * 60)
print("JOB LANSAT CU SUCCES!")
print("=" * 60)
print("\nPentru a vedea progresul:")
print("1. Mergi la AWS Console -> SageMaker -> Training Jobs")
print("2. Sau asteapta aici sa vezi log-urile in timp real")
