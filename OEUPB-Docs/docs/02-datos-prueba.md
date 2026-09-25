# Datos de prueba

## Fuentes actuales

- `OEUPB-Backend/seed_db.py`: creación de usuarios/datos iniciales; revisar antes de ejecutar.
- `OEUPB-Backend/scripts/dev/generate_excel_fixtures.py`: generador parametrizable y reproducible de archivos Excel sintéticos.

## Reglas

1. Usar únicamente datos sintéticos.
2. No copiar documentos, correos, teléfonos ni respuestas reales de egresados.
3. Las credenciales de prueba deben estar marcadas como locales y no reutilizarse en producción.
4. Un fixture debe declarar momento, año y sede esperados.
5. Los casos mínimos deben cubrir: documento repetido, documento vacío, doble titulación, momento inválido, sede distinta y columnas faltantes.

## Ejemplo

```powershell
cd OEUPB-Backend
python scripts/dev/generate_excel_fixtures.py .tmp/encuestas.xlsx --rows 100 --double-degree-rate 0.05
```

Los fixtures automatizados viven junto a las pruebas que los consumen; no se conservan copias con datos personales ni variantes numeradas en la raíz.
