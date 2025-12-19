import os
import sys
import subprocess
import zipfile
import yaml
import shutil

def install_dependencies():
    """Instaleaza librariile necesare in container (YOLO nu e standard in PyTorch image)"""
    print("--- Installing Ultralytics YOLO ---")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])

def prepare_data(base_dir, max_images=0):
    """
    Dezarhiveaza datele si creeaza un fisier data.yaml corect pentru Linux.
    SageMaker monteaza datele de intrare in os.environ['SM_CHANNEL_TRAINING']
    """
    print("--- Preparing Data ---")
    
    # Calea unde SageMaker pune datele venite de pe S3
    input_dir = os.environ.get('SM_CHANNEL_TRAINING', '/opt/ml/input/data/training')
    # Calea unde vom lucra (writable)
    work_dir = base_dir
    
    zip_path = os.path.join(input_dir, 'data.zip')
    
    if not os.path.exists(zip_path):
        print(f"ERROR: data.zip not found at {zip_path}")
        # Listam ce e acolo pentru debug
        print(f"Contents of {input_dir}: {os.listdir(input_dir)}")
        sys.exit(1)
        
    print(f"Unzipping {zip_path} to {work_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(work_dir)
        
    # Structura dezarhivata ar trebui sa fie:
    # work_dir/datasets/ppe_balanced/...
    
    dataset_root = os.path.join(work_dir, 'datasets', 'ppe_balanced')

    # --- LIMITARE DATASET (OPTIONAL) ---
    if max_images > 0:
        print(f"--- Limiting dataset to {max_images} images per split ---")
        for split in ['train', 'valid']:
            img_dir = os.path.join(dataset_root, split, 'images')
            lbl_dir = os.path.join(dataset_root, split, 'labels')
            
            if os.path.exists(img_dir):
                files = sorted(os.listdir(img_dir))
                if len(files) > max_images:
                    print(f"  Truncating {split} from {len(files)} to {max_images}...")
                    for f in files[max_images:]:
                        os.remove(os.path.join(img_dir, f))
                        # Stergem si label-ul asociat
                        name = os.path.splitext(f)[0]
                        lbl = os.path.join(lbl_dir, name + '.txt')
                        if os.path.exists(lbl): os.remove(lbl)
                else:
                    print(f"  {split}: {len(files)} images (<= {max_images}), keeping all.")
    
    # Cream un nou data.yaml cu cai absolute de Linux
    # Structura YOLO asteapta caile catre train/val
    new_yaml_content = {
        'path': dataset_root,
        'train': 'train/images',
        'val': 'valid/images', # Atentie: in zip-ul tau folderul e 'valid' sau 'val'? Verificam structura
        'names': {
            0: 'glove', 1: 'goggles', 2: 'helmet', 3: 'mask', 
            4: 'no_glove', 5: 'no_goggles', 6: 'no_helmet', 
            7: 'no_mask', 8: 'no_shoes', 9: 'shoes'
        }
    }
    
    yaml_path = os.path.join(work_dir, 'data_sagemaker.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(new_yaml_content, f)
        
    print(f"Created new config at {yaml_path}")
    return yaml_path

def train(yaml_path, epochs, imgsz, batch):
    from ultralytics import YOLO
    
    print(f"--- Starting Training (Epochs={epochs}, ImgSz={imgsz}) ---")
    
    # Folosim modelul nano pentru test
    model = YOLO('yolo11n.pt') 
    
    # Antrenare
    # project='/opt/ml/model' asigura ca artefactele sunt salvate unde trebuie
    # pentru ca SageMaker sa le urce inapoi pe S3 la final
    results = model.train(
        data=yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project='/opt/ml/model', # Folderul special SageMaker pentru output
        name='yolo_run',
        exist_ok=True,
        device='cpu' # Fortam CPU pentru testul ieftin (sau lasam auto daca luam GPU)
    )

if __name__ == '__main__':
    # 1. Instalam dependinte
    install_dependencies()
    
    # Citim hyperparametrii (inclusiv max_images)
    epochs = int(os.environ.get('SM_HP_EPOCHS', 1))
    imgsz = int(os.environ.get('SM_HP_IMGSZ', 640))
    batch = int(os.environ.get('SM_HP_BATCH', 8))
    max_images = int(os.environ.get('SM_HP_MAX_IMAGES', 0)) # 0 = fara limita

    # 2. Pregatim datele
    # Folosim /tmp pentru ca e writable in containerele SageMaker
    yaml_config = prepare_data('/tmp', max_images)
    
    # 4. Start Antrenament
    train(yaml_config, epochs, imgsz, batch)
    
    print("--- Training Finished Successfully ---")
