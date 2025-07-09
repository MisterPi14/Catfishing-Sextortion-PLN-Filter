import json
import os
from pytablewriter import LatexTableWriter

DIRECTORY = 'LMMs-Classification-Test-Results/Zero-Shot-Aproach'

def create_latex_tables():
    with open('classification_results.tex', 'w') as f:
        # Cambiar el preámbulo para incluir geometry y el formato correcto
        title_suffix = DIRECTORY.split('/')[-1].replace('-', ' ').replace('_', ' ')
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{booktabs}\n')
        f.write('\\usepackage[top=1.9cm, bottom=3cm, left=1.3cm, right=1.3cm]{geometry}\n\n')
        f.write('\\begin{document}\n')
        f.write(f'\\title{{LMMs Classification Test Results: {title_suffix}}}\\n\\maketitle\\n\\n')
        
        for filename in os.listdir(DIRECTORY):
            if filename.endswith('.json'):
                with open(f'{DIRECTORY}/{filename}', 'r') as jf:
                    data = json.load(jf)
                
                model_name = filename.replace('.json', '').replace('_', '\\_')
                f.write(f'\\section{{{model_name}}}\n')
                
                # Metadata table - improved version
                metadata = None
                if 'metadata' in data:
                    metadata = data['metadata']
                elif 'results' in data and 'metadata' in data['results']:
                    metadata = data['results']['metadata']
                
                if metadata:
                    f.write('\\subsection{Metadata}\n\n')
                    f.write('\\begin{center}\n')
                    f.write('\\begin{tabular}{l | l} \\hline\n')
                    f.write('    \\verb|      Key      | & \\verb|           Value           | \\\\ \\hline\n')
                    f.write('    \\hline\n')
                    
                    for key, value in metadata.items():
                        f.write(f'    \\verb|{key:<14}| & \\verb|{str(value):<29}| \\\\ \\hline\n')
                    
                    f.write('\\end{tabular}\n')
                    f.write('\\end{center}\n\n')
                
                # Timing metrics table
                timing_metrics = None
                if 'timing_metrics' in data:
                    timing_metrics = data['timing_metrics']
                elif 'results' in data and 'timing_metrics' in data['results']:
                    timing_metrics = data['results']['timing_metrics']

                if timing_metrics:
                    f.write('\\subsection{Timing Metrics}\n\n')
                    f.write('\\begin{center}\n')
                    f.write('\\begin{tabular}{l | l} \\hline\n')
                    f.write('    \\verb|      Metric     | & \\verb|           Value           | \\\\ \\hline\n')
                    f.write('    \\hline\n')
                    
                    for key, value in timing_metrics.items():
                        value_str = f'{value:.4f}' if isinstance(value, float) else str(value)
                        f.write(f'    \\verb|{key:<14}| & \\verb|{value_str:<29}| \\\\ \\hline\n')
                    
                    f.write('\\end{tabular}\n')
                    f.write('\\end{center}\n\n')

                # Classification report table
                report = None
                if 'classification_report' in data:
                    report = data['classification_report']
                elif 'results' in data and 'classification_report' in data['results']:
                    report = data['results']['classification_report']
                
                if report:
                    f.write('\\subsection{Classification Report}\n\n')
                    f.write('\\begin{center}\n')
                    f.write('\\begin{tabular}{l | r | r | r | r} \\hline\n')
                    f.write('    \\verb|            | & \\verb|    precision     | & \\verb|      recall      | & \\verb|     f1-score     | & \\verb|support| \\\\ \\hline\n')
                    f.write('    \\hline\n')
                    
                    for key, values in report.items():
                        if isinstance(values, dict):
                            # Modificar el nombre de la clase si es un número
                            if key in ['0', '1']:
                                class_name = f'class {key}'
                            else:
                                class_name = key
                        
                            precision = values.get('precision', '')
                            recall = values.get('recall', '')
                            f1_score = values.get('f1-score', '')
                            support = values.get('support', '')
                            
                            f.write(f'    \\verb|{class_name:<11}| & {precision} & {recall} & {f1_score} & {support:>7} \\\\ \\hline\n')
                    
                    f.write('\\end{tabular}\n')
                    f.write('\\end{center}\n\n')
                    
                    # Add accuracy line centered
                    accuracy = report.get('accuracy', 'N/A')
                    f.write('\\begin{center}\n')
                    f.write(f'Accuracy = {accuracy}\n')
                    f.write('\\end{center}\n\n')
        
        f.write('\\end{document}')

create_latex_tables()