# -*- coding: utf-8 -*-
"""
Prueba de Validación de Reglas de Asociación (Market Basket Analysis)
sobre las 18 Respuestas Simuladas del Observatorio de Egresados UPB.
"""
import sys
import json

# Asegurar codificación UTF-8 en terminal de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from application.ia_service import (
    extraer_habilidades_por_respuesta,
    generar_reglas_asociacion,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. 18 Respuestas abiertas simuladas (las mismas usadas en test_ia_pipeline.py)
# ─────────────────────────────────────────────────────────────────────────────
respuestas_simuladas = [
    # Ingeniería de Sistemas
    "Considero que me faltó mayor preparación en liderazgo, especialmente en Docker, Kubernetes y soluciones en la nube.",
    "En mi trabajo actual me exigieron inglés conversacional, trabajo bajo presión, conocimientos sólidos en Scrum y arquitectura de microservicios.",
    "Las empresas piden mucho manejo de Excel avanzado, análisis de datos y metodologías ágiles. También resolución de problemas complejos.",
    "Falta énfasis en trabajo en equipo interdisciplinario y comunicación asertiva con clientes no técnicos.",
    "Se requiere Python, machine learning, gestión de proyectos y pensamiento crítico para tomar buenas decisiones de diseño.",

    # Derecho
    "Fue necesario aprender sobre análisis financiero, litigio penal y derecho laboral procesal en el ejercicio profesional.",
    "El mercado exige redacción técnica de alta calidad, negociación con contrapartes y cumplimiento normativo estricto.",
    "Me hizo falta formación en oratoria, comunicación efectiva ante jueces y adaptabilidad al cambio de legislación.",
    "Los abogados necesitamos más planeación estratégica de casos y manejo del tiempo para cumplir con los términos procesales.",

    # Psicología
    "Las empresas valoran mucho la inteligencia emocional, la empatía y las relaciones interpersonales del profesional.",
    "Se necesita creatividad para diseñar intervenciones, trabajo en equipo multidisciplinario y estadística aplicada.",
    "La toma de decisiones basada en evidencia y la comunicación asertiva son indispensables en el ámbito clínico.",

    # Administración
    "Definitivamente falta más formación en marketing digital, elaboración de presupuestos y Power BI para los dashboards gerenciales.",
    "El liderazgo de equipos, la gestión estratégica y la atención al cliente son lo que más piden las empresas hoy en día.",
    "Necesité bilingüismo para las negociaciones internacionales, gestión de proyectos ágiles y Excel avanzado para los reportes.",

    # Medicina
    "La comunicación con el paciente, el manejo del estrés y la toma de decisiones bajo presión son competencias vitales.",
    "Falta más formación en investigación clínica, redacción de informes médicos y normativa legal del sector salud.",
    "Se requiere trabajo en equipo, liderazgo en urgencias y adaptabilidad al cambio tecnológico en la salud digital.",
]

def ejecutar_pruebas():
    print("=" * 80)
    print("AUDITORÍA DE TRANSACCIONES DE ENTRADA (18 RESPUESTAS)")
    print("=" * 80)

    # Extraer conjuntos de habilidades por respuesta
    transacciones = []
    for i, texto in enumerate(respuestas_simuladas, 1):
        habs = extraer_habilidades_por_respuesta(texto)
        transacciones.append(habs)
        estado = "VALIDA (>=2)" if len(habs) >= 2 else "DESCARTADA (<2)"
        print(f"  Resp {i:02d} [{len(habs)} habs | {estado}]: {sorted(list(habs))}")

    validas = [t for t in transacciones if len(t) >= 2]
    descartadas = [t for t in transacciones if len(t) < 2]

    print("\n" + "-" * 80)
    print(f"Total respuestas evaluadas:       {len(transacciones)}")
    print(f"Transacciones válidas (>= 2 hab): {len(validas)} (utilizadas como soporte de Apriori)")
    print(f"Transacciones descartadas (< 2):  {len(descartadas)} (Respuestas 1, 6 y 10 con 1 sola habilidad)")
    print("-" * 80)

    # ─────────────────────────────────────────────────────────────────────────
    # PRUEBA A: min_ocurrencias = 3 (Filtro Estricto Solicitado)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("PRUEBA A: min_ocurrencias = 3 (min_soporte=0.05, min_confianza=0.5)")
    print("=" * 80)
    res_a = generar_reglas_asociacion(
        transacciones=transacciones,
        min_soporte=0.05,
        min_confianza=0.5,
        min_ocurrencias=3,
        top_reglas=20,
    )
    print("\n--- OUTPUT CRUDO JSON (PRUEBA A) ---")
    print(json.dumps(res_a, indent=2, ensure_ascii=False))

    # ─────────────────────────────────────────────────────────────────────────
    # PRUEBA B: min_ocurrencias = 2 (Para visualizar pares detectados en muestra pequeña)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("PRUEBA B: min_ocurrencias = 2 (min_soporte=0.05, min_confianza=0.5)")
    print("=" * 80)
    res_b = generar_reglas_asociacion(
        transacciones=transacciones,
        min_soporte=0.05,
        min_confianza=0.5,
        min_ocurrencias=2,
        top_reglas=20,
    )
    print("\n--- OUTPUT CRUDO JSON (PRUEBA B) ---")
    print(json.dumps(res_b, indent=2, ensure_ascii=False))

    # ─────────────────────────────────────────────────────────────────────────
    # Tabla de interpretación técnica
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("TABLA COMPARATIVA DE REGLAS ENCONTRADAS (PRUEBA B - min_ocurrencias=2):")
    print("=" * 80)
    print(f"{'Si menciona (Antecedente)':<28} {'También menciona (Consecuente)':<30} {'Ocurr':<6} {'Soporte':<9} {'Confianza':<10} {'Lift'}")
    print(f"{'-'*28} {'-'*30} {'-'*6} {'-'*9} {'-'*10} {'-'*6}")
    for r in res_b["reglas"]:
        print(f"{r['si_menciona']:<28} {r['tambien_menciona']:<30} {r['ocurrencias']:<6} {r['soporte']:<9.4f} {r['confianza']*100:<9.1f}% {r['lift']:.2f}")

if __name__ == "__main__":
    ejecutar_pruebas()
