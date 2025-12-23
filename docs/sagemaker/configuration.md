# SageMaker Configuration

## Configuration File

The `training_job_config.json` defines your training job:

```json
{
  "job_name": "yolo11-ppe-training",
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
    "data": "data_balanced.yaml"
  },
  
  "input_data": {
    "s3_uri": "s3://YOUR-BUCKET/datasets/ppe_balanced/"
  },
  
  "output_data": {
    "s3_uri": "s3://YOUR-BUCKET/output/"
  }
}
```

## Key Parameters

### Instance Configuration

- **instance_type**: GPU instance type (see [Overview](overview.md))
- **instance_count**: Number of instances (1 for single-GPU)
- **volume_size**: EBS volume size in GB

### Training Configuration

- **max_run**: Maximum training time (seconds)
- **use_spot_instances**: Use cheaper spot instances
- **max_wait**: Maximum wait time for spot instances

### Hyperparameters

Training parameters passed to your script:

- **epochs**: Number of training epochs
- **batch**: Batch size
- **imgsz**: Input image size
- **data**: Dataset configuration file

## S3 Data Structure

Upload your dataset to S3:

```
s3://YOUR-BUCKET/
├── datasets/
│   └── ppe_balanced/
│       ├── train/
│       ├── valid/
│       ├── data_balanced.yaml
│       └── ...
└── output/
    └── [training outputs]
```

## Upload Dataset to S3

Use the provided script:

```bash
python upload_data_s3.py
```

Or manually:

```bash
aws s3 sync datasets/ppe_balanced/ s3://YOUR-BUCKET/datasets/ppe_balanced/
```

## IAM Permissions

Your IAM role needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:CreateTrainingJob",
        "sagemaker:DescribeTrainingJob",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Environment Variables

Set these before launching:

```bash
export AWS_REGION=us-east-1
export S3_BUCKET=your-bucket-name
export SAGEMAKER_ROLE=arn:aws:iam::ACCOUNT:role/SageMakerRole
```

## Next Steps

- [Launch Training Job](launch.md)
- [Dataset Preparation](../training/dataset.md)
