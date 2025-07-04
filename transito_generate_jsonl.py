import json
from PyPDF2 import PdfReader

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

# Paso 3: Guardar en formato JSONL
def save_to_jsonl(articles, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(json.dumps({"text": article}, ensure_ascii=False) + "\n")

# Ejecutar el proceso
if __name__ == "__main__":
    pdf_path = "ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf"
    output_path = "articulos_ley_769.jsonl"

    print("Extrayendo texto del PDF...")
    full_text = extract_text_from_pdf(pdf_path)

    print("Dividiendo por artículos...")
    articles = split_by_articles(full_text)

    print(f"Guardando {len(articles)} artículos en {output_path}...")
    save_to_jsonl(articles, output_path)

    print("✅ Archivo JSONL generado exitosamente.")