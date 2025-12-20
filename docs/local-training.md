# Local Training

## Quick Training Scripts

### Train on Full Dataset

```bash
python train_yolo11.py
```

### Train on Subset

```bash
python train_subset.py
```

### Quick Training Test

```bash
python train_quick.py
```

## Training Configuration

### Basic Configuration

Training parameters are defined in the scripts:

```python
model = YOLO('yolo11n.pt')

results = model.train(
    data='data_balanced.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='yolo11_balanced',
    device=0,  # GPU
    workers=8,
    patience=10
)
```

### Data Configuration Files

#### `data_balanced.yaml`

Full dataset configuration:

```yaml
path: ./datasets/ppe_balanced
train: train/images
val: valid/images

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

#### `data_subset.yaml`

Subset for quick testing:

```yaml
path: ./datasets/ppe_balanced
train: train_subset.txt
val: val_subset.txt

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

## Monitoring Training

Training outputs are saved to:

```
ppe_training/
└── yolo11_balanced/
    ├── args.yaml
    ├── results.csv
    └── weights/
        ├── best.pt
        └── last.pt
```

## Training Metrics

Monitor these metrics during training:

- **Box Loss**: Bounding box regression loss
- **Class Loss**: Classification loss
- **DFL Loss**: Distribution focal loss
- **mAP50**: Mean Average Precision at IoU=0.5
- **mAP50-95**: mAP at IoU thresholds 0.5-0.95

## Validation

After training, validate your model:

```bash
jupyter notebook validation_fixed.ipynb
```

See [Validation Guide](training/validation.md) for details.

## Troubleshooting

### CUDA Out of Memory

Reduce batch size:

```python
results = model.train(
    batch=8,  # Reduced from 16
    # ... other params
)
```

### Slow Training

- Ensure GPU is being used: `device=0`
- Increase workers: `workers=8`
- Check dataset loading time

## Next Steps

- [Deploy to SageMaker](sagemaker/launch.md)
- [Model Validation](training/validation.md)
