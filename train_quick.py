from ultralytics import YOLO

if __name__ == '__main__':
    # 1. Încărcăm modelul cel mai mic și rapid (Nano)
    model = YOLO('yolo11n.pt')

    # 2. Antrenăm rapid pe datele tale (data_balanced.yaml)
    # 20 de epoci ar trebui să fie suficiente pentru a învăța mănușile
    print("Începe antrenarea rapidă...")
    results = model.train(
        data='data_balanced.yaml', 
        epochs=20, 
        imgsz=640, 
        batch=8,            # Batch mic pentru a nu încărca memoria
        project='ppe_training',
        name='yolo11_quick_run',
        exist_ok=True       # Suprascrie folderul dacă există
    )
    print("Antrenare finalizată! Modelul nou este salvat în ppe_training/yolo11_quick_run/weights/best.pt")
