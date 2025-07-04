# Transito App - Generador de JSONL

Este proyecto contiene un script de Python que extrae texto de un PDF de la Ley 769 de 2002 (Código Nacional de Tránsito) y lo convierte a formato JSONL dividido por artículos.

## Configuración del Entorno Virtual

### Instalación desde cero

Si es la primera vez que configuras el proyecto, sigue estos pasos:

1. **Crear el entorno virtual:**
   ```bash
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

Si el entorno virtual ya existe, simplemente actívalo:

```powershell
venv\Scripts\Activate.ps1
```

*Verifica que el entorno esté activado cuando veas `(venv)` al inicio de la línea de comandos.*

### Desactivar el entorno virtual

Cuando termines de trabajar, puedes desactivar el entorno virtual:

```bash
deactivate
```

## Uso del Script

Una vez que tengas el entorno virtual activado y las dependencias instaladas:

1. **Asegúrate de que el archivo PDF esté en el directorio del proyecto:**
   - `ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf`

2. **Ejecuta el script:**
   ```powershell
   python transito_generate_jsonl.py
   ```

3. **El script generará:**
   - Un archivo `articulos_ley_769.jsonl` con los artículos extraídos del PDF

## Estructura del Proyecto

```
transito_app/
├── venv/                    # Entorno virtual (generado)
├── ley-769-de-2002-codigo-nacional-de-transito_3704_0.pdf
├── requirements.txt         # Dependencias del proyecto
├── transito_generate_jsonl.py  # Script principal
├── articulos_ley_769.jsonl  # Archivo generado (después de ejecutar)
└── README.md               # Este archivo
```

## Dependencias

El proyecto utiliza las siguientes librerías de Python:
- `PyPDF2`: Para extraer texto de archivos PDF

## Notas

- El entorno virtual se crea en la carpeta `venv/` dentro del directorio del proyecto
- Asegúrate de activar el entorno virtual cada vez que trabajes en el proyecto
- El archivo `requirements.txt` contiene todas las dependencias necesarias
- El script está optimizado para extraer artículos y capítulos del Código Nacional de Tránsito

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contact

Developed by:
- Paul Realpe
- Jimmy Realpe

Email: co.devpaul@gmail.com

Phone: 3148580454

<a href="https://devpaul.pro">https://devpaul.pro/</a>

Feel free to reach out for any inquiries or collaborations!