# Launch SageMaker Training

## Launch Methods

### Method 1: PowerShell Script (Windows)

```powershell
.\launch_sagemaker_cli.ps1
```

### Method 2: Python Script

```bash
python launch_sagemaker_job.py
```

## Launch Process

1. **Verify Configuration**

```bash
# Check training_job_config.json
cat training_job_config.json
```

2. **Ensure Dataset is on S3**

```bash
aws s3 ls s3://YOUR-BUCKET/datasets/ppe_balanced/
```

3. **Launch Training**

```bash
python launch_sagemaker_job.py
```

Expected output:

```
Training job created: yolo11-ppe-training-20231220-143022
Status: InProgress
Check progress: https://console.aws.amazon.com/sagemaker/...
```

## Monitor Training

### Check Status

```bash
aws sagemaker describe-training-job --training-job-name yolo11-ppe-training-20231220-143022
```

### View Logs

```bash
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

### CloudWatch Console

Visit AWS CloudWatch Console:

1. Navigate to **CloudWatch** → **Log groups**
2. Find `/aws/sagemaker/TrainingJobs`
3. Select your job name
4. View real-time logs

## Training Outputs

After completion, outputs are saved to:

```
s3://YOUR-BUCKET/output/yolo11-ppe-training-20231220-143022/
├── output/
│   ├── model.tar.gz
│   └── ...
└── logs/
```

## Download Results

```bash
aws s3 sync s3://YOUR-BUCKET/output/yolo11-ppe-training-20231220-143022/ ./sagemaker_output/
```

## Extract Model

```bash
tar -xzf sagemaker_output/output/model.tar.gz
```

## Troubleshooting

### Job Fails Immediately

Check:
- IAM role permissions
- S3 bucket access
- Training script syntax

### CUDA Errors

- Verify instance type has GPU
- Check PyTorch/CUDA compatibility

### Timeout Errors

- Increase `max_run` in config
- Use larger instance type
- Reduce epochs or batch size

## Cost Monitoring

Track costs in AWS Cost Explorer:

1. Filter by **Service**: SageMaker
2. Group by **Training Job**
3. View daily/monthly costs

## Next Steps

- [Model Validation](../training/validation.md)
- [View Training Metrics](../training/model.md)
