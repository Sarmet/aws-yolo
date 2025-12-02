import os
import glob
import yaml
from ultralytics import YOLO

# Config
BASE_DIR = os.path.abspath('.')
DATASET_DIR = os.path.join(BASE_DIR, 'datasets', 'ppe_balanced')
TRAIN_IMG_DIR = os.path.join(DATASET_DIR, 'train', 'images')
VAL_IMG_DIR = os.path.join(DATASET_DIR, 'valid', 'images')

# 1. Select subset of images
# Selectam primele 100 de imagini pentru antrenare si 20 pentru validare
train_images = glob.glob(os.path.join(TRAIN_IMG_DIR, '*.jpg'))[:100] 
val_images = glob.glob(os.path.join(VAL_IMG_DIR, '*.jpg'))[:20]     

print(f"Selected {len(train_images)} training images and {len(val_images)} validation images.")

# 2. Create text files with paths
train_txt_path = os.path.join(DATASET_DIR, 'train_subset.txt')
val_txt_path = os.path.join(DATASET_DIR, 'val_subset.txt')

with open(train_txt_path, 'w') as f:
    f.write('\n'.join(train_images))

with open(val_txt_path, 'w') as f:
    f.write('\n'.join(val_images))

# 3. Create subset yaml
# Read original names from data_balanced.yaml
with open('data_balanced.yaml', 'r') as f:
    original_data = yaml.safe_load(f)

subset_data = {
    'path': DATASET_DIR,
    'train': 'train_subset.txt',
    'val': 'val_subset.txt',
    'names': original_data['names']
}

subset_yaml_path = 'data_subset.yaml'
with open(subset_yaml_path, 'w') as f:
    yaml.dump(subset_data, f)

print(f"Created {subset_yaml_path}")

# 4. Train
if __name__ == '__main__':
    # Folosim modelul Nano (cel mai mic)
    model = YOLO('yolo11n.pt') 
    print("Starting quick training on subset...")
    
    model.train(
        data=subset_yaml_path,
        epochs=5,           # 5 epoci pe 100 de imagini va fi foarte rapid
        imgsz=640,
        batch=4,            # Batch mic pentru CPU
        project='ppe_training',
        name='yolo11_subset_run',
        exist_ok=True
    )
    print("Training complete. Model saved to ppe_training/yolo11_subset_run/weights/best.pt")
