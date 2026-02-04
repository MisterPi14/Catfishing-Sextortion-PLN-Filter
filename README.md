# Framework de Evaluación de LLMs para Detección de Fraude Digital (PLN Filter)

Este proyecto es un entorno de pruebas diseñado para evaluar la capacidad de diversos Modelos de Lenguaje (LLMs) locales (vía Ollama) para detectar y clasificar intentos de fraude digital en mensajes de texto, específicamente **Catfishing** y **Sextorción**, frente a mensajes inofensivos (**Harmless**).

El enfoque se centra en el análisis de patrones lingüísticos y semánticos del español coloquial de la Ciudad de México.

## 📂 Estructura del Proyecto

### Carpetas Principales

*   **`testDataSet/`**
    *   Contiene los archivos JSON con los mensajes "crudos" que serán sometidos a evaluación.
    *   Se divide en datos `real` (casos reales anonimizados) y `sintetic` (generados para pruebas de estrés).
    *   Es la fuente de verdad para medir la precisión (Accuracy, Precision, Recall, F1) del modelo.

*   **`refinementDataSet/`**
    *   Contiene archivos para **Ingeniería de Prompts (Prompt Engineering)** y estrategias **Few-Shot**.
    *   **Nota Importante:** Los datos aquí alojados **NO SE USAN PARA FINE-TUNING** (re-entrenamiento de pesos). Se utilizan para inyectar contexto dinámico en el prompt del sistema, proporcionando:
        1.  Un diccionario de regionalismos mexicanos.
        2.  Ejemplos demostrativos (Few-Shot samples) para guiar al modelo antes de que realice la predicción.

*   **`LMMs-Classification-Test-Results/`**
    *   Directorio de salida donde se almacenan los resultados de las pruebas.
    *   Se organiza automáticamente según la estrategia utilizada (ej. `Few-Shot-Approach`, `Zero-Shot-Approach`).
    *   Contiene los archivos `.json` crudos generados por el script de evaluación principal.

---

## 🛠️ Scripts y Componentes

### 1. `ModelsClassificationTests.ipynb` (Core de Evaluación)
Es el motor principal del proyecto. Este Notebook orquesta la conexión con Ollama y ejecuta el ciclo de pruebas.

*   **Configuración Flexible:** Permite alternar entre enfoques *Zero-Shot* (solo definiciones) y *Few-Shot* (definiciones + ejemplos + diccionario).
*   **Metodología Stateless / Sin Memoria:**
    
    Este proyecto utiliza un enfoque **Stateless** para garantizar métricas objetivas. Comparativa con el enfoque conversacional tradicional:

    **1. Forma Actual (Stateless / Sin Memoria)**
    Es la que usas ahora:
    ```mermaid
    graph TD
    A[Prompt + Sample 1] --> B(Predicción)
    C[Prompt + Sample 2] --> D(Predicción)
    ```
    *   **Mayor Precisión:** Cada muestra se evalúa con las instrucciones "frescas" y pristinas. El modelo no se distrae.
    *   **Independencia:** La predicción del "Mensaje 50" no se ve influenciada por lo que el modelo respondió en el "Mensaje 49". Esto es crucial para calcular métricas científicas reales (Recall, F1-Score).
    *   **Evita el "Context Drift" (Deriva del Contexto):** En conversaciones largas, los LLMs tienden a "olvidar" las instrucciones iniciales (definiciones de catfishing) a medida que la ventana de contexto se llena con mensajes nuevos.

    **2. Forma "Instancia Abierta" (Stateful / Conversacional)**
    *Enfoque NO utilizado (solo referencia):*
    ```mermaid
    graph TD
    A[Prompt Inicial] --> B(Ok)
    B --> C[Sample 1]
    C --> D(Predicción)
    D --> E[Sample 2]
    E --> F(Predicción...)
    ```
    *   **Riesgo de Sesgo de Auto-Refuerzo:** Si el modelo predice "harmless" 10 veces seguidas, es probable que en la 11ª vez tenga un sesgo estadístico para decir "harmless" de nuevo, ignorando el contenido real, solo porque es el patrón reciente en la conversación.
    *   **Contaminación:** Si el modelo comete un error en el Sample 1, ese error se queda en el historial y puede justificar un error en el Sample 2.
    *   **Límite de Contexto:** Aunque los modelos actuales tienen ventanas grandes, eventualmente se llenan. Cuando esto pasa, lo primero en borrarse suele ser el principio (tus instrucciones y definiciones).
*   **Output:** Genera un archivo JSON detallado por cada modelo evaluado con métricas de tiempo y clasificación.

### 2. `CSV-Generator.py` (Agregador de Resultados)
Herramienta de post-procesamiento para análisis de datos.
*   Escanea los directorios de resultados (`LMMs-Classification-Test-Results`).
*   Extrae las métricas clave de todos los archivos JSON individuales.
*   Genera un archivo `.csv` consolidado que permite comparar fácilmente el rendimiento de todos los modelos lado a lado (Accuracy, F1-Score por categoría, tiempos de inferencia, etc.).
*   Formatea los números para compatibilidad con estándares europeos/latinoamericanos (uso de comas decimales).

### 3. `Tests-Docs-Generator.py` (Generador de Reportes)
Herramienta de documentación automatizada.
*   Toma los archivos JSON de resultados y genera código **LaTeX** (`.tex`).
*   Crea tablas formateadas profesionalmente para:
    *   Metadatos de la prueba.
    *   Métricas de tiempo.
    *   Reportes de clasificación (`precision`, `recall`, `f1-score`, `support`) por clase.
*   Facilita la creación de PDFs académicos o reportes técnicos finales sin necesidad de copiar y pegar datos manualmente.

---

## 🚀 Requisitos Previos

*   **Python 3.x**
*   **Ollama**: Debe estar instalado y ejecutándose (`ollama serve`) localmente.
*   Librerías Python: `scikit-learn`, `ollama`, `pytablewriter` (ver `requirements.txt` si disponible).

## 📊 Flujo de Trabajo Típico

1.  Asegurar que los datos de prueba estén en `testDataSet`.
2.  Ejecutar `ModelsClassificationTests.ipynb` para correr las evaluaciones masivas.
3.  Ejecutar `CSV-Generator.py` para obtener una tabla comparativa rápida en Excel.
4.  Ejecutar `Tests-Docs-Generator.py` para generar la documentación formal en LaTeX.
