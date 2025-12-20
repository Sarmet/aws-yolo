from ultralytics import YOLO

def main():
    """Train YOLO11 model on PPE detection dataset.
    
    Loads pretrained yolo11n.pt model and trains on configured dataset
    for 10 epochs at 640x640 image resolution. Training outputs are saved
    to ppe_training/yolo11_ppe_run/.
    
    Configuration:
        - Model: yolo11n.pt (nano variant)
        - Epochs: 10
        - Image size: 640x640
        - Dataset: Configured in data.yaml
    """
    # Load a model
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)

    # Train the model
    results = model.train(data=r"C:\aws-img-tensor\ppe_detection_yolo\data.yaml", epochs=10, imgsz=640, project="ppe_training", name="yolo11_ppe_run")

if __name__ == "__main__":
    main()
