import json
from PyPDF2 import PdfReader
import re

# Paso 1: Extraer texto del PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Paso 2: Dividir en bloques (ej: por artículo)
def split_by_articles(full_text):
    articles = []
    current_article = ""
    
    for line in full_text.split('\n'):
        if line.strip().upper().startswith("ARTÍCULO") or line.strip().upper().startswith("CAPÍTULO"):
            if current_article:
                articles.append(current_article.strip())
            current_article = line + "\n"
        else:
            current_article += line + "\n"
    
    if current_article:
        articles.append(current_article.strip())
    
    return articles

# Paso 3: Extraer número y título del artículo
def extract_article_info(article_text):
    lines = article_text.split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # Buscar patrón "ARTÍCULO X°." o "ARTÍCULO X."
    match = re.search(r'ARTÍCULO\s+(\d+)[°.]?\s*[.-]?\s*(.*)', first_line, re.IGNORECASE)
    if match:
        number = match.group(1)
        title = match.group(2).strip().rstrip('.')
        return number, title
    
    # Buscar patrón "CAPÍTULO"
    match = re.search(r'CAPÍTULO\s+(\w+)\s*[.-]?\s*(.*)', first_line, re.IGNORECASE)
    if match:
        number = match.group(1)
        title = match.group(2).strip().rstrip('.')
        return f"CAP-{number}", title
    
    # Si no encuentra patrón, usar las primeras palabras como título
    words = first_line.split()[:5]  # Primeras 5 palabras
    title = ' '.join(words) if words else "Sin título"
    return "UNKNOWN", title

# Paso 4: Generar preguntas variadas sobre el artículo
def generate_questions_for_article(article_number, article_title, article_content):
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
def create_training_examples(articles):
    training_examples = []
    system_message = "Eres un asistente experto en el Código Nacional de Tránsito de Colombia (Ley 769 de 2002). Proporciona información precisa y detallada sobre los artículos del código cuando se te consulte."
    
    for article in articles:
        if not article.strip():
            continue
            
        article_number, article_title = extract_article_info(article)
        
        # Limpiar el contenido del artículo
        clean_content = article.strip()
        
        # Generar múltiples preguntas para este artículo
        questions = generate_questions_for_article(article_number, article_title, clean_content)
        
        # Crear ejemplos de entrenamiento para cada pregunta
        for question in questions:
            training_example = {
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": clean_content}
                ]
            }
            training_examples.append(training_example)
    
    return training_examples

# Paso 6: Guardar en formato JSONL para fine-tuning
def save_to_jsonl_finetuning(training_examples, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

# Paso 7: Validar formato del archivo JSONL
def validate_jsonl_format(file_path):
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
                
                # Verificar que cada mensaje tenga 'role' y 'content'
                for msg_idx, message in enumerate(messages):
                    if 'role' not in message:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx}: Falta 'role'")
                    if 'content' not in message:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx}: Falta 'content'")
                    if message.get('role') not in ['system', 'user', 'assistant']:
                        errors.append(f"Línea {line_num}, mensaje {msg_idx}: Rol inválido '{message.get('role')}'")
                
            except json.JSONDecodeError as e:
                errors.append(f"Línea {line_num}: Error de JSON - {str(e)}")
    
    return errors

# Ejecutar el proceso
if __name__ == "__main__":
    pdf_path = "ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf"
    output_path = "articulos_ley_769_finetuning.jsonl"

    print("🔍 Extrayendo texto del PDF...")
    full_text = extract_text_from_pdf(pdf_path)

    print("📄 Dividiendo por artículos...")
    articles = split_by_articles(full_text)
    print(f"   Encontrados {len(articles)} artículos")

    print("🤖 Creando ejemplos de entrenamiento para fine-tuning...")
    training_examples = create_training_examples(articles)
    print(f"   Generados {len(training_examples)} ejemplos de entrenamiento")

    print(f"💾 Guardando ejemplos en {output_path}...")
    save_to_jsonl_finetuning(training_examples, output_path)

    print("✅ Validando formato del archivo...")
    validation_errors = validate_jsonl_format(output_path)
    
    if validation_errors:
        print("❌ Se encontraron errores de formato:")
        for error in validation_errors[:10]:  # Mostrar solo los primeros 10 errores
            print(f"   {error}")
        if len(validation_errors) > 10:
            print(f"   ... y {len(validation_errors) - 10} errores más")
    else:
        print("✅ Archivo JSONL generado exitosamente y validado para fine-tuning de OpenAI.")
        print(f"📊 Total de ejemplos: {len(training_examples)}")
        print(f"📁 Archivo: {output_path}")
        print("\n🚀 El archivo está listo para subir a OpenAI para fine-tuning.")