# Transito App - Generador de JSONL para Fine-tuning de OpenAI

Este proyecto contiene scripts de Python que extraen texto de un PDF de la Ley 769 de 2002 (Código Nacional de Tránsito) y lo convierten a diferentes formatos JSONL.

## 📁 Archivos del Proyecto

### Scripts Disponibles

1. **`transito_generate_jsonl.py`** - Script original
   - Genera formato JSONL simple con clave `"text"`
   - Útil para análisis general de texto

2. **`transito_generate_jsonl_finetuning.py`** - Script para fine-tuning ✨
   - Genera formato JSONL compatible con OpenAI fine-tuning
   - Incluye estructura de `"messages"` con roles `system`, `user`, `assistant`
   - Crea múltiples ejemplos de entrenamiento por artículo
   - Incluye validación automática del formato

### Archivos Generados

- `articulos_ley_769.jsonl` - Formato simple (script original)
- `articulos_ley_769_finetuning.jsonl` - Formato para fine-tuning de OpenAI

## 🚀 Configuración del Entorno

### Instalación desde cero

1. **Crear el entorno virtual:**
   ```powershell
   python -m venv venv
   ```

2. **Activar el entorno virtual:**
   ```powershell
   venv\Scripts\Activate.ps1
   ```
   
   *Nota: Si aparece un error de política de ejecución, ejecuta primero:*
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Instalar las dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

### Activación del entorno virtual existente

```powershell
venv\Scripts\Activate.ps1
```

*Verifica que el entorno esté activado cuando veas `(venv)` al inicio de la línea de comandos.*

## 📊 Uso de los Scripts

### Para Fine-tuning de OpenAI (Recomendado)

```powershell
python transito_generate_jsonl_finetuning.py
```

**Características:**
- ✅ Formato compatible con OpenAI fine-tuning
- ✅ Validación automática del formato
- ✅ Múltiples ejemplos por artículo (6 variaciones de preguntas)
- ✅ Sistema de roles (system, user, assistant)
- ✅ Extracción mejorada de números de artículos
- ✅ Total: ~1,038 ejemplos de entrenamiento

### Para Análisis General

```powershell
python transito_generate_jsonl.py
```

**Características:**
- Formato simple con clave `"text"`
- Un ejemplo por artículo
- Total: ~173 artículos

## 📋 Formato de Datos

### Formato Fine-tuning (OpenAI)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente experto en el Código Nacional de Tránsito de Colombia (Ley 769 de 2002). Proporciona información precisa y detallada sobre los artículos del código cuando se te consulte."
    },
    {
      "role": "user",
      "content": "¿Qué establece el artículo 1 del Código Nacional de Tránsito?"
    },
    {
      "role": "assistant",
      "content": "ARTÍCULO 1°. ÁMBITO DE APLICACIÓN Y PRINCIPIOS. Las normas del presente Código..."
    }
  ]
}
```

### Formato Simple

```json
{"text": "ARTÍCULO 1°. ÁMBITO DE APLICACIÓN Y PRINCIPIOS. Las normas del presente Código..."}
```

## 🔧 Características del Script de Fine-tuning

### Extracción Inteligente de Artículos
- Detecta automáticamente números de artículos y capítulos
- Extrae títulos de artículos
- Maneja casos especiales y formatos irregulares

### Generación de Preguntas Variadas
Para cada artículo, genera 6 tipos de preguntas:
1. "¿Qué establece el artículo X del Código Nacional de Tránsito?"
2. "Explícame el contenido del artículo X."
3. "¿Cuál es el contenido del artículo X sobre [título]?"
4. "Artículo X: [título]"
5. "¿Qué dice la ley de tránsito en el artículo X?"
6. "Necesito información sobre el artículo X del código de tránsito."

### Validación Automática
- Verifica estructura de `"messages"`
- Valida roles (`system`, `user`, `assistant`)
- Confirma presencia de claves requeridas
- Detecta errores de formato JSON

## 📤 Subir a OpenAI para Fine-tuning

1. **Verifica el archivo generado:**
   - `articulos_ley_769_finetuning.jsonl`
   - Debe mostrar "✅ Archivo JSONL generado exitosamente y validado"

2. **Sube el archivo a OpenAI:**
   ```python
   import openai
   
   # Subir archivo de entrenamiento
   with open("articulos_ley_769_finetuning.jsonl", "rb") as f:
       response = openai.files.create(
           file=f,
           purpose="fine-tune"
       )
   
   file_id = response.id
   print(f"Archivo subido con ID: {file_id}")
   ```

3. **Crear trabajo de fine-tuning:**
   ```python
   # Crear fine-tuning job
   job = openai.fine_tuning.jobs.create(
       training_file=file_id,
       model="gpt-3.5-turbo"
   )
   
   print(f"Job de fine-tuning creado: {job.id}")
   ```

## 📊 Estadísticas del Dataset

- **Total de artículos extraídos:** 173
- **Total de ejemplos de entrenamiento:** 1,038
- **Promedio de ejemplos por artículo:** 6
- **Formato:** Compatible con OpenAI fine-tuning API
- **Validación:** ✅ Automática

## 🛠️ Dependencias

```txt
PyPDF2==3.0.1
```

## 📁 Estructura del Proyecto

```
python_training/
├── venv/                                    # Entorno virtual
├── ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf
├── requirements.txt                         # Dependencias
├── transito_generate_jsonl.py              # Script original
├── transito_generate_jsonl_finetuning.py   # Script para fine-tuning ⭐
├── articulos_ley_769.jsonl                 # Salida formato simple
├── articulos_ley_769_finetuning.jsonl      # Salida para fine-tuning ⭐
├── README.md                               # Documentación general
└── README_FINETUNING.md                   # Esta documentación
```

## 💡 Consejos para Fine-tuning

1. **Tamaño del dataset:** 1,038 ejemplos es un buen tamaño para fine-tuning
2. **Calidad:** Cada ejemplo está validado automáticamente
3. **Variedad:** 6 tipos diferentes de preguntas por artículo
4. **Consistencia:** Formato uniforme en todos los ejemplos
5. **Contexto:** Sistema message define claramente el rol del asistente

## 🔍 Solución de Problemas

### Error: "Invalid file format. Example X is missing key 'messages'"
- ✅ **Solucionado:** Usa `transito_generate_jsonl_finetuning.py`
- Este script genera el formato correcto con la clave `"messages"`

### Error: "ModuleNotFoundError: No module named 'PyPDF2'"
- Activa el entorno virtual: `venv\Scripts\Activate.ps1`
- Instala dependencias: `pip install -r requirements.txt`

### Error de política de ejecución en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

**¡El archivo está listo para fine-tuning de OpenAI! 🚀**