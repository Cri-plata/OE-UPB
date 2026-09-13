# Observatorio de Egresados UPB (OE UPB)

Bienvenido al repositorio oficial del proyecto **OE UPB**. Este proyecto está dividido en una arquitectura de múltiples capas (Cliente-Servidor).

## Estructura del Repositorio

* **\OEUPB-Docs:** Documentación oficial, arquitectura, requerimientos y planes.
* **\OEUPB-Contracts:** Contratos de API (Interfaces TypeScript y Modelos Pydantic) compartidos.
* **\OEUPB-Frontend:** Aplicación web desarrollada en Angular 17+ (Modo Claro).
* **\OEUPB-Backend:** API REST y Módulo Analítico en Python (FastAPI/Flask, Pandas, IA).

## Configuración del Backend (Módulo de IA)

Para ejecutar el backend y su módulo de Inteligencia Artificial (procesamiento de lenguaje natural y extracción de habilidades), además de instalar las dependencias de `requirements.txt`, es necesario descargar el modelo de spaCy en español:

```bash
# 1. Instalar dependencias
pip install -r OEUPB-Backend/requirements.txt

# 2. Descargar modelo de lenguaje en español (obligatorio para el pipeline de IA)
python -m spacy download es_core_news_md
```

> **Nota:** El modelo `es_core_news_md` no se instala automáticamente vía `requirements.txt` y debe descargarse aparte mediante el comando indicado.
