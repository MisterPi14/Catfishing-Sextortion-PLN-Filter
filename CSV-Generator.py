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

def parse_size_to_bytes(size_value):
    """
    Convierte un valor de tamano como "1.0 GB" a bytes (base 2).
    """
    if not isinstance(size_value, str):
        return None

    text = size_value.strip().lower()
    if not text or text == 'unknown':
        return None

    parts = text.split()
    if len(parts) != 2:
        return None

    number_text, unit = parts
    try:
        number_value = float(number_text)
    except ValueError:
        return None

    unit_map = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 ** 2,
        'gb': 1024 ** 3,
        'tb': 1024 ** 4,
    }

    if unit not in unit_map:
        return None

    return int(number_value * unit_map[unit])

def extract_metrics_from_json(json_file_path):
    """
    Extrae solo las métricas de clasificación de un archivo JSON de evaluación
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extraer metadata
        metadata = data.get('metadata', {})
        model_name = metadata.get('model_name', 'Unknown')
        model_size = metadata.get('model_size', 'Unknown')
        model_billion_parameters = metadata.get('model_billion_parameters', '')
        
        # Crear nombre del modelo concatenando nombre y tamaño
        full_model_name = f"{model_name} ({model_size})"
        
        # Extraer métricas
        results = data.get('results', {})
        classification_report = results.get('classification_report', {})
        
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
        
        return metrics
        
    except Exception as e:
        print(f"Error procesando {json_file_path}: {str(e)}")
        return None

def extract_model_metadata_from_json(json_file_path):
    """
    Extrae metadata de un archivo JSON de evaluación
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        metadata = data.get('metadata', {})
        model_name = metadata.get('model_name', 'Unknown')
        model_size = metadata.get('model_size', 'Unknown')
        model_billion_parameters = metadata.get('model_billion_parameters', '')

        full_model_name = f"{model_name} ({model_size})"

        metrics = {'Model': full_model_name}

        if model_billion_parameters != '':
            metrics['metadata.model_billion_parameters'] = round_numeric_values(model_billion_parameters)

        model_size_bytes = parse_size_to_bytes(model_size)
        if model_size_bytes is not None:
            metrics['metadata.model_size_bytes'] = str(model_size_bytes)

        return metrics

    except Exception as e:
        print(f"Error procesando {json_file_path}: {str(e)}")
        return None

def extract_timing_metrics_from_json(json_file_path):
    """
    Extrae timing metrics de un archivo JSON de evaluación
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        metadata = data.get('metadata', {})
        model_name = metadata.get('model_name', 'Unknown')
        model_size = metadata.get('model_size', 'Unknown')

        full_model_name = f"{model_name} ({model_size})"

        results = data.get('results', {})
        timing_metrics = results.get('timing_metrics', {})

        metrics = {'Model': full_model_name}

        average_time = timing_metrics.get('average_time_per_prediction_seconds', '')
        total_time = timing_metrics.get('total_evaluation_time_seconds', '')

        if average_time != '':
            metrics['timing_metrics.average_time_per_prediction_seconds'] = round_numeric_values(average_time)

        if total_time != '':
            metrics['timing_metrics.total_evaluation_time_seconds'] = round_numeric_values(total_time)

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
    
    # 5. Métricas por etiqueta (catfishing, harmless, sextortion)
    label_metrics = []
    for label in ['catfishing', 'harmless', 'sextortion']:
        for metric in ['precision', 'recall', 'f1-score']:  # Eliminamos 'support'
            column_name = f"{label}_{metric}"
            if column_name in all_columns:
                label_metrics.append(column_name)
    
    # 6. Métricas agregadas (micro avg, macro avg, weighted avg)
    aggregate_metrics = []
    for avg_type in ['micro avg', 'macro avg', 'weighted avg']:
        for metric in ['precision', 'recall', 'f1-score']:  # Eliminamos 'support'
            column_name = f"{avg_type}_{metric}"
            if column_name not in aggregate_metrics:
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

def generate_metadata_csv(base_path, subfolders):
    """
    Genera un CSV con metadata de todas las carpetas
    """
    csv_filename = "Model-Metadata.csv"
    csv_path = os.path.join(base_path, csv_filename)

    all_metrics = []

    seen = set()

    for subfolder in subfolders:
        folder_path = os.path.join(base_path, subfolder)
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

        for json_file in json_files:
            json_path = os.path.join(folder_path, json_file)
            metrics = extract_model_metadata_from_json(json_path)
            if metrics:
                model_key = metrics.get('Model', '')
                if model_key and model_key not in seen:
                    seen.add(model_key)
                    all_metrics.append(metrics)

    if not all_metrics:
        print("No se pudieron extraer metadata de ningún archivo")
        return

    ordered_columns = [
        'Model',
        'metadata.model_billion_parameters',
        'metadata.model_size_bytes'
    ]

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ordered_columns, delimiter=';')
            writer.writeheader()

            for metrics in all_metrics:
                row = {col: metrics.get(col, '') for col in ordered_columns}
                writer.writerow(row)

        print(f"✓ CSV generado exitosamente: {csv_path}")
        print(f"  - Modelos procesados: {len(all_metrics)}")
        print(f"  - Columnas de metadata: {len(ordered_columns)}")

    except Exception as e:
        print(f"Error escribiendo CSV: {str(e)}")

def generate_timing_csv(base_path, subfolder, csv_filename):
    """
    Genera un CSV con timing metrics para una carpeta específica
    """
    csv_path = os.path.join(base_path, csv_filename)

    all_metrics = []

    folder_path = os.path.join(base_path, subfolder)
    if not os.path.isdir(folder_path):
        print(f"No se encontró la carpeta {subfolder}")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    for json_file in json_files:
        json_path = os.path.join(folder_path, json_file)
        metrics = extract_timing_metrics_from_json(json_path)
        if metrics:
            all_metrics.append(metrics)

    if not all_metrics:
        print(f"No se pudieron extraer timing metrics en {subfolder}")
        return

    ordered_columns = [
        'Model',
        'timing_metrics.average_time_per_prediction_seconds',
        'timing_metrics.total_evaluation_time_seconds'
    ]

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ordered_columns, delimiter=';')
            writer.writeheader()

            for metrics in all_metrics:
                row = {col: metrics.get(col, '') for col in ordered_columns}
                writer.writerow(row)

        print(f"✓ CSV generado exitosamente: {csv_path}")
        print(f"  - Modelos procesados: {len(all_metrics)}")
        print(f"  - Columnas de timing: {len(ordered_columns)}")

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
    
    # Procesar cada carpeta (CSV de métricas)
    for subfolder in subfolders:
        folder_path = os.path.join(base_path, subfolder)
        generate_csv_for_folder(folder_path)
        print("-" * 60)

    # Generar CSV de metadata
    generate_metadata_csv(base_path, subfolders)

    # Generar CSV de timing por approach
    generate_timing_csv(base_path, 'Few-Shot-Approach', 'Model-Timing-Metrics-Few-Shot.csv')
    generate_timing_csv(base_path, 'Zero-Shot-Approach', 'Model-Timing-Metrics-Zero-Shot.csv')
    
    print("¡Proceso completado!")

if __name__ == "__main__":
    main()