# Scripts Reference

## Training Scripts

### train_yolo11.py

Main training script for full dataset.

::: train_yolo11.main
    options:
      show_source: true

**Usage:**
```bash
python train_yolo11.py
```

### `train_subset.py`

Training on data subset for quick testing.

```python
model.train(
    data='data_subset.yaml',
    epochs=10,
    # ... reduced parameters
)
```

**Usage:**
```bash
python train_subset.py
```

### `train_quick.py`

Ultra-fast training for debugging.

```python
model.train(
    data='data_subset.yaml',
    epochs=3,
    batch=8,
    imgsz=320,  # Smaller images
    # ... minimal settings
)
```

**Usage:**
```bash
python train_quick.py
```

### `train_entrypoint.py`

SageMaker training entrypoint.

Handles:
- Command-line arguments from SageMaker
- S3 data loading
- Environment variable configuration
- Model output saving

**Usage (on SageMaker):**
```bash
python train_entrypoint.py \
    --epochs 50 \
    --batch 16 \
    --data /opt/ml/input/data/training/data_balanced.yaml
```

## Data Management Scripts

### upload_data_s3.py

Upload dataset to S3 for SageMaker training.

::: upload_data_s3.main
    options:
      show_source: true

**Usage:**
```bash
python upload_data_s3.py
```

**Environment variables:**
- `S3_BUCKET`: Target S3 bucket
- `AWS_REGION`: AWS region

### `prepare_repo.py`

Prepare repository structure and validate dataset.

Functions:
- Create directory structure
- Validate dataset integrity
- Generate subset files
- Check label format

**Usage:**
```bash
python prepare_repo.py
```

## SageMaker Deployment Scripts

### launch_sagemaker_job.py

Launch SageMaker training job via Python SDK.

::: launch_sagemaker_job
    options:
      show_source: false
      members: false

**Usage:**
```bash
python launch_sagemaker_job.py
```

**Requirements:**
- AWS credentials configured
- `training_job_config.json` configured
- Dataset uploaded to S3

### `launch_sagemaker_cli.ps1`

PowerShell script for Windows users.

```powershell
# Load configuration
$config = Get-Content training_job_config.json | ConvertFrom-Json

# Launch training job
aws sagemaker create-training-job `
    --training-job-name $config.job_name `
    --role-arn $config.role_arn `
    --algorithm-specification $config.algorithm `
    # ... more parameters
```

**Usage:**
```powershell
.\launch_sagemaker_cli.ps1
```

## Validation Scripts

### `validation_fixed.ipynb`

Jupyter notebook for model validation.

Sections:
1. Load model
2. Run validation
3. Calculate metrics
4. Visualize results
5. Error analysis

**Usage:**
```bash
jupyter notebook validation_fixed.ipynb
```

### `validation_colab.ipynb`

Google Colab version with setup cells.

Additional features:
- Google Drive integration
- GPU setup
- Package installation

**Usage:**
Open in Google Colab and run all cells.

## Configuration Files

### `data_balanced.yaml`

Full dataset configuration:

```yaml
path: ./datasets/ppe_balanced
train: train/images
val: valid/images

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

### `data_subset.yaml`

Subset configuration:

```yaml
path: ./datasets/ppe_balanced
train: train_subset.txt
val: val_subset.txt

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

### `training_job_config.json`

SageMaker job configuration:

```json
{
  "job_name": "yolo11-ppe-training",
  "instance_type": "ml.g4dn.2xlarge",
  "hyperparameters": {
    "epochs": "50",
    "batch": "16"
  },
  "input_data": {
    "s3_uri": "s3://bucket/datasets/"
  }
}
```

## Helper Functions

### Common Imports

```python
from ultralytics import YOLO
import torch
import cv2
import matplotlib.pyplot as plt
import numpy as np
```

### Load Model

```python
def load_model(weights_path='best.pt'):
    """Load trained YOLO model"""
    model = YOLO(weights_path)
    return model
```

### Predict Image

```python
def predict_image(model, image_path, conf=0.25):
    """Run inference on image"""
    results = model.predict(
        source=image_path,
        conf=conf,
        save=False
    )
    return results[0]
```

### Visualize Results

```python
def visualize_results(image_path, results):
    """Display predictions"""
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(results.plot())
    plt.axis('off')
    plt.show()
```

## Next Steps

- [Configuration Files Reference](config.md)
- [Training Guide](../training/model.md)
- [SageMaker Deployment](../sagemaker/launch.md)
