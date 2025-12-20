# Model Validation

## Validation Notebooks

### `validation_fixed.ipynb`

Complete validation pipeline:

1. Load trained model
2. Run inference on validation set
3. Calculate metrics
4. Visualize results
5. Analyze per-class performance

### `validation_colab.ipynb`

Google Colab version for cloud validation.

## Running Validation

### Launch Jupyter

```bash
jupyter notebook validation_fixed.ipynb
```

### Load Model

```python
from ultralytics import YOLO

# Load best model
model = YOLO('ppe_training/yolo11_balanced/weights/best.pt')

# Or latest checkpoint
model = YOLO('ppe_training/yolo11_balanced/weights/last.pt')
```

### Validate on Test Set

```python
# Run validation
results = model.val(
    data='data_balanced.yaml',
    split='val',
    imgsz=640,
    batch=16,
    conf=0.25,  # Confidence threshold
    iou=0.45,   # NMS IoU threshold
    plots=True
)

# Print metrics
print(f"mAP50: {results.box.map50:.4f}")
print(f"mAP50-95: {results.box.map:.4f}")
```

## Inference on Images

### Single Image

```python
# Predict on single image
results = model.predict(
    source='demo_images/test1.jpg',
    conf=0.25,
    save=True,
    save_txt=True
)

# Access results
for r in results:
    boxes = r.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        print(f"Class: {cls}, Conf: {conf:.2f}, Box: {xyxy}")
```

### Multiple Images

```python
# Predict on directory
results = model.predict(
    source='validation_samples/',
    conf=0.25,
    save=True
)
```

## Visualization

### Display Predictions

```python
import cv2
import matplotlib.pyplot as plt

# Load image
img = cv2.imread('demo_images/test1.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Predict
results = model.predict(source=img, conf=0.25)

# Plot
plt.figure(figsize=(12, 8))
plt.imshow(results[0].plot())
plt.axis('off')
plt.show()
```

### Confusion Matrix

```python
from ultralytics.utils.plotting import plot_confusion_matrix

# Load confusion matrix
cm = results.confusion_matrix.matrix

# Plot
plot_confusion_matrix(
    cm,
    names=model.names,
    save_dir='.',
    normalize=True
)
```

## Performance Analysis

### Per-Class Metrics

```python
# Get per-class results
class_names = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask']

for i, name in enumerate(class_names):
    print(f"\n{name}:")
    print(f"  Precision: {results.box.p[i]:.4f}")
    print(f"  Recall: {results.box.r[i]:.4f}")
    print(f"  mAP50: {results.box.ap50[i]:.4f}")
    print(f"  mAP50-95: {results.box.ap[i]:.4f}")
```

### Speed Benchmarking

```python
import time

# Warm-up
model.predict('demo_images/test1.jpg', verbose=False)

# Benchmark
times = []
for _ in range(100):
    start = time.time()
    model.predict('demo_images/test1.jpg', verbose=False)
    times.append(time.time() - start)

print(f"Average inference time: {sum(times)/len(times)*1000:.2f}ms")
print(f"FPS: {1/(sum(times)/len(times)):.2f}")
```

## Export Model

### Export to ONNX

```python
# Export to ONNX
model.export(format='onnx', imgsz=640)
```

### Export to TensorRT

```python
# Export to TensorRT (requires GPU)
model.export(format='engine', imgsz=640, half=True)
```

### Export Formats

| Format | Use Case |
|--------|----------|
| ONNX | General deployment |
| TensorRT | NVIDIA GPU optimization |
| CoreML | iOS/macOS |
| TFLite | Mobile/Edge |
| OpenVINO | Intel hardware |

## Threshold Tuning

### Find Optimal Confidence

```python
import numpy as np

confidences = np.arange(0.1, 0.9, 0.05)
results_list = []

for conf in confidences:
    r = model.val(
        data='data_balanced.yaml',
        conf=conf,
        verbose=False
    )
    results_list.append({
        'conf': conf,
        'mAP50': r.box.map50,
        'precision': r.box.p.mean(),
        'recall': r.box.r.mean()
    })

# Plot results
import pandas as pd
df = pd.DataFrame(results_list)

plt.figure(figsize=(10, 6))
plt.plot(df['conf'], df['mAP50'], label='mAP50')
plt.plot(df['conf'], df['precision'], label='Precision')
plt.plot(df['conf'], df['recall'], label='Recall')
plt.xlabel('Confidence Threshold')
plt.ylabel('Metric Value')
plt.legend()
plt.grid(True)
plt.show()
```

## Error Analysis

### False Positives

```python
# Find images with false positives
# Predictions with wrong class or background

def analyze_false_positives(model, val_path, conf=0.25):
    results = model.val(data=val_path, conf=conf)
    
    # Extract false positive info
    fp_images = []
    # Analysis logic here
    
    return fp_images
```

### False Negatives

```python
# Find images with missed detections
def analyze_false_negatives(model, val_path, conf=0.25):
    results = model.val(data=val_path, conf=conf)
    
    # Extract false negative info
    fn_images = []
    # Analysis logic here
    
    return fn_images
```

## Next Steps

- [Refine training parameters](model.md)
- [Export for deployment](../reference/scripts.md)
- [Deploy to production](../sagemaker/overview.md)
