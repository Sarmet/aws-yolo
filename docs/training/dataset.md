# Dataset Preparation

## Dataset Structure

YOLO requires this structure:

```
datasets/ppe_balanced/
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── labels/
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
└── valid/
    ├── images/
    └── labels/
```

## Label Format

Each `.txt` file contains annotations:

```
class_id x_center y_center width height
```

Example (`image1.txt`):

```
0 0.5 0.5 0.3 0.4
2 0.7 0.3 0.2 0.25
```

Values are normalized (0.0-1.0):
- `class_id`: 0-3 (Hardhat, Mask, NO-Hardhat, NO-Mask)
- `x_center, y_center`: Center of bounding box
- `width, height`: Box dimensions

## Dataset Configuration

### `data_balanced.yaml`

```yaml
path: ./datasets/ppe_balanced
train: train/images
val: valid/images

nc: 4  # Number of classes
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

### Class Distribution

| Class | Training | Validation |
|-------|----------|------------|
| Hardhat | ~2500 | ~500 |
| Mask | ~2500 | ~500 |
| NO-Hardhat | ~2500 | ~500 |
| NO-Mask | ~2500 | ~500 |

## Data Augmentation

YOLO automatically applies:

- Random scaling
- Random crops
- Horizontal flips
- HSV color adjustments
- Mosaic augmentation

## Creating Subsets

For quick testing, create subset files:

### `train_subset.txt`

```
train/images/image1.jpg
train/images/image2.jpg
train/images/image3.jpg
...
```

### `data_subset.yaml`

```yaml
path: ./datasets/ppe_balanced
train: train_subset.txt
val: val_subset.txt

nc: 4
names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']
```

## Prepare Repository Script

Use `prepare_repo.py` to organize your dataset:

```bash
python prepare_repo.py
```

This script:
- Validates dataset structure
- Checks label files
- Creates subset files
- Verifies class distribution

## Data Quality Checks

### Check Image-Label Pairs

```python
import os

images = set(os.listdir('datasets/ppe_balanced/train/images'))
labels = set(os.listdir('datasets/ppe_balanced/train/labels'))

# Remove extensions
images = {f.rsplit('.', 1)[0] for f in images}
labels = {f.rsplit('.', 1)[0] for f in labels}

# Find mismatches
missing_labels = images - labels
missing_images = labels - images

print(f"Images without labels: {len(missing_labels)}")
print(f"Labels without images: {len(missing_images)}")
```

### Validate Label Format

```python
def validate_label(label_path):
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                return False
            
            class_id, x, y, w, h = map(float, parts)
            
            # Check ranges
            if not (0 <= class_id < 4):
                return False
            if not all(0 <= v <= 1 for v in [x, y, w, h]):
                return False
    
    return True
```

## Next Steps

- [Start Training](model.md)
- [Local Training Guide](../local-training.md)
