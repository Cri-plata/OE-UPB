# -*- coding: utf-8 -*-
"""
Prueba FINAL de fragmentos con doble-forma (A+B).
Corrige el bug del test anterior: compara claves SIN tildes usando normalizacion.
"""
import unicodedata
from application.ia_service import analizar_habilidades_demandadas

def sin_tildes(texto):
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

# Mismos fragmentos de la Ronda 2
fragmentos = [
    # Cat A: palabras sueltas
    "empatia",
    "estadistica",
    "liderazgo",
    "excel",
    "creatividad",
    "negociacion",
    "adaptabilidad",
    "ingles",
    "scrum",

    # Cat B: listas por comas
    "excel, trabajo en equipo, ingles",
    "negociacion, persuasion, empatia",
    "estadistica, analisis de datos, power bi",
    "trabajo bajo presion, toma de decisiones",
    "liderazgo, comunicacion, adaptabilidad",

    # Cat C: fragmentos informales
    "mas ingles y trabajo bajo presion",
    "empatia creatividad innovacion",
    "python docker kubernetes",
    "scrum planeacion y normativa",
    "presupuestos toma de decisiones y proactividad",
    "comunicacion trabajo bajo presion excel ingles",
    "bilinguismo y oratoria",
    "mas pensamiento critico y puntualidad",
]

resultado = analizar_habilidades_demandadas(fragmentos, top_emergentes=10)

print("=" * 80)
print("PRUEBA FINAL: FRAGMENTOS CON DOBLE-FORMA (A+B) + es_core_news_md")
print("=" * 80)

stats = resultado["estadisticas"]
print(f"\nTotal respuestas: {stats['total_respuestas_analizadas']}")
print(f"Con habilidad: {stats['respuestas_con_habilidad']}")
print(f"Sin habilidad: {stats['respuestas_sin_habilidad']}")

print(f"\nHabilidades reconocidas ({len(resultado['habilidades_reconocidas'])} categorias):")
print(f"  {'Habilidad':<30} {'Tipo':<8} {'Menciones'}")
print(f"  {'-'*30} {'-'*8} {'-'*9}")
for h in resultado["habilidades_reconocidas"]:
    print(f"  {h['habilidad']:<30} {h['tipo']:<8} {h['menciones']}")

# Verificacion con comparacion normalizada (sin tildes)
print("\n--- VERIFICACION DE CASOS CRITICOS (comparacion sin tildes) ---")
habs_norm = {sin_tildes(h["habilidad"]) for h in resultado["habilidades_reconocidas"]}

casos = [
    ("Inteligencia emocional",  "empatia sola y en listas"),
    ("Analisis de datos",       "estadistica sola y en lista"),
    ("Gestion de proyectos",    "scrum solo y en fragmento"),
    ("Toma de decisiones",      "en lista y fragmento"),
    ("Comunicacion",            "sola y en fragmento"),
    ("Trabajo bajo presion",    "en lista y fragmento"),
    ("Trabajo en equipo",       "en lista"),
    ("Manejo de Excel / Office","excel solo y en fragmento"),
    ("Ingles / Segundo idioma", "ingles solo y fragmento"),
    ("Liderazgo",               "solo y en lista"),
    ("Negociacion",             "sola y en lista"),
    ("Creatividad e innovacion","sola y en fragmento"),
    ("Adaptabilidad al cambio", "sola y en lista"),
    ("Pensamiento critico",     "en fragmento"),
    ("Gestion del tiempo",      "puntualidad en fragmento"),
]

ok = 0
fallos = 0
for hab, desc in casos:
    encontrada = sin_tildes(hab) in habs_norm
    marker = "OK" if encontrada else "FALLO"
    if encontrada:
        ok += 1
    else:
        fallos += 1
    print(f"  [{marker}] {hab} ({desc})")

print(f"\nResultado: {ok}/{ok+fallos} casos criticos resueltos")
if fallos == 0:
    print("TODOS LOS CASOS CRITICOS RESUELTOS CON DOBLE-FORMA (A+B)")
else:
    print(f"QUEDAN {fallos} FALLOS POR RESOLVER")

# Emergentes
print(f"\nCandidatas emergentes ({len(resultado['candidatas_emergentes'])}):")
for c in resultado["candidatas_emergentes"]:
    print(f"  {c['termino']:<28} score={c['score_tfidf']:.4f} docs={c['frecuencia_documentos']}")
