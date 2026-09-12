"""Prueba del pipeline completo con datos simulados de encuestas."""
import json
from application.ia_service import analizar_habilidades_demandadas

# Respuestas abiertas ficticias simulando egresados de diversas carreras
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

# Ejecutar el pipeline completo
resultado = analizar_habilidades_demandadas(
    textos_respuestas=respuestas_simuladas,
    top_emergentes=12,
)

# Formatear salida
print("=" * 80)
print("RESULTADO AGREGADO DEL ENDPOINT /api/ia/habilidades-demandadas")
print("=" * 80)

print(f"\n[ESTADISTICAS]")
stats = resultado["estadisticas"]
print(f"   Total respuestas analizadas:  {stats['total_respuestas_analizadas']}")
print(f"   Con al menos 1 habilidad:     {stats['respuestas_con_habilidad']}")
print(f"   Sin habilidades detectadas:   {stats['respuestas_sin_habilidad']}")

print(f"\n[HABILIDADES RECONOCIDAS] ({len(resultado['habilidades_reconocidas'])} categorias):")
print(f"   {'Habilidad':<28} {'Tipo':<8} {'Menciones'}")
print(f"   {'-'*28} {'-'*8} {'-'*9}")
for h in resultado["habilidades_reconocidas"]:
    print(f"   {h['habilidad']:<28} {h['tipo']:<8} {h['menciones']}")

print(f"\n[CANDIDATAS EMERGENTES] (TOP {len(resultado['candidatas_emergentes'])} por TF-IDF):")
print(f"   {'Término':<28} {'Score':<10} {'Doc Freq'}")
print(f"   {'-'*28} {'-'*10} {'-'*8}")
for c in resultado["candidatas_emergentes"]:
    print(f"   {c['termino']:<28} {c['score_tfidf']:<10.4f} {c['frecuencia_documentos']}")

print("\n" + "=" * 80)
print("JSON COMPLETO (tal como lo devolvería el endpoint):")
print("=" * 80)
print(json.dumps(resultado, indent=2, ensure_ascii=False))
