# Launch SageMaker training job using AWS CLI (bypasses Python SDK issues)

$BUCKET = "radu-yolo-data"
$ROLE_ARN = "arn:aws:iam::881839984863:role/SageMakerExecutionRole"
$JOB_NAME = "yolo-test-" + (Get-Date -Format "yyyyMMdd-HHmmss")

# Create training job configuration
$config = @"
{
  "TrainingJobName": "$JOB_NAME",
  "RoleArn": "$ROLE_ARN",
  "AlgorithmSpecification": {
    "TrainingImage": "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.1.0-gpu-py310",
    "TrainingInputMode": "File",
    "EnableSageMakerMetricsTimeSeries": false
  },
  "InputDataConfig": [
    {
      "ChannelName": "training",
      "DataSource": {
        "S3DataSource": {
          "S3DataType": "S3Prefix",
          "S3Uri": "s3://$BUCKET/data.zip",
          "S3DataDistributionType": "FullyReplicated"
        }
      }
    },
    {
      "ChannelName": "code",
      "DataSource": {
        "S3DataSource": {
          "S3DataType": "S3Prefix",
          "S3Uri": "s3://$BUCKET/code/",
          "S3DataDistributionType": "FullyReplicated"
        }
      }
    }
  ],
  "OutputDataConfig": {
    "S3OutputPath": "s3://$BUCKET/output"
  },
  "ResourceConfig": {
    "InstanceType": "ml.m5.large",
    "InstanceCount": 1,
    "VolumeSizeInGB": 30
  },
  "StoppingCondition": {
    "MaxRuntimeInSeconds": 900
  },
  "HyperParameters": {
    "sagemaker_program": "train_entrypoint.py",
    "sagemaker_submit_directory": "s3://$BUCKET/code/sourcedir.tar.gz",
    "epochs": "1",
    "imgsz": "640",
    "batch": "8",
    "max_images": "200"
  },
  "CheckpointConfig": {
    "S3Uri": "s3://$BUCKET/checkpoints"
  },
  "EnableNetworkIsolation": false,
  "EnableInterContainerTrafficEncryption": false
}
"@

# Save configuration to file
$config | Out-File -FilePath "training_job_config.json" -Encoding UTF8

Write-Host "Job name: $JOB_NAME" -ForegroundColor Green
Write-Host ""
Write-Host "Launching SageMaker training job..." -ForegroundColor Yellow

# Launch the training job
aws sagemaker create-training-job --cli-input-json file://training_job_config.json --region us-east-1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Job launched successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Monitor your job:" -ForegroundColor Cyan
    Write-Host "  aws sagemaker describe-training-job --training-job-name $JOB_NAME --region us-east-1"
    Write-Host ""
    Write-Host "Watch logs:" -ForegroundColor Cyan
    Write-Host "  aws sagemaker wait training-job-completed-or-stopped --training-job-name $JOB_NAME --region us-east-1"
} else {
    Write-Host ""
    Write-Host "✗ Job launch failed!" -ForegroundColor Red
}
