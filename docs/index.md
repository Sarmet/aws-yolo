# AWS YOLO Training Documentation

Documentation for training YOLO models for Personal Protective Equipment (PPE) detection using AWS SageMaker.

## Project Overview

This project provides a pipeline for:

- Training YOLO11 models on custom datasets
- Deploying training jobs to AWS SageMaker
- Validating model performance
- Managing training configurations

## Quick Start

1. Setup environment: [Setup Guide](setup.md)
2. Prepare dataset: [Dataset Preparation](training/dataset.md)
3. Launch training: [Local Training](local-training.md) or [SageMaker Overview](sagemaker/overview.md)

## 📂 Project Structure

```
aws-yolo/
├── datasets/          # Training datasets
├── ppe_training/      # Training outputs
├── train_*.py         # Training scripts
├── launch_sagemaker_* # SageMaker deployment scripts
└── validation_*.ipynb # Validation notebooks
```

## Key Features

- YOLO11 model training
- AWS SageMaker integration
- Automated dataset balancing
- Training validation tools
- S3 data management

## Documentation Sections

- **Getting Started**: Setup and local training guides
- **AWS SageMaker**: Cloud training configuration
- **Training**: Dataset preparation and model training
- **Reference**: Scripts and configuration reference
