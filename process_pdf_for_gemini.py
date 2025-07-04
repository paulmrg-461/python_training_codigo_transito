import json
from PyPDF2 import PdfReader
import re

# Paso 1: Extraer texto del PDF
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        return ""

# Paso 2: Dividir en bloques (ej: por artículo)
def split_by_articles(full_text):
    # Usa una expresión regular para encontrar los artículos de forma más robusta
    # Esto busca "ARTICULO" o "ARTÍCULO" seguido de números y un punto.
    articles = re.split(r'(?=ART[IÍ]CULO\s+\d+[°º.]?)', full_text, flags=re.IGNORECASE)
    
    # El primer elemento del split suele ser el texto antes del primer artículo, lo filtramos si está vacío
    return [article.strip() for article in articles if article and article.strip()]

# Paso 3: Extraer número y título del artículo
def extract_article_info(article_text):
    lines = article_text.split('\n')
    first_line = lines[0].strip() if lines else ""

    # Patrón mejorado para "ARTÍCULO X°." o "ARTÍCULO X."
    match = re.search(r'ART[IÍ]CULO\s+(\d+)[°º.]?\s*[.-]?\s*(.*)', first_line, re.IGNORECASE)
    if match:
        number = match.group(1)
        title = match.group(2).strip().rstrip('.')
        # Si el título está vacío, intenta tomar la siguiente línea
        if not title and len(lines) > 1:
            title = lines[1].strip()
        return number, title if title else "Sin título"
        
    return "UNKNOWN", "Sin título"

# Paso 4: Generar preguntas variadas sobre el artículo
def generate_questions_for_article(article_number, article_title):
    # No incluimos el contenido aquí, ya que no es necesario para generar las preguntas
    if article_number == "UNKNOWN":
        return [] # No generar preguntas si no podemos identificar el artículo
        
    questions = [
        f"¿Qué establece el artículo {article_number} del Código Nacional de Tránsito?",
        f"Explícame el contenido del artículo {article_number}.",
        f"¿Cuál es el contenido del artículo {article_number} sobre {article_title.lower()}?",
        f"Artículo {article_number}: {article_title}",
        f"¿Qué dice la ley de tránsito en el artículo {article_number}?",
        f"Necesito información sobre el artículo {article_number} del código de tránsito."
    ]
    return questions

# Paso 5: Crear ejemplos de entrenamiento en formato Gemini
def create_training_examples(articles):
    training_examples = []
    for article in articles:
        if not article.strip():
            continue
            
        article_number, article_title = extract_article_info(article)
        
        # Si no se pudo extraer un número de artículo, saltamos este bloque
        if article_number == "UNKNOWN":
            continue

        # Limpiar el contenido del artículo
        clean_content = article.strip()
        
        # Generar múltiples preguntas para este artículo
        questions = generate_questions_for_article(article_number, article_title)
        
        # Crear ejemplos de entrenamiento para cada pregunta
        for question in questions:
            training_example = {
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "model", "content": clean_content}
                ]
            }
            training_examples.append(training_example)
            
    return training_examples

# Paso 6: Guardar en formato JSONL para fine-tuning
def save_to_jsonl_finetuning(training_examples, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

# Paso 7: Validar formato del archivo JSONL para Gemini
def validate_jsonl_format_for_gemini(file_path):
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Verificar que tenga la clave 'messages'
                if 'messages' not in data:
                    errors.append(f"Línea {line_num}: Falta la clave 'messages'")
                    continue
                    
                messages = data['messages']
                if not isinstance(messages, list):
                    errors.append(f"Línea {line_num}: 'messages' debe ser una lista")
                    continue
                
                # Verificar la estructura de los mensajes
                if len(messages) != 2:
                     errors.append(f"Línea {line_num}: Debe haber exactamente 2 mensajes (user, model)")
                     continue

                if messages[0].get('role') != 'user' or messages[1].get('role') != 'model':
                    errors.append(f"Línea {line_num}: Los roles deben ser 'user' y luego 'model'.")

                # Verificar que cada mensaje tenga 'role' y 'content'
                for msg_idx, message in enumerate(messages):
                    if 'role' not in message:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx+1}: Falta 'role'")
                    if 'content' not in message:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx+1}: Falta 'content'")

            except json.JSONDecodeError as e:
                errors.append(f"Línea {line_num}: Error de JSON - {str(e)}")
                
    return errors

# Ejecutar el proceso
if __name__ == "__main__":
    # Asegúrate de que el nombre del archivo PDF sea correcto y esté en la misma carpeta
    pdf_path = "ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf" 
    output_path = "articulos_ley_769_gemini.jsonl"
    
    print("Extrayendo texto del PDF...")
    full_text = extract_text_from_pdf(pdf_path)
    
    if full_text:
        print("Dividiendo por artículos...")
        articles = split_by_articles(full_text)
        print(f"  Encontrados {len(articles)} bloques de artículos")
        
        print("Creando ejemplos de entrenamiento para fine-tuning...")
        training_examples = create_training_examples(articles)
        print(f"  Generados {len(training_examples)} ejemplos de entrenamiento")
        
        print(f"Guardando ejemplos en {output_path}...")
        save_to_jsonl_finetuning(training_examples, output_path)
        
        print("Validando formato del archivo para Gemini...")
        validation_errors = validate_jsonl_format_for_gemini(output_path)
        
        if validation_errors:
            print("ERROR: Se encontraron errores de formato:")
            for error in validation_errors[:10]:  # Mostrar solo los primeros 10 errores
                print(f"  {error}")
            if len(validation_errors) > 10:
                print(f"  ... y {len(validation_errors) - 10} errores más")
        else:
            print("EXITO: Archivo JSONL generado y validado exitosamente para fine-tuning de Gemini.")
            print(f"  Total de ejemplos: {len(training_examples)}")
            print(f"  Archivo: {output_path}")
            print("\nEl archivo está listo para el proceso de fine-tuning en Google AI Studio o a través de la API de Gemini.")
