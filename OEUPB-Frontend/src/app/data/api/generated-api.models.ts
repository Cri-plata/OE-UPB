// Archivo generado desde OEUPB-Docs/specs/api/openapi.json.
// No editar manualmente; ejecute: npm run generate:api

export interface AlertaResponse {
  "tipo": "empleabilidad" | "texto_abierto";
  "programa": string;
  "momento"?: number | null;
  "severidad": "media" | "alta";
  "mensaje": string;
  "valor": number;
  "muestra": number;
}

export interface AlertaRiesgoItem {
  "programa": string;
  "severidad": string;
  "mensaje": string;
  "riesgo_estimado": number;
  "tamano_muestra": number;
}

export interface AnaliticaResponse {
  "textos_analizados": number;
  "competencias": Array<CompetenciaResponse>;
  "alertas": Array<AlertaResponse>;
}

export interface BenchmarkSedeItem {
  "sede_id": number;
  "sede_nombre": string;
  "estado": string;
  "total_trayectorias": number;
  "precision_modelo": number;
  "probabilidad_empleo_promedio": number;
  "egresados_en_riesgo": number;
  "factor_principal": string;
  "robustez": string;
}

export interface Body_procesar_excel_api_carga_excel_post {
  "momento": number;
  "anio": number;
  "file": string;
}

export interface CambioContrasenaTemporalRequest {
  "nuevaContrasena": string;
  "confirmarContrasena": string;
}

export interface CandidataEmergente {
  "termino": string;
  "score_tfidf": number;
  "frecuencia_documentos": number;
}

export interface CargaRechazadaResponse {
  "detail": DetalleCargaRechazada;
}

export interface CargaResponse {
  "mensaje": string;
  "errores"?: Array<ErrorFila>;
  "carga_id"?: number | null;
  "version"?: number | null;
  "estado"?: string | null;
  "registros"?: number | null;
}

export interface ChartDatasetResponse {
  "label": string;
  "data": Array<number | null>;
  "borderColor"?: string | null;
  "backgroundColor"?: string | null;
  "borderWidth"?: number | null;
  "pointBackgroundColor"?: string | null;
  "pointBorderColor"?: string | null;
  "pointBorderWidth"?: number | null;
  "pointRadius"?: number | null;
  "pointHoverRadius"?: number | null;
  "fill"?: boolean | null;
  "tension"?: number | null;
  "spanGaps"?: boolean | null;
}

export interface ComparacionProgramaResponse {
  "programa": string;
  "pares": number;
  "suficiente": boolean;
  "valor_inicial"?: number | null;
  "valor_final"?: number | null;
}

export interface ComparacionResponse {
  "momento_inicial": number;
  "momento_final": number;
  "indicador": string;
  "minimo_pares": number;
  "programas": Array<ComparacionProgramaResponse>;
}

export interface ComparativaAlgoritmoItem {
  "algoritmo": string;
  "accuracy": number;
  "f1_score": number;
  "tiempo_ms": number;
  "seleccionado": boolean;
}

export interface CompetenciaResponse {
  "categoria": string;
  "frecuencia": number;
}

export interface CurarHabilidadRequest {
  "termino_original": string;
  "etiqueta_canonica": string;
  "tipo"?: string;
  "variantes"?: Array<string>;
  "estado"?: string;
}

export interface CurarHabilidadResponse {
  "mensaje": string;
  "curada": HabilidadCuradaItem;
}

export interface DatasetGrafica {
  "label": string;
  "data": Array<number | null>;
  "backgroundColor"?: string | Array<string> | null;
  "borderColor"?: string | null;
}

export interface DefinicionGrafica {
  "origen": "reporte_general" | "tendencias" | "explorador";
  "tipo_visualizacion": "bar" | "line" | "pie" | "doughnut";
  "indicador"?: string | null;
  "pregunta"?: string | null;
  "momento"?: 0 | 1 | 5 | null;
  "programa"?: string | null;
  "anio"?: number | null;
  "programas"?: Array<string> | null;
  "anios"?: Array<number> | null;
}

export interface DetalleCargaRechazada {
  "mensaje": string;
  "errores": Array<ErrorFila>;
}

export interface DirectorioItem {
  "documento": string;
  "nombre_completo": string;
  "programa": string | null;
  "fecha_grado": string;
  "encuestas": string;
}

export interface DirectorioResponse {
  "total": number;
  "page": number;
  "limit": number;
  "data": Array<DirectorioItem>;
}

export interface EgresadoManualRequest {
  "numero_documento": string;
  "primer_nombre": string;
  "primer_apellido"?: string | null;
  "programa": string;
  "fecha_grado"?: string | null;
  "motivo": string;
}

export interface EgresadoManualUpdate {
  "primer_nombre"?: string | null;
  "primer_apellido"?: string | null;
  "programa"?: string | null;
  "fecha_grado"?: string | null;
  "motivo": string;
}

export interface EliminarCargaRequest {
  "motivo": string;
}

export interface EliminarCuraduriaResponse {
  "mensaje": string;
}

export interface EliminarEgresadoRequest {
  "motivo": string;
}

export interface EncuestaPerfilResponse {
  "momento": number;
  "anio": number;
  "empleabilidad": unknown;
  "salario": unknown;
  "respuestas_completas": Record<string, unknown>;
}

export interface ErrorCodificado {
  "codigo": string;
  "mensaje": string;
}

export interface ErrorFila {
  "fila": number;
  "columna": string;
  "error": string;
}

export interface ErrorResponse {
  "detail": string | ErrorCodificado;
}

export interface EstadisticasAnalisis {
  "total_respuestas_analizadas": number;
  "respuestas_con_habilidad": number;
  "respuestas_sin_habilidad": number;
}

export interface ExploradorInitResponse {
  "preguntas": Array<string>;
  "programas": Array<string>;
  "anios": Array<number>;
}

export interface ExploradorResponse {
  "labels": Array<string>;
  "valores": Array<number>;
}

export interface FiltrosDisponiblesResponse {
  "programas": Array<string>;
  "anios": Array<number>;
  "momentos": Array<number>;
}

export interface HTTPValidationError {
  "detail"?: Array<ValidationError>;
}

export interface HabilidadComparativaItem {
  "habilidad": string;
  "tipo": string;
  "m0_menciones": number;
  "m0_pct": number;
  "m0_porcentaje"?: number | null;
  "m1_menciones": number;
  "m1_pct": number;
  "m1_porcentaje"?: number | null;
  "m5_menciones": number;
  "m5_pct": number;
  "m5_porcentaje"?: number | null;
  "delta_m1_m0": number;
  "tendencia": string;
  "total_menciones": number;
}

export interface HabilidadCuradaItem {
  "id": number;
  "termino_original": string;
  "etiqueta_canonica": string;
  "tipo": string;
  "variantes": Array<string>;
  "estado": string;
  "creado_por_id": number;
  "creado_por_correo": string;
  "fecha_creacion": string;
}

export interface HabilidadReconocida {
  "habilidad": string;
  "tipo": string;
  "menciones": number;
}

export interface HabilidadesComparativaResponse {
  "comparativa": Array<HabilidadComparativaItem>;
  "totales_respuestas": Record<string, number>;
  "totales_con_habilidad": Record<string, number>;
}

export interface HabilidadesDemandadasResponse {
  "habilidades_reconocidas": Array<HabilidadReconocida>;
  "candidatas_emergentes": Array<CandidataEmergente>;
  "estadisticas": EstadisticasAnalisis;
}

export interface HealthResponse {
  "status": string;
}

export interface HistorialCargaItem {
  "id": number;
  "momento": number;
  "anio": number;
  "nombre": string;
  "nombre_archivo": string;
  "fecha_carga": string;
  "version": number;
  "registros": number;
  "estado": string;
}

export interface ImportanciaFactorItem {
  "factor": string;
  "importancia": number;
}

export interface KpisResponse {
  "total_egresados": number;
  "total_encuestados": number;
  "tasa_empleabilidad": number;
  "tasa_formalidad"?: number | null;
  "tasa_informalidad"?: number | null;
  "observaciones_formalidad": number;
  "promedio_salarial": number;
  "rango_salarial"?: RangoSalarialResponse | null;
  "distribucion_estado_laboral": Record<string, number>;
  "distribucion_programas": Record<string, unknown>;
  "nivel_satisfaccion": Record<string, unknown>;
}

export interface LoginRequest {
  "correoInstitucional": string;
  "contrasena": string;
}

export interface LoginResponse {
  "token": string;
  "usuario": UsuarioLoginResponse;
}

export interface MatrizConfusionData {
  "clases": Array<string>;
  "matriz": Array<Array<number>>;
}

export interface MensajeResponse {
  "mensaje": string;
}

export interface MetricasGrafica {
  "labels": Array<string>;
  "datasets": Array<DatasetGrafica>;
}

export interface MotivoRequest {
  "motivo": string;
}

export interface OperacionEgresadoResponse {
  "documento": string;
  "estado": string;
}

export interface PerfilEgresadoResponse {
  "documento": string;
  "id_estudiante"?: string | null;
  "nombre_completo": string;
  "programa": string | null;
  "fecha_grado": string;
  "encuestas": Array<EncuestaPerfilResponse>;
}

export interface PrediccionEmpleabilidadResponse {
  "estado": string;
  "mensaje": string;
  "total_trayectorias": number;
  "precision_modelo": number;
  "f1_score": number;
  "programas_analizados": number;
  "egresados_en_riesgo": number;
  "importancia_factores": Array<ImportanciaFactorItem>;
  "predicciones_programas": Array<PrediccionProgramaItem>;
  "alertas_riesgo": Array<AlertaRiesgoItem>;
  "matriz_confusion": MatrizConfusionData;
  "indicadores_robustez"?: Record<string, unknown> | null;
  "comparativa_algoritmos"?: Array<ComparativaAlgoritmoItem> | null;
  "validacion_temporal"?: ValidacionTemporalData | null;
}

export interface PrediccionProgramaItem {
  "programa": string;
  "total_egresados": number;
  "probabilidad_empleado": number;
  "probabilidad_independiente": number;
  "probabilidad_estudiante": number;
  "probabilidad_sin_empleo": number;
  "nivel_riesgo": string;
  "rango_salarial_estimado": string;
}

export interface PublicacionCreate {
  "grafica_key": string;
  "titulo": string;
  "definicion": DefinicionGrafica;
  "aprobada_privacidad": boolean;
}

export interface PublicacionResponse {
  "id": number;
  "grafica_key": string;
  "titulo": string;
  "sede_id": number;
  "sede_nombre": string;
  "programas": Array<string>;
  "permiso_requerido": string;
  "definicion": DefinicionGrafica;
  "metricas": MetricasGrafica;
  "version": number;
  "estado": string;
  "aprobada_privacidad": boolean;
  "fecha_publicacion": string;
  "fecha_retiro": string | null;
}

export interface RangoSalarialResponse {
  "minimo": number;
  "mediana": number;
  "maximo": number;
  "observaciones": number;
}

export interface ReemisionCredencialRequest {
  "motivo": string;
}

export interface ReemisionCredencialResponse {
  "usuario": UsuarioResponse;
  "contrasena_temporal": string;
  "credencial_temporal_expira_en": string;
}

export interface ReglaAsociacionItem {
  "si_menciona": string;
  "tambien_menciona": string;
  "ocurrencias": number;
  "soporte": number;
  "confianza": number;
  "lift": number;
}

export interface ReglasAsociacionResponse {
  "total_respuestas": number;
  "transacciones_validas": number;
  "transacciones_insuficientes": number;
  "total_reglas": number;
  "reglas": Array<ReglaAsociacionItem>;
}

export interface SedeResponse {
  "id": number;
  "codigo": string;
  "nombre": string;
}

export interface TendenciasResponse {
  "labels": Array<string>;
  "datasets": Array<ChartDatasetResponse>;
}

export interface UsuarioCreateRequest {
  "nombre": string;
  "correo": string;
  "numero_documento": string;
  "rol": "Coordinador_Sede" | "Usuario_Consulta";
  "sede_id"?: number | null;
  "etiqueta"?: "Rector" | "Profesor" | "Administrativo" | null;
  "permisos"?: Array<"ver_reporte_general" | "ver_tendencias" | "ver_explorador" | "ver_publicaciones">;
  "programas"?: Array<string>;
}

export interface UsuarioCreateResponse {
  "id": number;
  "nombre": string;
  "correo": string;
  "rol": "Admin_CTIC" | "Coordinador_Sede" | "Usuario_Consulta";
  "sede_id"?: number | null;
  "debe_cambiar_contrasena": boolean;
  "credencial_temporal_expira_en"?: string | null;
  "activo": boolean;
  "version_autorizacion": number;
  "etiqueta"?: "Rector" | "Profesor" | "Administrativo" | null;
  "permisos": Array<"ver_reporte_general" | "ver_tendencias" | "ver_explorador" | "ver_publicaciones">;
  "programas": Array<string>;
  "programas_sin_datos"?: Array<string>;
  "contrasena_temporal": string;
  "modo_credencial": "documento" | "random";
}

export interface UsuarioLoginResponse {
  "id": number;
  "nombre": string;
  "correo": string;
  "rol": "Admin_CTIC" | "Coordinador_Sede" | "Usuario_Consulta";
  "sedeId": number | null;
  "debeCambiarContrasena": boolean;
}

export interface UsuarioResponse {
  "id": number;
  "nombre": string;
  "correo": string;
  "rol": "Admin_CTIC" | "Coordinador_Sede" | "Usuario_Consulta";
  "sede_id"?: number | null;
  "debe_cambiar_contrasena": boolean;
  "credencial_temporal_expira_en"?: string | null;
  "activo": boolean;
  "version_autorizacion": number;
  "etiqueta"?: "Rector" | "Profesor" | "Administrativo" | null;
  "permisos": Array<"ver_reporte_general" | "ver_tendencias" | "ver_explorador" | "ver_publicaciones">;
  "programas": Array<string>;
  "programas_sin_datos"?: Array<string>;
}

export interface UsuarioUpdateRequest {
  "nombre"?: string | null;
  "sede_id"?: number | null;
  "etiqueta"?: "Rector" | "Profesor" | "Administrativo" | null;
  "permisos"?: Array<"ver_reporte_general" | "ver_tendencias" | "ver_explorador" | "ver_publicaciones"> | null;
  "programas"?: Array<string> | null;
}

export interface ValidacionTemporalData {
  "disponible": boolean;
  "motivo"?: string | null;
  "cohorte_evaluada"?: number | null;
  "tamano_muestra_prueba"?: number | null;
  "tamano_muestra_entrenamiento"?: number | null;
  "accuracy_temporal"?: number | null;
  "f1_temporal"?: number | null;
  "diagnostico_estabilidad"?: string | null;
  "color_estabilidad"?: string | null;
}

export interface ValidationError {
  "loc": Array<string | number>;
  "msg": string;
  "type": string;
  "input"?: unknown;
  "ctx"?: Record<string, unknown>;
}
