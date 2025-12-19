# AWS SageMaker - Training YOLO pe Cloud

Documentație pentru antrenarea modelelor YOLO pe AWS SageMaker folosind PowerShell CLI.

## 🎯 Scop

Pipeline complet pentru antrenarea modelelor YOLO în cloud cu AWS SageMaker:
- ✅ Bypass SDK Python issues (SageMaker SDK v3 are probleme cu `sagemaker.pytorch`)
- ✅ Folosește AWS CLI direct din PowerShell
- ✅ Cost-eficient (CPU instances, configurație Spot/On-Demand)
- ✅ Testabil rapid (smoke tests cu 200 imagini)

## 📋 Prerequisite

### 1. AWS CLI Instalat și Configurat

```powershell
# Verifică AWS CLI
aws --version

# Configurează credentials (dacă nu ai deja)
aws configure
```

**Credentials necesare** (în `~/.aws/credentials`):
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### 2. Python Environment

```powershell
# Crează environment Python 3.11 (NECESAR pentru SageMaker SDK compatibility)
py -3.11 -m venv .venv-sagemaker
.venv-sagemaker\Scripts\Activate.ps1

# Instalează pachete
pip install boto3 ultralytics
```

**NOTĂ:** SageMaker SDK v3 are bug-uri. Folosim AWS CLI în loc de Python SDK!

## 🗂️ Structura Fișierelor

```
c:\aws-yolo\
├── train_entrypoint.py        # Script antrenament (rulează în container)
├── launch_sagemaker_cli.ps1   # Launcher PowerShell (AWS CLI)
├── upload_data_s3.py          # Upload date pe S3
├── datasets/                  # Date locale
│   └── ppe_balanced/
├── demo_images/               # Imagini test
└── best.pt                    # Model antrenat (descărcat din S3)
```

## 🚀 Workflow Complet

### Pasul 1: Upload Date pe S3

```powershell
# Activează environment
.venv-sagemaker\Scripts\Activate.ps1

# Rulează upload (arhivează datasets/ + demo_images/ → S3)
python upload_data_s3.py
```

**Output:**
- Arhivă: `temp_pack_for_s3/data.zip` (~1.6 GB)
- S3: `s3://radu-yolo-data/data.zip`

### Pasul 2: Pregătește Scriptul de Training

Fișierul `train_entrypoint.py` conține logica de antrenament:
- Descarcă și extrage `data.zip` din `/opt/ml/input/data/training/`
- Instalează Ultralytics în container
- Limitează dataset la `max_images` per clasă
- Antrenează YOLO cu hyperparametrii din env vars
- Salvează `best.pt` în `/opt/ml/model/` (uplodat automat pe S3)

**Upload script pe S3:**
```powershell
# Creează tar.gz
tar -czf sourcedir.tar.gz train_entrypoint.py

# Upload
aws s3 cp sourcedir.tar.gz s3://radu-yolo-data/code/ --region us-east-1
```

### Pasul 3: Creează IAM Role (Dacă nu există)

```powershell
# Creează rol cu politica SageMaker
aws iam create-role --role-name SageMakerExecutionRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "sagemaker.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}'

# Attach politici
aws iam attach-role-policy --role-name SageMakerExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam attach-role-policy --role-name SageMakerExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Pasul 4: Lansează Training Job

```powershell
# Editează parametrii în launch_sagemaker_cli.ps1 dacă e necesar
# Apoi rulează:
.\launch_sagemaker_cli.ps1
```

**Parametrii configurabili în script:**
- `epochs`: Număr epoci (1 pentru smoke test)
- `imgsz`: Rezoluție imagini (640 standard)
- `batch`: Batch size (8 pentru CPU)
- `max_images`: Limite imagini per clasă (200 pentru test rapid)

**Instance types:**
- **CPU:** `ml.m5.large` (~$0.12/oră) - recomandat pentru teste
- **GPU:** `ml.p3.2xlarge` (~$3/oră) - pentru training serios

**Spot vs On-Demand:**
```powershell
# Spot Instances (mai ieftin, dar poate fi întrerupt)
"EnableManagedSpotTraining": true,
"MaxWaitTimeInSeconds": 1800

# On-Demand (garantat, dar mai scump)
# ⚠️ Șterge liniile de mai sus
```

### Pasul 5: Monitorizează Job-ul

#### În AWS Console
```
SageMaker → Training jobs → yolo-test-TIMESTAMP
```

#### În Terminal (PowerShell)
```powershell
# Status job
aws sagemaker describe-training-job --training-job-name yolo-test-TIMESTAMP --region us-east-1 --query TrainingJobStatus

# Logs CloudWatch
aws logs filter-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name-prefix yolo-test-TIMESTAMP --region us-east-1
```

### Pasul 6: Descarcă Modelul Antrenat

```powershell
# Verifică output S3
aws s3 ls s3://radu-yolo-data/output/ --recursive --region us-east-1

# Descarcă model.tar.gz
aws s3 cp s3://radu-yolo-data/output/yolo-test-TIMESTAMP/output/model.tar.gz . --region us-east-1

# Extrage best.pt
tar -xzf model.tar.gz
```

### Pasul 7: Testează Modelul Local

```powershell
# Activează environment
.venv-sagemaker\Scripts\Activate.ps1

# Test rapid cu Python
python -c "from ultralytics import YOLO; model = YOLO('best.pt'); results = model('demo_images/005302_jpg.rf.6f3709a257117249dc503de98fcb5f5d.jpg'); print(f'Detectii: {len(results[0].boxes)}')"
```

**Output așteptat:**
```
image 1/1 ...: 640x512 1 helmet, 160.5ms
Speed: 35.5ms preprocess, 160.5ms inference, 15.2ms postprocess
Detectii: 1
```

## 💰 Costuri Estimate

### Smoke Test (200 imagini, 1 epocă, CPU)
- **Instance:** ml.m5.large
- **Timp:** ~9 minute
- **Cost:** $0.018 (2 cenți!)

### Training Serios (dataset complet, 50 epoci, GPU)
- **Instance:** ml.p3.2xlarge
- **Timp:** ~2-3 ore
- **Cost:** $6-9 (fără Spot), $3-5 (cu Spot)

### Storage S3
- **data.zip (1.6 GB):** $0.037/lună
- **model.tar.gz (14 MB):** $0.0003/lună

## 🛠️ Troubleshooting

### ❌ "Insufficient capacity error from EC2"
**Cauză:** Spot Instances nu sunt disponibile în us-east-1

**Soluție:**
```powershell
# În launch_sagemaker_cli.ps1, șterge:
# "EnableManagedSpotTraining": true,
# "MaxWaitTimeInSeconds": 1800,
```

### ❌ "No module named 'sagemaker.pytorch'"
**Cauză:** SageMaker SDK v3 a eliminat modulul `pytorch`

**Soluție:** Folosește `launch_sagemaker_cli.ps1` (AWS CLI) în loc de Python SDK

### ❌ "AccessDeniedException"
**Cauză:** IAM role lipsă sau permissions insuficiente

**Soluție:**
```powershell
# Verifică role ARN
aws iam get-role --role-name SageMakerExecutionRole

# Verifică politici atașate
aws iam list-attached-role-policies --role-name SageMakerExecutionRole
```

### ❌ Training job "Failed"
**Cauză:** Eroare în `train_entrypoint.py`

**Soluție:**
```powershell
# Citește logs complete
aws logs tail /aws/sagemaker/TrainingJobs --log-stream-name-prefix yolo-test-TIMESTAMP --follow
```

## 📊 Metrici Training

Jobul salvează automat:
- `model.tar.gz`: Model final + best.pt
- CloudWatch Logs: Output complet (epoci, loss, mAP)

**Verifică metrici finale:**
```powershell
aws sagemaker describe-training-job --training-job-name yolo-test-TIMESTAMP --query '{
    Status: TrainingJobStatus,
    BillableSeconds: BillableTimeInSeconds,
    MetricData: FinalMetricDataList
}'
```

## 🔄 Next Steps

1. **Optimizare Hyperparametri:**
   - Crește `epochs` (50-100 pentru producție)
   - Ajustează `batch` (mai mare pe GPU)
   - Elimină `max_images` pentru dataset complet

2. **Deploy Model:**
   ```powershell
   # Creează endpoint SageMaker
   aws sagemaker create-model --model-name yolo-ppe --primary-container Image=...,ModelDataUrl=s3://...
   ```

3. **Automatizare:**
   - Creează script Git hooks pentru re-training automat
   - Configurează CloudWatch Events pentru training periodic

## 📚 Referințe

- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [AWS CLI Reference](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sagemaker/index.html)

---

**Versiune:** 1.0 (Decembrie 2025)  
**Autor:** Testare AWS SageMaker cu YOLO  
**Status:** ✅ Validat (smoke test success)
