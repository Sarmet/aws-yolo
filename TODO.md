# Plan de lucru - Proiect PPE (Casti si Manusi)

## Obiectiv
Extinderea detectiei pentru a include **casti** (helmet) si **manusi** (glove) cu precizie ridicata.

## Pasi de urmat

1.  **Verificare Dataset**:
    *   Verifica daca etichetele din `datasets/ppe_balanced` contin clasele pentru manusi (`glove`, `no_glove`).
    *   Analizeaza distributia claselor (cate instante de `helmet` vs `glove` avem).

2.  **Antrenament (Fine-tuning)**:
    *   Configureaza antrenamentul pentru a pune accent pe clasele `helmet` si `glove`.
    *   Ruleaza antrenamentul folosind `train_yolo11.py` (sau un script nou dedicat) pe noul dataset din `c:\aws-yolo`.
    *   Salveaza noul model (ex: `ppe_training/yolo11_helmet_glove`).

3.  **Validare si Testare**:
    *   Foloseste `validation.ipynb` pentru a testa noul model.
    *   Ruleaza predictii pe cele 5 imagini din `demo_images`.
    *   Verifica vizual daca manusile sunt detectate corect alaturi de casti.

## Resurse
*   Dataset: `datasets/ppe_balanced`
*   Config: `data_balanced.yaml`
*   Model curent: `ppe_training/yolo11_balanced/weights/best.pt`
