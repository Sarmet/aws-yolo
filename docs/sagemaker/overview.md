# AWS SageMaker Overview

## Why SageMaker?

AWS SageMaker provides:

- Scalable GPU instances (ml.g4dn, ml.p3, etc.)
- Pay-per-use pricing
- Managed training infrastructure
- Automatic resource cleanup
- 📁 S3 integration for datasets

## Architecture

```
Local Machine          AWS Cloud
    │                      │
    ├──> S3 Bucket ────────┤
    │    (Dataset)         │
    │                      │
    └──> SageMaker ────────┤
         Training Job      │
              │            │
              └──> S3      │
                   (Model) │
```

## SageMaker Training Flow

1. **Prepare Dataset**: Upload to S3
2. **Configure Job**: Set instance type, hyperparameters
3. **Launch Training**: Submit job via CLI or Python SDK
4. **Monitor Progress**: Check CloudWatch logs
5. **Retrieve Model**: Download from S3

## Instance Types

| Instance | GPUs | Memory | Best For |
|----------|------|--------|----------|
| ml.g4dn.xlarge | 1x T4 | 16GB | Testing, small models |
| ml.g4dn.2xlarge | 1x T4 | 32GB | Medium training |
| ml.p3.2xlarge | 1x V100 | 61GB | Large models, faster training |
| ml.p3.8xlarge | 4x V100 | 244GB | Multi-GPU training |

## Cost Estimation

Example costs (EU regions):

- **ml.g4dn.xlarge**: ~$0.70/hour
- **ml.g4dn.2xlarge**: ~$1.00/hour
- **ml.p3.2xlarge**: ~$3.80/hour

Note: Use spot instances for 70% discount.

## Next Steps

- [Configure SageMaker](configuration.md)
- [Launch Training Job](launch.md)
