import os
import glob
import shutil

# Config
valid_labels_path = 'datasets/ppe_balanced/valid/labels'
valid_images_path = 'datasets/ppe_balanced/valid/images'
output_dir = 'validation_samples'

# Create output directory
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Find images with gloves
label_files = glob.glob(os.path.join(valid_labels_path, '*.txt'))
print(f"Scanning {len(label_files)} label files...")

count = 0
for label_file in label_files:
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    has_glove = False
    for line in lines:
        if line.strip().startswith('0 '): # 0 = glove
            has_glove = True
            break
    
    if has_glove:
        image_name = os.path.basename(label_file).replace('.txt', '.jpg')
        image_path = os.path.join(valid_images_path, image_name)
        
        if os.path.exists(image_path):
            # Copy image to validation_samples
            shutil.copy(image_path, os.path.join(output_dir, image_name))
            print(f"Copied: {image_name}")
            count += 1
    
    if count >= 10: # Save 10 examples
        break

print(f"Done. Saved {count} images to {output_dir}.")
