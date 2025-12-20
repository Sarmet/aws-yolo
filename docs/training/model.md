# Model Training

## YOLO11 Architecture

YOLO11 is the latest version with:

- Improved backbone network
- Better feature pyramid
- Enhanced detection head
- Faster inference speed

## Pre-trained Models

| Model | Size | Parameters | Speed | mAP |
|-------|------|------------|-------|-----|
| yolo11n.pt | Nano | 2.6M | Fastest | Lower |
| yolo11s.pt | Small | 9.4M | Fast | Medium |
| yolo11m.pt | Medium | 20.1M | Medium | High |
| yolo11l.pt | Large | 25.3M | Slow | Higher |
| yolo11x.pt | XLarge | 56.9M | Slowest | Highest |

For this project, we use **yolo11n.pt** for faster training.

## Training Parameters

### Essential Parameters

```python
model.train(
    data='data_balanced.yaml',  # Dataset config
    epochs=50,                   # Training epochs
    imgsz=640,                   # Input image size
    batch=16,                    # Batch size
    device=0,                    # GPU device
    workers=8,                   # Data loading workers
    name='yolo11_balanced',      # Run name
    patience=10                  # Early stopping patience
)
```

### Advanced Parameters

```python
model.train(
    # Data
    data='data_balanced.yaml',
    
    # Training
    epochs=100,
    batch=32,
    imgsz=640,
    
    # Optimization
    optimizer='AdamW',
    lr0=0.01,                    # Initial learning rate
    lrf=0.01,                    # Final learning rate
    momentum=0.937,
    weight_decay=0.0005,
    
    # Augmentation
    hsv_h=0.015,                 # HSV-Hue augmentation
    hsv_s=0.7,                   # HSV-Saturation
    hsv_v=0.4,                   # HSV-Value
    degrees=0.0,                 # Rotation
    translate=0.1,               # Translation
    scale=0.5,                   # Scaling
    shear=0.0,                   # Shear
    perspective=0.0,             # Perspective
    flipud=0.0,                  # Vertical flip
    fliplr=0.5,                  # Horizontal flip
    mosaic=1.0,                  # Mosaic augmentation
    mixup=0.0,                   # Mixup augmentation
    
    # Regularization
    dropout=0.0,
    label_smoothing=0.0,
    
    # System
    device=0,
    workers=8,
    project='ppe_training',
    name='yolo11_balanced',
    exist_ok=False,
    patience=10,
    save=True,
    save_period=-1,
    cache=False,
    
    # Validation
    val=True,
    plots=True
)
```

## Training Metrics

### Loss Functions

1. **Box Loss**: Bounding box regression
   - CIoU loss for box coordinates
   - Lower is better

2. **Class Loss**: Classification loss
   - Binary cross-entropy
   - Lower is better

3. **DFL Loss**: Distribution Focal Loss
   - Fine-grained localization
   - Lower is better

### Performance Metrics

1. **Precision**: TP / (TP + FP)
   - How many detections are correct

2. **Recall**: TP / (TP + FN)
   - How many objects are detected

3. **mAP50**: Mean Average Precision at IoU=0.5
   - Standard YOLO metric

4. **mAP50-95**: mAP averaged over IoU 0.5-0.95
   - COCO evaluation metric

## Training Results

Results are saved to:

```
ppe_training/yolo11_balanced/
├── weights/
│   ├── best.pt      # Best model
│   └── last.pt      # Last epoch
├── results.csv      # Training metrics
├── results.png      # Plots
├── confusion_matrix.png
├── F1_curve.png
├── P_curve.png
├── PR_curve.png
├── R_curve.png
└── args.yaml        # Training arguments
```

## Analyzing Results

### Load Results CSV

```python
import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv('ppe_training/yolo11_balanced/results.csv')
results.columns = results.columns.str.strip()

# Plot training loss
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(results['epoch'], results['train/box_loss'], label='Box Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 3, 2)
plt.plot(results['epoch'], results['train/cls_loss'], label='Class Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 3, 3)
plt.plot(results['epoch'], results['metrics/mAP50(B)'], label='mAP50')
plt.xlabel('Epoch')
plt.ylabel('mAP')
plt.legend()

plt.tight_layout()
plt.show()
```

## Resume Training

To resume from checkpoint:

```python
from ultralytics import YOLO

model = YOLO('ppe_training/yolo11_balanced/weights/last.pt')
model.train(resume=True)
```

## Best Practices

### Batch Size Selection

- **Small GPU (4-6GB)**: batch=8
- **Medium GPU (8-12GB)**: batch=16
- **Large GPU (16GB+)**: batch=32

### Learning Rate

- Default works well: `lr0=0.01`
- Reduce for fine-tuning: `lr0=0.001`
- Increase for large batches: `lr0=0.02`

### Early Stopping

- Set `patience=10-20` for automatic stopping
- Saves time if model stops improving

### Data Augmentation

- More augmentation = better generalization
- Reduce if overfitting isn't an issue

## Next Steps

- [Model Validation](validation.md)
- [Deploy to SageMaker](../sagemaker/launch.md)
