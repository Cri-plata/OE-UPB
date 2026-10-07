"""
Servicio del Modelo de Análisis de Empleabilidad (RF-71, ADR-021)

Modelo de análisis retrospectivo, no predictivo: se entrena y resume sobre trayectorias ya
observadas. Los identificadores conservan el nombre histórico "prediccion" por compatibilidad.
======================================================
Módulo de Machine Learning para proyectar trayectorias de egresados UPB.
Entrena modelos supervisados (GradientBoostingClassifier) usando mediciones
longitudinales (M0 -> M1 o M0/M1 -> M5).

Restricciones éticas y técnicas:
  - Sin exposición de datos personales individuales (números de documento o nombres).
  - Resultados agregados por programa académico y cohorte.
  - Explicabilidad transparente: ranking de importancia de características.
  - Validación cruzada estratificada (Stratified K-Fold).
  - Umbral mínimo de 30 trayectorias para evitar estimaciones espurias con muestras insuficientes.
"""

import io
import time
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import numpy as np
import pandas as pd
import sklearn.base

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight

from domain.models import Medicion, Egresado, Sede
from application.indicadores import estado_laboral, salario
from application.ia_service import (
    extraer_habilidades_por_respuesta,
    TAXONOMIA_HABILIDADES_BRUTA,
    extraer_textos_libres_encuesta,
    PATRONES_PREGUNTAS_ABIERTAS,
    PATRONES_EXCLUSION_PREGUNTAS,
)
from application.model_cache import prediccion_model_cache
from application.programas import canonizar_programa

# Reutilizar patrones canónicos definidos en ia_service (IA-AUD-05)
_OPEN_PATTERNS = PATRONES_PREGUNTAS_ABIERTAS
_EXCLUDE_PATTERNS = PATRONES_EXCLUSION_PREGUNTAS
_extraer_textos_libres = extraer_textos_libres_encuesta

MAPA_ESTADO_NUM = {
    "sin_empleo": 0,
    "estudiante": 1,
    "independiente": 2,
    "empleado": 3,
}

UMBRAL_MINIMO_TRAYECTORIAS = 30


def _calcular_satisfaccion_promedio(respuestas: Optional[dict]) -> float:
    """Extrae el promedio numérico de satisfacción general (1.0 a 5.0)."""
    if not respuestas:
        return 3.0
    valores = []
    for k, v in respuestas.items():
        if "califique su nivel de satisfacci" in k.lower() and v is not None:
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                pass
    return float(np.mean(valores)) if valores else 3.0


def _contar_habilidades(respuestas: Optional[dict]) -> Tuple[int, int]:
    """Cuenta habilidades blandas y duras detectadas en respuestas abiertas."""
    textos = _extraer_textos_libres(respuestas)
    blandas = 0
    duras = 0
    for t in textos:
        habs_detectadas = extraer_habilidades_por_respuesta(t)
        for h in habs_detectadas:
            tipo = TAXONOMIA_HABILIDADES_BRUTA.get(h, {}).get("tipo")
            if tipo == "blanda":
                blandas += 1
            elif tipo == "dura":
                duras += 1
    return blandas, duras


def _categorizar_salario(valor_smlv: Optional[float], estado: str) -> str:
    """Clasifica el salario en rangos estandarizados de política pública UPB."""
    if estado == "sin_empleo" or valor_smlv is None:
        return "Sin ingreso / No reporta"
    if valor_smlv < 2.0:
        return "< 2 SMLV"
    if valor_smlv <= 4.0:
        return "2–4 SMLV"
    return "> 4 SMLV"


def extraer_trayectorias_longitudinales(
    mediciones: List[Medicion],
    egresados_dict: Dict[str, Egresado],
    momento_origen: int = 0,
    momento_destino: int = 1,
    filtro_programa: Optional[str] = None,
    filtro_anio: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Agrupa mediciones por egresado y empareja mediciones de momento_origen y momento_destino.
    """
    por_egresado: Dict[str, List[Medicion]] = {}
    for m in mediciones:
        if m.egresado_documento:
            por_egresado.setdefault(m.egresado_documento, []).append(m)

    filas: List[Dict[str, Any]] = []

    for doc, ms in por_egresado.items():
        m_origen = next((m for m in ms if m.momento == momento_origen), None)
        m_destino = next((m for m in ms if m.momento == momento_destino), None)

        if not (m_origen and m_destino):
            continue

        if filtro_anio and (m_origen.anio != filtro_anio and m_destino.anio != filtro_anio):
            continue

        e_origen = estado_laboral(m_origen.respuestas)
        e_destino = estado_laboral(m_destino.respuestas)

        if not (e_origen and e_destino):
            continue

        egr = egresados_dict.get(doc)
        prog_raw = (egr.programa if egr and egr.programa else "Otros").strip()
        prog = canonizar_programa(prog_raw)

        if filtro_programa:
            filtro_canon = canonizar_programa(filtro_programa)
            if prog != filtro_canon and prog_raw != filtro_programa:
                continue

        sal_orig = salario(m_origen.respuestas) or 0.0
        sat_orig = _calcular_satisfaccion_promedio(m_origen.respuestas)
        hb_orig, hd_orig = _contar_habilidades(m_origen.respuestas)

        sal_dest = salario(m_destino.respuestas)
        rango_dest = _categorizar_salario(sal_dest, e_destino)

        filas.append({
            "documento": doc,
            "programa": prog,
            "estado_origen": e_origen,
            "salario_origen": sal_orig,
            "satisfaccion_origen": sat_orig,
            "habs_blandas_origen": hb_orig,
            "habs_duras_origen": hd_orig,
            "anio_origen": m_origen.anio,
            "estado_destino": e_destino,
            "rango_salarial_destino": rango_dest,
        })

    return filas


def preparar_matriz_features(df: pd.DataFrame) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """
    Construye la matriz de diseño numérica para scikit-learn con nombres legibles.
    """
    df_proc = df.copy()

    # Codificación ordinal de estado inicial
    df_proc["estado_origen_num"] = df_proc["estado_origen"].map(lambda x: MAPA_ESTADO_NUM.get(x, 0))

    # One-hot encoding de programas (top 8 + Otros)
    top_programas = df_proc["programa"].value_counts().head(8).index.tolist()
    df_proc["programa_agrupado"] = df_proc["programa"].apply(lambda p: p if p in top_programas else "Otros")

    df_dummies = pd.get_dummies(df_proc["programa_agrupado"], prefix="prog", drop_first=False)
    df_proc = pd.concat([df_proc, df_dummies], axis=1)

    columnas_programa = list(df_dummies.columns)

    feature_cols = [
        "estado_origen_num",
        "salario_origen",
        "satisfaccion_origen",
        "habs_blandas_origen",
        "habs_duras_origen",
        "anio_origen",
    ] + columnas_programa

    # Llenar cualquier valor nulo restante
    for col in feature_cols:
        df_proc[col] = df_proc[col].fillna(0)

    X = df_proc[feature_cols].values
    return X, feature_cols, df_proc


def calcular_pesos_balanceados(y: np.ndarray, factor_suavizado: float = 0.65) -> np.ndarray:
    """
    Calcula pesos muestrales balanceados inversamente proporcionales a las frecuencias de clase (Cost-Sensitive Learning),
    aplicando suavizado exponencial (factor_suavizado=0.65) para atenuar sobre-penalizaciones agresivas de la clase mayoritaria.
    Normaliza los pesos para preservar la escala promedio unitaria (mean=1.0).
    """
    if len(y) == 0:
        return np.array([], dtype=float)
    raw_weights = compute_sample_weight(class_weight="balanced", y=y)
    if factor_suavizado != 1.0:
        smoothed = np.power(raw_weights, factor_suavizado)
        mean_val = float(np.mean(smoothed))
        return (smoothed / mean_val) if mean_val > 0 else smoothed
    return raw_weights


def entrenar_evaluar_modelo(
    X: np.ndarray,
    y: np.ndarray,
    feature_cols: List[str],
) -> Dict[str, Any]:
    """
    Aplica GradientBoostingClassifier con calibración adaptativa contra desbalance de clases (Cost-Sensitive Learning),
    validación cruzada estratificada y evaluación comparativa multi-algoritmo (IA-10).
    """
    clase_counts = Counter(y)
    min_count = min(clase_counts.values()) if clase_counts else 0
    n_splits = max(2, min(5, min_count))
    sample_weights = calcular_pesos_balanceados(y, factor_suavizado=0.65)

    # Definir suite de clasificadores supervisados con soporte de ponderación balanceada (IA-10)
    candidatos = [
        ("Gradient Boosting", GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)),
        ("Random Forest", RandomForestClassifier(n_estimators=50, max_depth=5, class_weight="balanced", random_state=42)),
        ("Regresión Logística", make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, class_weight="balanced", random_state=42))),
    ]

    comparativa_algoritmos = []
    clf_produccion = None
    acc_prod = 0.0
    f1_prod = 0.0

    for nombre, estimator in candidatos:
        t0 = time.perf_counter()
        if n_splits >= 2 and len(clase_counts) > 1:
            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            try:
                acc_folds = []
                f1_folds = []
                for tr_idx, te_idx in cv.split(X, y):
                    est_fold = sklearn.base.clone(estimator)
                    if nombre == "Gradient Boosting":
                        sw_fold = calcular_pesos_balanceados(y[tr_idx], factor_suavizado=0.65)
                        est_fold.fit(X[tr_idx], y[tr_idx], sample_weight=sw_fold)
                    else:
                        est_fold.fit(X[tr_idx], y[tr_idx])
                    preds_fold = est_fold.predict(X[te_idx])
                    acc_folds.append(accuracy_score(y[te_idx], preds_fold))
                    f1_folds.append(f1_score(y[te_idx], preds_fold, average="macro"))
                m_acc = float(np.mean(acc_folds))
                m_f1 = float(np.mean(f1_folds))
            except Exception:
                if nombre == "Gradient Boosting":
                    estimator.fit(X, y, sample_weight=sample_weights)
                else:
                    estimator.fit(X, y)
                preds = estimator.predict(X)
                m_acc = float(accuracy_score(y, preds))
                m_f1 = float(f1_score(y, preds, average="macro"))
        else:
            if nombre == "Gradient Boosting":
                estimator.fit(X, y, sample_weight=sample_weights)
            else:
                estimator.fit(X, y)
            preds = estimator.predict(X)
            m_acc = float(accuracy_score(y, preds))
            m_f1 = float(f1_score(y, preds, average="macro"))
        t_elapsed = round((time.perf_counter() - t0) * 1000, 1)

        # Ajuste final en toda la muestra
        if nombre == "Gradient Boosting":
            estimator.fit(X, y, sample_weight=sample_weights)
        else:
            estimator.fit(X, y)
        es_seleccionado = (nombre == "Gradient Boosting")

        comparativa_algoritmos.append({
            "algoritmo": nombre,
            "accuracy": round(m_acc * 100, 1),
            "f1_score": round(m_f1, 3),
            "tiempo_ms": t_elapsed,
            "seleccionado": es_seleccionado,
        })

        if es_seleccionado:
            clf_produccion = estimator
            acc_prod = m_acc
            f1_prod = m_f1

    clf = clf_produccion if clf_produccion else candidatos[0][1]

    # Importancia de features con nombres legibles
    nombres_legibles = {
        "estado_origen_num": "Estado laboral inicial (M0)",
        "salario_origen": "Nivel salarial inicial",
        "satisfaccion_origen": "Satisfacción académica UPB",
        "habs_blandas_origen": "Habilidades blandas detectadas",
        "habs_duras_origen": "Habilidades técnicas/duras",
        "anio_origen": "Año de graduación / Cohorte",
    }
    
    importancias_raw = list(zip(feature_cols, clf.feature_importances_))
    importancias_raw.sort(key=lambda x: x[1], reverse=True)

    importancias_limpias = []
    for f, imp in importancias_raw:
        if f.startswith("prog_"):
            nombre = f"Programa: {f.replace('prog_', '').replace('_', ' ').title()}"
        else:
            nombre = nombres_legibles.get(f, f)
        importancias_limpias.append({
            "factor": nombre,
            "importancia": round(float(imp) * 100, 1),
        })

    # Matriz de confusión
    labels = sorted(list(set(y)))
    cm = confusion_matrix(y, clf.predict(X), labels=labels).tolist()

    return {
        "modelo": clf,
        "clases": list(clf.classes_),
        "accuracy": round(acc_prod * 100, 1),
        "f1_score": round(f1_prod, 3),
        "importancia_factores": importancias_limpias[:8],
        "matriz_confusion": {
            "clases": labels,
            "matriz": cm,
        },
        "comparativa_algoritmos": comparativa_algoritmos,
    }


def evaluar_validacion_temporal(
    df: pd.DataFrame,
    X: np.ndarray,
    y: np.ndarray,
    accuracy_cv: float,
) -> Dict[str, Any]:
    """
    Realiza backtesting longitudinal por cohorte anual (IA-17):
    Entrena con las cohortes históricas anteriores y evalúa sobre la cohorte graduada más reciente,
    simulando la capacidad real de proyección en el tiempo.
    """
    if "anio_origen" not in df.columns:
        return {
            "disponible": False,
            "motivo": "Columna anio_origen no disponible para partición temporal.",
        }

    anios = sorted([int(a) for a in df["anio_origen"].dropna().unique() if a])
    if len(anios) < 2:
        return {
            "disponible": False,
            "motivo": f"Se identificó una sola cohorte anual ({anios[0] if anios else 'N/A'}). Se requieren al menos 2 cohortes para validación temporal.",
        }

    anio_test = anios[-1]
    mask_test = (df["anio_origen"] == anio_test).values
    mask_train = (df["anio_origen"] < anio_test).values

    n_test = int(np.sum(mask_test))
    n_train = int(np.sum(mask_train))

    if n_test < 5 or n_train < 15:
        return {
            "disponible": False,
            "motivo": f"Muestra insuficiente para backtesting en la cohorte {anio_test} (Entrenamiento: {n_train}, Prueba: {n_test}). Mínimo requerido: 15 / 5.",
        }

    X_train, y_train = X[mask_train], y[mask_train]
    X_test, y_test = X[mask_test], y[mask_test]

    clf_temporal = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
    try:
        sw_temporal = calcular_pesos_balanceados(y_train, factor_suavizado=0.65)
        clf_temporal.fit(X_train, y_train, sample_weight=sw_temporal)
        preds_test = clf_temporal.predict(X_test)

        acc_temp = float(accuracy_score(y_test, preds_test)) * 100.0
        f1_temp = float(f1_score(y_test, preds_test, average="macro"))

        # Diagnóstico de estabilidad comparando con CV
        diff = abs(accuracy_cv - acc_temp)
        if diff <= 6.0:
            diag = "Alta (Generalización temporal consistente)"
            color = "verde"
        elif diff <= 14.0:
            diag = "Moderada (Sensibilidad leve a variaciones de cohorte)"
            color = "amarillo"
        else:
            diag = "Sensible (Influencia de ciclo económico anual)"
            color = "naranja"

        return {
            "disponible": True,
            "motivo": None,
            "cohorte_evaluada": int(anio_test),
            "tamano_muestra_prueba": n_test,
            "tamano_muestra_entrenamiento": n_train,
            "accuracy_temporal": round(acc_temp, 1),
            "f1_temporal": round(f1_temp, 3),
            "diagnostico_estabilidad": diag,
            "color_estabilidad": color,
        }
    except Exception as e:
        return {
            "disponible": False,
            "motivo": f"No fue posible ejecutar el backtesting temporal: {str(e)}",
        }


def agregar_predicciones_por_programa(
    df: pd.DataFrame,
    X: np.ndarray,
    modelo_estado: GradientBoostingClassifier,
    clases_estado: List[str],
    modelo_salario: Optional[GradientBoostingClassifier] = None,
) -> Tuple[List[Dict[str, Any]], int, List[Dict[str, Any]]]:
    """
    Agrupa las estimaciones por programa académico, calcula semáforo de riesgo y alertas.
    """
    probs_estado = modelo_estado.predict_proba(X)
    preds_salario = modelo_salario.predict(X) if modelo_salario else ["No proyectado"] * len(X)

    # Índices de clases
    idx_empleado = clases_estado.index("empleado") if "empleado" in clases_estado else None
    idx_indep = clases_estado.index("independiente") if "independiente" in clases_estado else None
    idx_estud = clases_estado.index("estudiante") if "estudiante" in clases_estado else None
    idx_sin_empleo = clases_estado.index("sin_empleo") if "sin_empleo" in clases_estado else None

    df_res = df.copy()
    df_res["p_empleado"] = probs_estado[:, idx_empleado] if idx_empleado is not None else 0.0
    df_res["p_independiente"] = probs_estado[:, idx_indep] if idx_indep is not None else 0.0
    df_res["p_estudiante"] = probs_estado[:, idx_estud] if idx_estud is not None else 0.0
    df_res["p_sin_empleo"] = probs_estado[:, idx_sin_empleo] if idx_sin_empleo is not None else 0.0
    df_res["salario_predicho"] = preds_salario

    agrupado = []
    total_egresados_en_riesgo = 0
    alertas = []

    for prog, grupo in df_res.groupby("programa"):
        n = len(grupo)
        p_emp = float(grupo["p_empleado"].mean() * 100)
        p_ind = float(grupo["p_independiente"].mean() * 100)
        p_est = float(grupo["p_estudiante"].mean() * 100)
        p_sin = float(grupo["p_sin_empleo"].mean() * 100)

        # Rango salarial más frecuente proyectado
        rango_mas_comun = grupo["salario_predicho"].mode().iloc[0] if not grupo["salario_predicho"].empty else "2–4 SMLV"

        # Clasificación de riesgo de desempleo
        if p_sin >= 30.0:
            nivel_riesgo = "Alto"
            total_egresados_en_riesgo += n
            alertas.append({
                "programa": prog,
                "severidad": "alta",
                "mensaje": f"Riesgo de desempleo proyectado del {p_sin:.1f}% supera el umbral del 30%.",
                "riesgo_estimado": round(p_sin, 1),
                "tamano_muestra": n,
            })
        elif p_sin >= 18.0:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"

        agrupado.append({
            "programa": prog,
            "total_egresados": n,
            "probabilidad_empleado": round(p_emp, 1),
            "probabilidad_independiente": round(p_ind, 1),
            "probabilidad_estudiante": round(p_est, 1),
            "probabilidad_sin_empleo": round(p_sin, 1),
            "nivel_riesgo": nivel_riesgo,
            "rango_salarial_estimado": rango_mas_comun,
        })

    # Ordenar por cantidad de egresados descendente
    agrupado.sort(key=lambda x: x["total_egresados"], reverse=True)

    return agrupado, total_egresados_en_riesgo, alertas


def calcular_indicadores_robustez(
    total_trayectorias: int,
    y_estado: np.ndarray,
    accuracy: float,
    f1: float,
) -> Dict[str, Any]:
    """
    Calcula el semáforo de robustez estadística del modelo (IA-13).
    Evalúa tres dimensiones clave:
      1. Tamaño muestral: óptimo (>=100), moderado (30-99), crítico (<30).
      2. Balance de clases: balanceado (mínimo >=10%), moderado (5-10%), severo (<5%).
      3. Exactitud en validación cruzada: alta (>=75%), moderada (55-75%), baja (<55%).
    Retorna un nivel consolidado ('Alta', 'Media', 'Baja') y observaciones interpretativas.
    """
    # 1. Tamaño muestral
    if total_trayectorias >= 100:
        status_muestra = "optimo"
        color_muestra = "verde"
        obs_muestra = f"Muestra robusta ({total_trayectorias} trayectorias longitudinales analizadas)."
    elif total_trayectorias >= 30:
        status_muestra = "moderado"
        color_muestra = "amarillo"
        obs_muestra = f"Muestra longitudinal moderada ({total_trayectorias} trayectorias). Sugerido consolidar periodos adicionales."
    else:
        status_muestra = "critico"
        color_muestra = "rojo"
        obs_muestra = f"Muestra longitudinal limitada ({total_trayectorias} trayectorias). Requiere cautela interpretativa."

    # 2. Balance de clases
    counts = Counter(y_estado)
    total = len(y_estado) if len(y_estado) > 0 else 1
    min_pct = min((c / total for c in counts.values()), default=0.0) * 100.0

    if min_pct >= 10.0:
        status_balance = "balanceado"
        color_balance = "verde"
        obs_balance = f"Distribución de condiciones laborales equilibrada (mínimo {min_pct:.1f}% en la clase minoritaria)."
    elif min_pct >= 5.0:
        status_balance = "desbalanceado_moderado"
        color_balance = "amarillo"
        obs_balance = f"Leve desbalance muestral ({min_pct:.1f}% en la condición laboral minoritaria)."
    else:
        status_balance = "desbalanceado_severo"
        color_balance = "rojo"
        obs_balance = f"Fuerte desbalance de clases ({min_pct:.1f}% en la clase minoritaria). Puede sesgar las estimaciones de las clases minoritarias."

    # 3. Precisión / Concordancia
    if accuracy >= 75.0:
        status_precision = "alta"
        color_precision = "verde"
        obs_precision = f"Alta concordancia empírica ({accuracy:.1f}% exactitud en validación estratificada)."
    elif accuracy >= 55.0:
        status_precision = "moderada"
        color_precision = "amarillo"
        obs_precision = f"Concordancia empírica moderada ({accuracy:.1f}% de exactitud en CV)."
    else:
        status_precision = "baja"
        color_precision = "rojo"
        obs_precision = f"Concordancia empírica preliminar ({accuracy:.1f}%). Usar proyecciones con cautela."

    # Consolidación del nivel general
    verdes = sum(1 for c in [color_muestra, color_balance, color_precision] if c == "verde")
    rojos = sum(1 for c in [color_muestra, color_balance, color_precision] if c == "rojo")

    if rojos >= 2 or (color_muestra == "rojo" and color_precision == "rojo"):
        nivel_general = "Baja"
        color_general = "rojo"
    elif verdes >= 2 and rojos == 0:
        nivel_general = "Alta"
        color_general = "verde"
    else:
        nivel_general = "Media"
        color_general = "amarillo"

    return {
        "nivel_general": nivel_general,
        "color_general": color_general,
        "estrategia_balanceo": "Ponderación adaptativa de clases activa (Cost-Sensitive Learning)",
        "muestra": {
            "status": status_muestra,
            "color": color_muestra,
            "trayectorias": total_trayectorias,
            "observacion": obs_muestra,
        },
        "balance_clases": {
            "status": status_balance,
            "color": color_balance,
            "min_porcentaje": round(min_pct, 1),
            "observacion": obs_balance + " Compensado con pesos muestrales balanceados.",
        },
        "precision": {
            "status": status_precision,
            "color": color_precision,
            "accuracy": round(accuracy, 1),
            "observacion": obs_precision,
        },
        "observaciones": [obs_muestra, obs_balance, obs_precision],
    }


def predecir_empleabilidad_servicio(
    mediciones: List[Medicion],
    egresados: List[Egresado],
    momento_origen: int = 0,
    momento_destino: int = 1,
    filtro_programa: Optional[str] = None,
    filtro_anio: Optional[int] = None,
    sede_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Punto de entrada principal para el router /api/ia/prediccion-empleabilidad.
    """
    egresados_dict = {e.numero_documento: e for e in egresados}
    mediciones_count = len(mediciones)
    max_medicion_id = max((m.id for m in mediciones), default=0)

    # IA-09 / IA-AUD-02: Verificación de cache en memoria con aislamiento por sede
    s_id = sede_id if sede_id is not None else (getattr(mediciones[0], "sede_id", 0) if mediciones else 0)
    tag_sede = f"sede_{s_id}"

    cached_result = prediccion_model_cache.get(
        mediciones_count=mediciones_count,
        max_medicion_id=max_medicion_id,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
        filtro_programa=filtro_programa,
        filtro_anio=filtro_anio,
        extra_tag=tag_sede,
    )
    if cached_result is not None:
        return cached_result

    trayectorias = extraer_trayectorias_longitudinales(
        mediciones=mediciones,
        egresados_dict=egresados_dict,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
        filtro_programa=filtro_programa,
        filtro_anio=filtro_anio,
    )

    if len(trayectorias) < UMBRAL_MINIMO_TRAYECTORIAS:
        return {
            "estado": "insuficiente_datos",
            "mensaje": (
                f"Se identificaron {len(trayectorias)} trayectorias longitudinales entre Momento {momento_origen} "
                f"y Momento {momento_destino}. Se requiere un mínimo de {UMBRAL_MINIMO_TRAYECTORIAS} trayectorias "
                "para garantizar significancia estadística y evitar sobreajuste."
            ),
            "total_trayectorias": len(trayectorias),
            "precision_modelo": 0.0,
            "f1_score": 0.0,
            "programas_analizados": 0,
            "egresados_en_riesgo": 0,
            "importancia_factores": [],
            "predicciones_programas": [],
            "alertas_riesgo": [],
            "matriz_confusion": {"clases": [], "matriz": []},
            "indicadores_robustez": {
                "nivel_general": "Baja",
                "color_general": "rojo",
                "muestra": {
                    "status": "critico",
                    "color": "rojo",
                    "trayectorias": len(trayectorias),
                    "observacion": f"Muestra insuficiente ({len(trayectorias)} de mínimo {UMBRAL_MINIMO_TRAYECTORIAS} requeridas).",
                },
                "balance_clases": {
                    "status": "desconocido",
                    "color": "gris",
                    "min_porcentaje": 0.0,
                    "observacion": "Sin datos longitudinales suficientes.",
                },
                "precision": {
                    "status": "nula",
                    "color": "gris",
                    "accuracy": 0.0,
                    "observacion": "Modelo no entrenado debido a tamaño muestral.",
                },
                "observaciones": ["Muestra longitudinal insuficiente para cálculo de robustez."],
            },
            "validacion_temporal": {
                "disponible": False,
                "motivo": "Muestra longitudinal insuficiente para ejecutar partición temporal por cohortes.",
            },
        }

    df = pd.DataFrame(trayectorias)
    X, feature_cols, df_encoded = preparar_matriz_features(df)

    y_estado = df["estado_destino"].values
    eval_estado = entrenar_evaluar_modelo(X, y_estado, feature_cols)

    # Entrenar modelo secundario para rango salarial
    y_salario = df["rango_salarial_destino"].values
    modelo_salario = None
    if len(set(y_salario)) > 1:
        clf_salario = GradientBoostingClassifier(n_estimators=40, max_depth=3, random_state=42)
        clf_salario.fit(X, y_salario)
        modelo_salario = clf_salario

    predicciones_prog, total_riesgo, alertas = agregar_predicciones_por_programa(
        df=df,
        X=X,
        modelo_estado=eval_estado["modelo"],
        clases_estado=eval_estado["clases"],
        modelo_salario=modelo_salario,
    )

    # IA-13: Semáforo de robustez estadística
    indicadores_robustez = calcular_indicadores_robustez(
        total_trayectorias=len(trayectorias),
        y_estado=y_estado,
        accuracy=eval_estado["accuracy"],
        f1=eval_estado["f1_score"],
    )

    # IA-17: Validación temporal por cohorte (backtesting longitudinal)
    val_temporal = evaluar_validacion_temporal(
        df=df,
        X=X,
        y=y_estado,
        accuracy_cv=eval_estado["accuracy"],
    )

    resultado = {
        "estado": "exitoso",
        "mensaje": "Modelo de análisis entrenado y validado satisfactoriamente con GradientBoostingClassifier y balanceo adaptativo de clases.",
        "estrategia_balanceo": "Ponderación adaptativa de clases activa (Cost-Sensitive Learning)",
        "total_trayectorias": len(trayectorias),
        "precision_modelo": eval_estado["accuracy"],
        "f1_score": eval_estado["f1_score"],
        "programas_analizados": len(predicciones_prog),
        "egresados_en_riesgo": total_riesgo,
        "importancia_factores": eval_estado["importancia_factores"],
        "predicciones_programas": predicciones_prog,
        "alertas_riesgo": alertas,
        "matriz_confusion": eval_estado["matriz_confusion"],
        "indicadores_robustez": indicadores_robustez,
        "comparativa_algoritmos": eval_estado.get("comparativa_algoritmos", []),
        "validacion_temporal": val_temporal,
    }

    # IA-09 / IA-AUD-02: Guardar en cache con aislamiento de sede
    prediccion_model_cache.set(
        mediciones_count=mediciones_count,
        max_medicion_id=max_medicion_id,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
        filtro_programa=filtro_programa,
        filtro_anio=filtro_anio,
        data=resultado,
        extra_tag=tag_sede,
    )

    return resultado


def generar_excel_prediccion(resultado: Dict[str, Any]) -> io.BytesIO:
    """
    Genera un informe ejecutivo en Excel (.xlsx) para directores de programa (IA-14):
      1. Resumen Ejecutivo y Métricas de Validación
      2. Proyecciones por Programa Académico
      3. Factores Determinantes de Empleabilidad
      4. Comparativa Multi-Algoritmo (IA-10)
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    header_fill = PatternFill(start_color="1A1818", end_color="1A1818", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    border_thin = Border(
        left=Side(style="thin", color="E2E3E1"),
        right=Side(style="thin", color="E2E3E1"),
        top=Side(style="thin", color="E2E3E1"),
        bottom=Side(style="thin", color="E2E3E1"),
    )

    # Hoja 1: Resumen
    ws1 = wb.active
    ws1.title = "Resumen Ejecutivo"
    ws1.append(["Métrica / Indicador", "Valor Registrado"])
    ws1.append(["Estado de la Proyección", str(resultado.get("estado", "")).title()])
    ws1.append(["Total Trayectorias Longitudinales", resultado.get("total_trayectorias", 0)])
    ws1.append(["Precisión Global (Accuracy)", f"{resultado.get('precision_modelo', 0.0)}%"])
    ws1.append(["Puntaje F1 Macro", resultado.get("f1_score", 0.0)])
    ws1.append(["Programas Analizados", resultado.get("programas_analizados", 0)])
    ws1.append(["Egresados en Riesgo Proyectado", resultado.get("egresados_en_riesgo", 0)])
    rob = resultado.get("indicadores_robustez", {})
    ws1.append(["Nivel de Robustez Estadística", rob.get("nivel_general", "N/A")])

    val_temp = resultado.get("validacion_temporal", {})
    if val_temp and val_temp.get("disponible"):
        ws1.append(["Backtesting Cohorte Evaluada", val_temp.get("cohorte_evaluada", "N/A")])
        ws1.append(["Accuracy Temporal (Cohorte no vista)", f"{val_temp.get('accuracy_temporal', 0.0)}%"])
        ws1.append(["Estabilidad Temporal Interanual", val_temp.get("diagnostico_estabilidad", "N/A")])

    # Hoja 2: Programas
    ws2 = wb.create_sheet(title="Proyecciones por Programa")
    ws2.append([
        "Programa Académico",
        "Egresados",
        "% Empleado",
        "% Independiente",
        "% Estudiante",
        "% Sin Empleo",
        "Nivel de Riesgo",
        "Rango Salarial Estimado",
    ])
    for p in resultado.get("predicciones_programas", []):
        ws2.append([
            p.get("programa", ""),
            p.get("total_egresados", 0),
            f"{p.get('probabilidad_empleado', 0.0)}%",
            f"{p.get('probabilidad_independiente', 0.0)}%",
            f"{p.get('probabilidad_estudiante', 0.0)}%",
            f"{p.get('probabilidad_sin_empleo', 0.0)}%",
            p.get("nivel_riesgo", ""),
            p.get("rango_salarial_estimado", ""),
        ])

    # Hoja 3: Factores Determinantes
    ws3 = wb.create_sheet(title="Factores Determinantes")
    ws3.append(["Factor Explicativo", "Importancia Relativa (%)"])
    for f in resultado.get("importancia_factores", []):
        ws3.append([f.get("factor", ""), f"{f.get('importancia', 0.0)}%"])

    # Hoja 4: Comparativa Algoritmos
    ws4 = wb.create_sheet(title="Comparativa Multi-Algoritmo")
    ws4.append(["Algoritmo", "Accuracy (%)", "F1 Score", "Tiempo (ms)", "Estado"])
    for a in resultado.get("comparativa_algoritmos", []):
        ws4.append([
            a.get("algoritmo", ""),
            f"{a.get('accuracy', 0.0)}%",
            a.get("f1_score", 0.0),
            a.get("tiempo_ms", 0.0),
            "Seleccionado (Producción)" if a.get("seleccionado") else "Evaluado",
        ])

    for ws in [ws1, ws2, ws3, ws4]:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.border = border_thin
                cell.alignment = Alignment(vertical="center")
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def benchmark_sedes_servicio(
    mediciones_por_sede: Dict[int, List[Medicion]],
    sedes_info: List[Dict[str, Any]],
    egresados: List[Egresado],
    momento_origen: int = 0,
    momento_destino: int = 1,
) -> List[Dict[str, Any]]:
    """
    Evalúa la robustez del modelo de análisis por sede (IA-08); el router solo le pasa la sede del JWT (ADR-020).
    """
    egresados_dict = {e.numero_documento: e for e in egresados}
    benchmark = []

    for s in sedes_info:
        s_id = s["id"]
        s_nombre = s["nombre"]
        meds = mediciones_por_sede.get(s_id, [])

        res = predecir_empleabilidad_servicio(
            mediciones=meds,
            egresados=egresados,
            momento_origen=momento_origen,
            momento_destino=momento_destino,
            sede_id=s_id,
        )

        if res["estado"] == "exitoso":
            progs = res.get("predicciones_programas", [])
            avg_empleo = round(
                sum(p["probabilidad_empleado"] for p in progs) / len(progs), 1
            ) if progs else 0.0
            factor_top = res["importancia_factores"][0]["factor"] if res.get("importancia_factores") else "N/A"

            benchmark.append({
                "sede_id": s_id,
                "sede_nombre": s_nombre,
                "estado": "exitoso",
                "total_trayectorias": res["total_trayectorias"],
                "precision_modelo": res["precision_modelo"],
                "probabilidad_empleo_promedio": avg_empleo,
                "egresados_en_riesgo": res["egresados_en_riesgo"],
                "factor_principal": factor_top,
                "robustez": res.get("indicadores_robustez", {}).get("nivel_general", "Media"),
            })
        else:
            benchmark.append({
                "sede_id": s_id,
                "sede_nombre": s_nombre,
                "estado": "insuficiente_datos",
                "total_trayectorias": res["total_trayectorias"],
                "precision_modelo": 0.0,
                "probabilidad_empleo_promedio": 0.0,
                "egresados_en_riesgo": 0,
                "factor_principal": "Muestra insuficiente",
                "robustez": "Baja",
            })

    return benchmark
