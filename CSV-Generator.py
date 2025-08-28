import json
import csv
import os
import sys
from pathlib import Path

def round_numeric_values(value, decimals=4):
    """
    Redondea valores numéricos para mejor legibilidad y convierte el punto decimal a coma
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # Redondear el valor
        rounded_value = round(value, decimals)
        # Convertir a string y cambiar punto por coma
        return str(rounded_value).replace('.', ',')
    return value

def extract_metrics_from_json(json_file_path):
    """
    Extrae las métricas de un archivo JSON de evaluación
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extraer metadata
        metadata = data.get('metadata', {})
        model_name = metadata.get('model_name', 'Unknown')
        model_size = metadata.get('model_size', 'Unknown')
        
        # Crear nombre del modelo concatenando nombre y tamaño
        full_model_name = f"{model_name} ({model_size})"
        
        # Extraer métricas
        results = data.get('results', {})
        classification_report = results.get('classification_report', {})
        timing_metrics = results.get('timing_metrics', {})
        
        # Crear diccionario con todas las métricas
        metrics = {'Model': full_model_name}
        
        # Agregar accuracy si existe
        if 'accuracy' in classification_report:
            metrics['accuracy'] = round_numeric_values(classification_report['accuracy'])
        
        # Agregar métricas de clasificación por clase
        for class_name, class_metrics in classification_report.items():
            if isinstance(class_metrics, dict):
                for metric_name, value in class_metrics.items():
                    key = f"{class_name}_{metric_name}"
                    # Redondear valores numéricos
                    metrics[key] = round_numeric_values(value)
        
        # NO agregar métricas de tiempo ni metadata adicional
        # Solo mantener el modelo, accuracy y las métricas de clasificación
        
        return metrics
        
    except Exception as e:
        print(f"Error procesando {json_file_path}: {str(e)}")
        return None

def generate_csv_for_folder(folder_path):
    """
    Genera un CSV para una carpeta específica
    """
    folder_name = os.path.basename(folder_path)
    csv_filename = f"{folder_name}.csv"
    csv_path = os.path.join(os.path.dirname(folder_path), csv_filename)
    
    print(f"Procesando carpeta: {folder_name}")
    print(f"Generando CSV: {csv_filename}")
    
    # Lista para almacenar todas las métricas
    all_metrics = []
    
    # Procesar todos los archivos JSON en la carpeta
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    if not json_files:
        print(f"No se encontraron archivos JSON en {folder_path}")
        return
    
    print(f"Encontrados {len(json_files)} archivos JSON")
    
    for json_file in json_files:
        json_path = os.path.join(folder_path, json_file)
        metrics = extract_metrics_from_json(json_path)
        
        if metrics:
            all_metrics.append(metrics)
            print(f"  ✓ Procesado: {json_file}")
        else:
            print(f"  ✗ Error procesando: {json_file}")
    
    if not all_metrics:
        print("No se pudieron extraer métricas de ningún archivo")
        return
    
    # Obtener todas las columnas únicas
    all_columns = set()
    for metrics in all_metrics:
        all_columns.update(metrics.keys())
    
    # Organizar columnas en el orden específico requerido
    # 1. Model primero
    ordered_columns = ['Model']
    
    # 2. Accuracy si existe
    if 'accuracy' in all_columns:
        ordered_columns.append('accuracy')
    
    # 3. Métricas por etiqueta (catfishing, harmless, sextortion)
    label_metrics = []
    for label in ['catfishing', 'harmless', 'sextortion']:
        for metric in ['precision', 'recall', 'f1-score']:  # Eliminamos 'support'
            column_name = f"{label}_{metric}"
            if column_name in all_columns:
                label_metrics.append(column_name)
    
    # 4. Métricas agregadas (micro avg, macro avg, weighted avg)
    aggregate_metrics = []
    for avg_type in ['micro avg', 'macro avg', 'weighted avg']:
        for metric in ['precision', 'recall', 'f1-score']:  # Eliminamos 'support'
            column_name = f"{avg_type}_{metric}"
            if column_name in all_columns:
                aggregate_metrics.append(column_name)
    
    # Combinar en el orden deseado
    ordered_columns.extend(label_metrics)
    ordered_columns.extend(aggregate_metrics)
    
    # Escribir CSV con formato europeo (separador ; y decimales con ,)
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ordered_columns, delimiter=';')
            writer.writeheader()
            
            for metrics in all_metrics:
                # Asegurar que todas las columnas estén presentes
                row = {col: metrics.get(col, '') for col in ordered_columns}
                writer.writerow(row)
        
        print(f"✓ CSV generado exitosamente: {csv_path}")
        print(f"  - Modelos procesados: {len(all_metrics)}")
        print(f"  - Columnas de métricas: {len(ordered_columns)}")
        
    except Exception as e:
        print(f"Error escribiendo CSV: {str(e)}")

def main():
    """
    Función principal
    """
    base_path = "LMMs-Classification-Test-Results"
    
    # Verificar si existe el directorio base
    if not os.path.exists(base_path):
        print(f"Error: No se encontró el directorio {base_path}")
        print("Asegúrate de ejecutar el script desde el directorio raíz del proyecto")
        return
    
    # Obtener todas las subcarpetas
    subfolders = [f for f in os.listdir(base_path) 
                 if os.path.isdir(os.path.join(base_path, f))]
    
    if not subfolders:
        print(f"No se encontraron subcarpetas en {base_path}")
        return
    
    print(f"Carpetas encontradas: {subfolders}")
    print("-" * 60)
    
    # Procesar cada carpeta
    for subfolder in subfolders:
        folder_path = os.path.join(base_path, subfolder)
        generate_csv_for_folder(folder_path)
        print("-" * 60)
    
    print("¡Proceso completado!")

if __name__ == "__main__":
    main()