from ultralytics import YOLO

def main():
    # Load a model
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)

    # Train the model
    results = model.train(data=r"C:\aws-img-tensor\ppe_detection_yolo\data.yaml", epochs=10, imgsz=640, project="ppe_training", name="yolo11_ppe_run")

if __name__ == "__main__":
    main()
