import json
import os
from pytablewriter import LatexTableWriter

def create_latex_tables():
    with open('classification_results.tex', 'w') as f:
        f.write('\\documentclass{article}\n\\usepackage{booktabs}\n\\begin{document}\n')
        f.write('\\title{LMMs Classification Test Results}\n\\maketitle\n\n')
        
        for filename in os.listdir('LMMs-Classification-Test-Results'):
            if filename.endswith('.json'):
                with open(f'LMMs-Classification-Test-Results/{filename}', 'r') as jf:
                    data = json.load(jf)
                
                model_name = filename.replace('.json', '')
                f.write(f'\\section{{{model_name}}}\n\n')
                
                # Metadata table - improved version
                metadata = None
                if 'metadata' in data:
                    metadata = data['metadata']
                elif 'results' in data and 'metadata' in data['results']:
                    metadata = data['results']['metadata']
                
                if metadata:
                    f.write('\\subsection{Metadata}\n')
                    writer = LatexTableWriter(
                        headers=['Key', 'Value'],
                        value_matrix=[[str(k), str(v)] for k, v in metadata.items()]
                    )
                    f.write(writer.dumps() + '\n\n')
                
                # Classification report table
                report = None
                if 'classification_report' in data:
                    report = data['classification_report']
                elif 'results' in data and 'classification_report' in data['results']:
                    report = data['results']['classification_report']
                
                if report:
                    f.write('\\subsection{Classification Report}\n')
                    headers = ['', 'precision', 'recall', 'f1-score', 'support']
                    value_matrix = []
                    
                    for key, values in report.items():
                        if isinstance(values, dict):
                            row = [key] + [values.get(h, '') for h in headers[1:]]
                            value_matrix.append(row)
                    
                    writer = LatexTableWriter(headers=headers, value_matrix=value_matrix)
                    f.write(writer.dumps() + '\n\n')
                    
                    # Add accuracy line
                    accuracy = report.get('accuracy', 'N/A')
                    f.write(f'Accuracy = {accuracy}\n\n')
        
        f.write('\\end{document}')

create_latex_tables()