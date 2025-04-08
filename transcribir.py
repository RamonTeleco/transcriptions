import subprocess
import os
import glob
import sys
from pathlib import Path

def process_video(video_path, model_size, output_dir):
    """Procesa un solo video con WhisperX"""
    try:
        # Obtener nombre base del video para crear una subcarpeta específica
        video_basename = os.path.basename(video_path)
        video_name = os.path.splitext(video_basename)[0]
        
        # Crear subcarpeta para este video específico
        video_output_dir = os.path.join(output_dir, video_name)
        os.makedirs(video_output_dir, exist_ok=True)
        
        print(f"\n=== Transcribiendo {video_basename} con WhisperX ===\n")
        
        # Verificar si el archivo existe
        if not os.path.isfile(video_path):
            print(f"Error: No se puede encontrar el archivo {video_path}")
            return False
        
        # Comando para WhisperX
        whisperx_cmd = [
            "whisperx",
            video_path,
            "--model", model_size,
            "--output_dir", video_output_dir,
            "--device", "cpu",  # "cpu" o "cuda" si tienes GPU NVIDIA
            "--align_model", "WAV2VEC2_ASR_BASE_960H",
            "--compute_type", "int8"  # O "float32" si prefieres
            # Omitimos --align_extend
        ]
        
        # Ejecutar el comando y capturar cualquier error
        result = subprocess.run(whisperx_cmd, check=False, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error al procesar {video_basename}")
            print(f"Mensaje de error: {result.stderr}")
            return False
        
        print(f"\nTranscripción de {video_basename} finalizada. Revisa la carpeta '{video_output_dir}'.\n")
        return True
        
    except Exception as e:
        print(f"Error al procesar {video_path}: {str(e)}")
        return False

def check_whisperx_installed():
    """Verifica si WhisperX está instalado correctamente"""
    try:
        # Intentar ejecutar 'whisperx --help' para ver si está instalado
        result = subprocess.run(["whisperx", "--help"], 
                               capture_output=True, 
                               text=True, 
                               check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("Iniciando script de procesamiento de videos con WhisperX...")
    
    # Verificar si WhisperX está instalado
    if not check_whisperx_installed():
        print("Error: WhisperX no está instalado o no se encuentra en el PATH.")
        print("Por favor, instala WhisperX con: pip install git+https://github.com/m-bain/whisperX.git")
        return
    
    # Configuración - puedes modificar estas variables según necesites
    current_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(current_dir, "videos")  # Carpeta donde se encuentran los videos
    model_size = "medium"
    output_dir = os.path.join(current_dir, "whisperx_results")
    
    # Crear carpeta de videos si no existe
    if not os.path.exists(videos_dir):
        print(f"Creando carpeta de videos en: {videos_dir}")
        os.makedirs(videos_dir, exist_ok=True)
        print(f"Por favor, coloca tus videos en la carpeta: {videos_dir}")
        return
    
    # Crear carpeta de resultados si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener lista de todos los videos en la carpeta
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.webm']
    video_files = []
    
    for ext in video_extensions:
        pattern = os.path.join(videos_dir, ext)
        video_files.extend(glob.glob(pattern))
    
    # Si no hay videos en la carpeta 'videos', buscar en el directorio actual
    if not video_files:
        print(f"No se encontraron videos en la carpeta '{videos_dir}'.")
        print("Buscando videos en el directorio actual...")
        
        for ext in video_extensions:
            pattern = os.path.join(current_dir, ext)
            video_files.extend(glob.glob(pattern))
    
    if not video_files:
        print("No se encontraron videos para procesar.")
        print(f"Por favor, coloca tus videos en la carpeta: {videos_dir}")
        print(f"O en el directorio donde se encuentra este script: {current_dir}")
        return
    
    # Mostrar videos encontrados
    print(f"Se encontraron {len(video_files)} videos para procesar:")
    for i, video in enumerate(video_files, 1):
        print(f"{i}. {os.path.basename(video)}")
    print()
    
    # Procesar cada video
    successful = 0
    failed = 0
    
    for video_path in video_files:
        if process_video(video_path, model_size, output_dir):
            successful += 1
        else:
            failed += 1
    
    # Mostrar resumen final
    print("\n" + "="*50)
    print(f"Resumen de procesamiento:")
    print(f"- Videos procesados correctamente: {successful}")
    print(f"- Videos con errores: {failed}")
    print(f"- Total: {len(video_files)}")
    print("="*50)
    
    if successful > 0:
        print(f"\nProcesamiento por lotes completado. Los resultados están en: {output_dir}")

if __name__ == "__main__":
    try:
        # Ejecutar el procesamiento por lotes
        main()
    except KeyboardInterrupt:
        print("\nProcesamiento interrumpido por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
    
    input("\nPresiona Enter para salir...")