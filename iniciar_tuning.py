import os
import vertexai
from google.cloud import storage
from google.api_core import exceptions

# ------------------------------------------------------------------
# ACCIÓN REQUERIDA: Edita la siguiente línea con tu información
# ------------------------------------------------------------------
PROJECT_ID = "141117906850"  # Reemplaza con tu ID de Proyecto de Google Cloud
# ------------------------------------------------------------------

# --- Valores pre-configurados (no necesitas cambiar esto)---
REGION = "us-central1"
BUCKET_NAME = "bucket-codigo-transito-devpaul-2025"
LOCAL_JSONL_PATH = "articulos_ley_769_gemini.jsonl"
MODEL_DISPLAY_NAME = "ley-transito-colombia-v1"
# ------------------------------------------------------------------

# Validar que el PROJECT_ID ha sido cambiado
if "tu-project-id" in PROJECT_ID:
    print("¡ERROR! Falta un paso importante.")
    print(f"Por favor, abre el archivo 'iniciar_tuning.py' y reemplaza 'tu-project-id' con tu ID de proyecto de Google Cloud.")
    exit()

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Sube un archivo local a un bucket de GCS, creándolo si no existe."""
    storage_client = storage.Client(project=PROJECT_ID)
    
    try:
        bucket = storage_client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' ya existe.")
    except exceptions.NotFound:
        print(f"Bucket '{bucket_name}' no encontrado. Creándolo en la región {REGION}...")
        bucket = storage_client.create_bucket(bucket_name, location=REGION)
        print(f"Bucket '{bucket_name}' creado exitosamente.")

    blob = bucket.blob(destination_blob_name)
    
    print(f"Subiendo archivo '{source_file_path}' a 'gs://{bucket_name}/{destination_blob_name}'...")
    blob.upload_from_filename(source_file_path)
    print("Archivo subido exitosamente.")
    
    return f"gs://{bucket_name}/{destination_blob_name}"

def tune_gemini_model(project_id, region, training_data_uri, model_display_name):
    """Inicia un trabajo de fine-tuning para un modelo Gemini."""
    print(f"Inicializando Vertex AI para el proyecto '{project_id}' en la región '{region}'...")
    vertexai.init(project=project_id, location=region)
    
    base_model = vertexai.generative_models.GenerativeModel("gemini-1.0-pro-002")
    
    print(f"Iniciando trabajo de fine-tuning para el modelo '{model_display_name}'...")
    print(f"Usando datos de entrenamiento: {training_data_uri}")
    
    tuning_job = base_model.tune(
        training_data=training_data_uri,
        model_display_name=model_display_name,
        train_steps=100,
        tuning_job_location="europe-west4",
        tuned_model_location=region,
    )
    
    print("\n¡Trabajo de fine-tuning iniciado!")
    print(f"ID del Job: {tuning_job.resource_name}")
    print(f"Para monitorear el progreso, visita la consola de Vertex AI en tu proyecto.")

if __name__ == "__main__":
    gcs_uri = upload_to_gcs(BUCKET_NAME, LOCAL_JSONL_PATH, LOCAL_JSONL_PATH)
    tune_gemini_model(PROJECT_ID, REGION, gcs_uri, MODEL_DISPLAY_NAME)
