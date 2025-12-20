"""Upload PPE detection dataset to S3 for SageMaker training.

This script packages datasets and demo images into a zip archive
and uploads to the configured S3 bucket for use in SageMaker training jobs.
"""

import boto3
import shutil
import os

# Configurare
BUCKET_NAME = 'radu-yolo-data'
REGION = 'us-east-1'
TEMP_DIR = 'temp_pack_for_s3'
ARCHIVE_NAME = 'data' # va rezulta data.zip

def main():
    """Package and upload training data to S3.
    
    Process:
        1. Verify or create S3 bucket in us-east-1
        2. Copy datasets/ and demo_images/ to temporary directory
        3. Create zip archive from temporary directory
        4. Upload zip archive to S3 bucket
        5. Clean up temporary files
    
    The resulting archive is uploaded to s3://radu-yolo-data/data.zip
    and can be used as input for SageMaker training jobs.
    
    Raises:
        Exception: If bucket creation, archiving, or upload fails
    """
    s3 = boto3.client('s3', region_name=REGION)

    # 1. Creare Bucket
    print(f"--- Pasul 1: Verificare/Creare Bucket '{BUCKET_NAME}' ---")
    try:
        # Verificam daca exista
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket-ul '{BUCKET_NAME}' exista deja.")
    except:
        print(f"Bucket-ul nu exista. Il cream in {REGION}...")
        try:
            if REGION == 'us-east-1':
                s3.create_bucket(Bucket=BUCKET_NAME)
            else:
                s3.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={'LocationConstraint': REGION}
                )
            print("Bucket creat cu succes!")
        except Exception as e:
            print(f"Eroare la crearea bucket-ului: {e}")
            return

    # 2. Pregatire si Arhivare
    print(f"\n--- Pasul 2: Pregatire arhiva (Datasets + Demo Images) ---")
    
    # Curatam folderul temporar daca exista
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    try:
        # Copiem structura in folderul temporar
        # Vrem ca in zip sa avem: /datasets si /demo_images
        print("Copiere datasets...")
        shutil.copytree('datasets', os.path.join(TEMP_DIR, 'datasets'))
        
        print("Copiere demo_images...")
        shutil.copytree('demo_images', os.path.join(TEMP_DIR, 'demo_images'))

        # Arhivare
        print(f"Creare arhiva {ARCHIVE_NAME}.zip...")
        shutil.make_archive(ARCHIVE_NAME, 'zip', TEMP_DIR)
        zip_file = ARCHIVE_NAME + '.zip'
        
        size_mb = os.path.getsize(zip_file) / 1024 / 1024
        print(f"Arhiva creata: {zip_file} ({size_mb:.2f} MB)")

    except Exception as e:
        print(f"Eroare la arhivare: {e}")
        return
    finally:
        # Curatenie folder temporar
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)

    # 3. Upload pe S3
    print(f"\n--- Pasul 3: Upload pe S3 ---")
    try:
        print(f"Urcam {zip_file} in {BUCKET_NAME}...")
        s3.upload_file(zip_file, BUCKET_NAME, zip_file)
        print(f"Succes! Datele sunt acum la: s3://{BUCKET_NAME}/{zip_file}")
    except Exception as e:
        print(f"Eroare la upload: {e}")

    # Curatenie zip local (optional, il lasam momentan sa vezi ce a facut)
    # os.remove(zip_file)

if __name__ == '__main__':
    main()
