#en este archivo quiero hacer un codigo que cree un archivo .tex donde se hagan tablas con esta informacion de los JSON dentro del directorio "LMMs-Classification-Test-Results" y se ponga un titulo con el nombre del modelo por cada tabla pero que lo haga leyendo todos los JSON dentro del directorio, ponle un titulo general al documento


import json
import os

def create_latex_tables():
    # Directorio con los archivos JSON
    json_dir = "LMMs-Classification-Test-Results"
    
    # Contenido inicial del documento LaTeX
    latex_content = """\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{booktabs}
\\usepackage{longtable}
\\usepackage{geometry}
\\geometry{margin=1in}

\\title{Resultados de Clasificación de Modelos LMM}
\\author{}
\\date{}

\\begin{document}
\\maketitle

"""
    
    # Verificar si el directorio existe
    if not os.path.exists(json_dir):
        print(f"El directorio {json_dir} no existe")
        return
    
    # Obtener todos los archivos JSON del directorio
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    for json_file in json_files:
        file_path = os.path.join(json_dir, json_file)
        model_name = os.path.splitext(json_file)[0]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Agregar título del modelo
            latex_content += f"\\section{{{model_name}}}\n\n"
            
            # Crear tabla con los datos del JSON
            latex_content += "\\begin{longtable}{|l|l|}\n"
            latex_content += "\\hline\n"
            latex_content += "\\textbf{Métrica} & \\textbf{Valor} \\\\\n"
            latex_content += "\\hline\n"
            
            # Procesar los datos del JSON
            def add_json_data(obj, prefix=""):
                for key, value in obj.items():
                    if isinstance(value, dict):
                        add_json_data(value, f"{prefix}{key}.")
                    else:
                        metric_name = f"{prefix}{key}".replace("_", "\\_")
                        if isinstance(value, float):
                            value_str = f"{value:.4f}"
                        else:
                            value_str = str(value).replace("_", "\\_")
                        latex_content_local = f"{metric_name} & {value_str} \\\\\n"
                        return latex_content_local
                return ""
            
            # Agregar datos a la tabla
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        metric_name = f"{key}.{sub_key}".replace("_", "\\_")
                        if isinstance(sub_value, float):
                            value_str = f"{sub_value:.4f}"
                        else:
                            value_str = str(sub_value).replace("_", "\\_")
                        latex_content += f"{metric_name} & {value_str} \\\\\n"
                        latex_content += "\\hline\n"
                else:
                    metric_name = key.replace("_", "\\_")
                    if isinstance(value, float):
                        value_str = f"{value:.4f}"
                    else:
                        value_str = str(value).replace("_", "\\_")
                    latex_content += f"{metric_name} & {value_str} \\\\\n"
                    latex_content += "\\hline\n"
            
            latex_content += "\\end{longtable}\n\n"
            latex_content += "\\clearpage\n\n"
            
        except Exception as e:
            print(f"Error procesando {json_file}: {e}")
    
    # Cerrar el documento
    latex_content += "\\end{document}"
    
    # Escribir el archivo .tex
    with open("resultados_modelos.tex", 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print("Archivo resultados_modelos.tex creado exitosamente")

if __name__ == "__main__":
    create_latex_tables()