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
    # Expresión regular para encontrar "ARTICULO" o "ARTÍCULO" seguido de números y un punto.
    articles = re.split(r'(?=ART[IÍ]CULO\s+\d+[°º.]?)', full_text, flags=re.IGNORECASE)
    return [article.strip() for article in articles if article and article.strip()]

# Paso 3: Extraer número y título del artículo
def extract_article_info(article_text):
    lines = article_text.split('\n')
    first_line = lines[0].strip() if lines else ""

    match = re.search(r'ART[IÍ]CULO\s+(\d+)[°º.]?\s*[.-]?\s*(.*)', first_line, re.IGNORECASE)
    if match:
        number = match.group(1)
        title = match.group(2).strip().rstrip('.')
        if not title and len(lines) > 1:
            title = lines[1].strip()
        return number, title if title else "Sin título"
        
    return "UNKNOWN", "Sin título"

# Paso 4: Generar preguntas variadas sobre el artículo
def generate_questions_for_article(article_number, article_title):
    if article_number == "UNKNOWN":
        return []
        
    questions = [
        f"¿Qué establece el artículo {article_number} del Código Nacional de Tránsito?",
        f"Explícame el contenido del artículo {article_number}.",
        f"¿Cuál es el contenido del artículo {article_number} sobre {article_title.lower()}?",
        f"Artículo {article_number}: {article_title}",
        f"¿Qué dice la ley de tránsito en el artículo {article_number}?",
        f"Necesito información sobre el artículo {article_number} del código de tránsito."
    ]
    return questions

# Paso 5: Crear ejemplos de entrenamiento en formato OpenAI
def create_training_examples_for_openai(articles):
    training_examples = []
    # El mensaje del sistema se incluye en cada ejemplo para el formato de chat de OpenAI
    system_message = "Eres un asistente experto en el Código Nacional de Tránsito de Colombia (Ley 769 de 2002). Proporciona información precisa y detallada sobre los artículos del código cuando se te consulte."

    for article in articles:
        if not article.strip():
            continue
            
        article_number, article_title = extract_article_info(article)
        
        if article_number == "UNKNOWN":
            continue

        clean_content = article.strip()
        questions = generate_questions_for_article(article_number, article_title)
        
        for question in questions:
            # Formato específico para OpenAI con roles: system, user, assistant
            training_example = {
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": clean_content}
                ]
            }
            training_examples.append(training_example)
            
    return training_examples

# Paso 6: Guardar en formato JSONL
def save_to_jsonl(training_examples, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

# Paso 7: Validar formato del archivo JSONL para OpenAI
def validate_jsonl_format_for_openai(file_path):
    errors = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                if 'messages' not in data:
                    errors.append(f"Línea {line_num}: Falta la clave 'messages'")
                    continue
                    
                messages = data['messages']
                if not isinstance(messages, list):
                    errors.append(f"Línea {line_num}: 'messages' debe ser una lista")
                    continue
                
                # Verificar roles válidos para OpenAI
                valid_roles = {'system', 'user', 'assistant'}
                for msg_idx, message in enumerate(messages):
                    if 'role' not in message or 'content' not in message:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx+1}: Falta 'role' o 'content'")
                    elif message.get('role') not in valid_roles:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx+1}: Rol inválido '{message.get('role')}'")

            except json.JSONDecodeError as e:
                errors.append(f"Línea {line_num}: Error de JSON - {str(e)}")
                
    return errors

# Ejecutar el proceso
if __name__ == "__main__":
    pdf_path = "ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf" 
    output_path = "articulos_ley_769_openai.jsonl"
    
    print("Extrayendo texto del PDF...")
    full_text = extract_text_from_pdf(pdf_path)
    
    if full_text:
        print("Dividiendo por artículos...")
        articles = split_by_articles(full_text)
        print(f"  Encontrados {len(articles)} bloques de artículos")
        
        print("Creando ejemplos de entrenamiento para OpenAI...")
        training_examples = create_training_examples_for_openai(articles)
        print(f"  Generados {len(training_examples)} ejemplos de entrenamiento")
        
        print(f"Guardando ejemplos en {output_path}...")
        save_to_jsonl(training_examples, output_path)
        
        print("Validando formato del archivo para OpenAI...")
        validation_errors = validate_jsonl_format_for_openai(output_path)
        
        if validation_errors:
            print("ERROR: Se encontraron errores de formato:")
            for error in validation_errors[:10]:
                print(f"  {error}")
            if len(validation_errors) > 10:
                print(f"  ... y {len(validation_errors) - 10} errores más")
        else:
            print("EXITO: Archivo JSONL generado y validado exitosamente para fine-tuning de OpenAI.")
            print(f"  Total de ejemplos: {len(training_examples)}")
            print(f"  Archivo: {output_path}")
            print("\nEl archivo está listo para subirse a la plataforma de OpenAI.")
