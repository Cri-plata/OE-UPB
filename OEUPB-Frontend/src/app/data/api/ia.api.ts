import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { HabilidadesDemandadasResponse, ReglasAsociacionResponse } from './generated-api.models';

export interface ImportanciaFactorItem {
  factor: string;
  importancia: number;
}

export interface PrediccionProgramaItem {
  programa: string;
  total_egresados: number;
  probabilidad_empleado: number;
  probabilidad_independiente: number;
  probabilidad_estudiante: number;
  probabilidad_sin_empleo: number;
  nivel_riesgo: 'Bajo' | 'Medio' | 'Alto' | string;
  rango_salarial_estimado: string;
}

export interface AlertaRiesgoItem {
  programa: string;
  severidad: string;
  mensaje: string;
  riesgo_estimado: number;
  tamano_muestra: number;
}

export interface MatrizConfusionData {
  clases: string[];
  matriz: number[][];
}

export interface IndicadorDimension {
  status: string;
  color: 'verde' | 'amarillo' | 'rojo' | 'gris' | string;
  observacion: string;
  [key: string]: any;
}

export interface IndicadoresRobustezData {
  nivel_general: 'Alta' | 'Media' | 'Baja' | string;
  color_general: 'verde' | 'amarillo' | 'rojo' | string;
  estrategia_balanceo?: string;
  muestra: IndicadorDimension;
  balance_clases: IndicadorDimension;
  precision: IndicadorDimension;
  observaciones: string[];
}

export interface HabilidadComparativaRow {
  habilidad: string;
  tipo: 'blanda' | 'dura' | string;
  m0_menciones: number;
  m0_porcentaje: number;
  m1_menciones: number;
  m1_porcentaje: number;
  m5_menciones: number;
  m5_porcentaje: number;
  delta_m1_m0: number;
  tendencia: 'crece' | 'decrece' | 'estable' | 'emergente_en_m1' | 'emergente_en_m5' | string;
  total_menciones: number;
}

export interface HabilidadComparativaResponse {
  comparativa: HabilidadComparativaRow[];
  totales_respuestas: { [momento: string]: number };
  totales_con_habilidad: { [momento: string]: number };
}

export interface ComparativaAlgoritmoItem {
  algoritmo: string;
  accuracy: number;
  f1_score: number;
  tiempo_ms: number;
  seleccionado: boolean;
}

export interface BenchmarkSedeItem {
  sede_id: number;
  sede_nombre: string;
  estado: string;
  total_trayectorias: number;
  precision_modelo: number;
  probabilidad_empleo_promedio: number;
  egresados_en_riesgo: number;
  factor_principal: string;
  robustez: string;
}

export interface ValidacionTemporalData {
  disponible: boolean;
  motivo?: string | null;
  cohorte_evaluada?: number | null;
  tamano_muestra_prueba?: number | null;
  tamano_muestra_entrenamiento?: number | null;
  accuracy_temporal?: number | null;
  f1_temporal?: number | null;
  diagnostico_estabilidad?: string | null;
  color_estabilidad?: 'verde' | 'amarillo' | 'naranja' | string | null;
}

export interface HabilidadCuradaItem {
  id: number;
  termino_original: string;
  etiqueta_canonica: string;
  tipo: 'blanda' | 'dura' | string;
  variantes: string[];
  estado: 'aprobada' | 'descartada' | string;
  creado_por_id: number;
  creado_por_correo: string;
  fecha_creacion: string;
}

export interface CurarHabilidadRequest {
  termino_original: string;
  etiqueta_canonica: string;
  tipo: 'blanda' | 'dura' | string;
  variantes?: string[];
  estado: 'aprobada' | 'descartada' | string;
}

export interface CurarHabilidadResponse {
  mensaje: string;
  curada: HabilidadCuradaItem;
}

export interface PrediccionEmpleabilidadResponse {
  estado: 'exitoso' | 'insuficiente_datos' | string;
  mensaje: string;
  total_trayectorias: number;
  precision_modelo: number;
  f1_score: number;
  programas_analizados: number;
  egresados_en_riesgo: number;
  importancia_factores: ImportanciaFactorItem[];
  predicciones_programas: PrediccionProgramaItem[];
  alertas_riesgo: AlertaRiesgoItem[];
  matriz_confusion: MatrizConfusionData;
  indicadores_robustez?: IndicadoresRobustezData;
  comparativa_algoritmos?: ComparativaAlgoritmoItem[];
  validacion_temporal?: ValidacionTemporalData;
  estrategia_balanceo?: string;
}

@Injectable({ providedIn: 'root' })
export class IaApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/ia`;

  habilidadesDemandadas(filtros?: { momento?: string | number; anio?: string | number; programa?: string; top_emergentes?: number }): Observable<HabilidadesDemandadasResponse> {
    let params = new HttpParams();
    if (filtros?.momento !== undefined && filtros?.momento !== null && filtros?.momento !== '') {
      params = params.set('momento', filtros.momento);
    }
    if (filtros?.anio !== undefined && filtros?.anio !== null && filtros?.anio !== '') {
      params = params.set('anio', filtros.anio);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    if (filtros?.top_emergentes) {
      params = params.set('top_emergentes', filtros.top_emergentes);
    }
    return this.http.get<HabilidadesDemandadasResponse>(`${this.url}/habilidades-demandadas`, { params });
  }

  habilidadesComparativa(filtros?: {
    anio?: string | number;
    programa?: string;
    top_n?: number;
  }): Observable<HabilidadComparativaResponse> {
    let params = new HttpParams();
    if (filtros?.anio !== undefined && filtros?.anio !== null && filtros?.anio !== '') {
      params = params.set('anio', filtros.anio);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    if (filtros?.top_n) {
      params = params.set('top_n', filtros.top_n);
    }
    return this.http.get<HabilidadComparativaResponse>(`${this.url}/habilidades-comparativa`, { params });
  }

  exportarHabilidadesExcel(filtros?: {
    momento?: string | number;
    anio?: string | number;
    programa?: string;
  }): Observable<Blob> {
    let params = new HttpParams();
    if (filtros?.momento !== undefined && filtros?.momento !== null && filtros?.momento !== '') {
      params = params.set('momento', filtros.momento);
    }
    if (filtros?.anio !== undefined && filtros?.anio !== null && filtros?.anio !== '') {
      params = params.set('anio', filtros.anio);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    return this.http.get(`${this.url}/habilidades-export`, {
      params,
      responseType: 'blob',
    });
  }

  reglasAsociacion(filtros?: { momento?: string | number; anio?: string | number; programa?: string; min_soporte?: number; min_confianza?: number; min_ocurrencias?: number; top_reglas?: number }): Observable<ReglasAsociacionResponse> {
    let params = new HttpParams();
    if (filtros?.momento !== undefined && filtros?.momento !== null && filtros?.momento !== '') {
      params = params.set('momento', filtros.momento);
    }
    if (filtros?.anio !== undefined && filtros?.anio !== null && filtros?.anio !== '') {
      params = params.set('anio', filtros.anio);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    if (filtros?.min_soporte !== undefined) {
      params = params.set('min_soporte', filtros.min_soporte);
    }
    if (filtros?.min_confianza !== undefined) {
      params = params.set('min_confianza', filtros.min_confianza);
    }
    if (filtros?.min_ocurrencias !== undefined) {
      params = params.set('min_ocurrencias', filtros.min_ocurrencias);
    }
    if (filtros?.top_reglas !== undefined) {
      params = params.set('top_reglas', filtros.top_reglas);
    }
    return this.http.get<ReglasAsociacionResponse>(`${this.url}/reglas-asociacion`, { params });
  }

  prediccionEmpleabilidad(filtros?: {
    momento_origen?: number;
    momento_destino?: number;
    programa?: string;
    anio?: number;
  }): Observable<PrediccionEmpleabilidadResponse> {
    let params = new HttpParams();
    if (filtros?.momento_origen !== undefined && filtros?.momento_origen !== null) {
      params = params.set('momento_origen', filtros.momento_origen);
    }
    if (filtros?.momento_destino !== undefined && filtros?.momento_destino !== null) {
      params = params.set('momento_destino', filtros.momento_destino);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    if (filtros?.anio !== undefined && filtros?.anio !== null) {
      params = params.set('anio', filtros.anio);
    }
    return this.http.get<PrediccionEmpleabilidadResponse>(`${this.url}/prediccion-empleabilidad`, { params });
  }

  exportarPrediccionExcel(filtros?: {
    momento_origen?: number;
    momento_destino?: number;
    programa?: string;
    anio?: number;
  }): Observable<Blob> {
    let params = new HttpParams();
    if (filtros?.momento_origen !== undefined && filtros?.momento_origen !== null) {
      params = params.set('momento_origen', filtros.momento_origen);
    }
    if (filtros?.momento_destino !== undefined && filtros?.momento_destino !== null) {
      params = params.set('momento_destino', filtros.momento_destino);
    }
    if (filtros?.programa) {
      params = params.set('programa', filtros.programa);
    }
    if (filtros?.anio !== undefined && filtros?.anio !== null) {
      params = params.set('anio', filtros.anio);
    }
    return this.http.get(`${this.url}/prediccion-export`, {
      params,
      responseType: 'blob',
    });
  }

  benchmarkSedes(filtros?: {
    momento_origen?: number;
    momento_destino?: number;
  }): Observable<BenchmarkSedeItem[]> {
    let params = new HttpParams();
    if (filtros?.momento_origen !== undefined && filtros?.momento_origen !== null) {
      params = params.set('momento_origen', filtros.momento_origen);
    }
    if (filtros?.momento_destino !== undefined && filtros?.momento_destino !== null) {
      params = params.set('momento_destino', filtros.momento_destino);
    }
    return this.http.get<BenchmarkSedeItem[]>(`${this.url}/prediccion-benchmark-sedes`, { params });
  }

  habilidadesCuradas(): Observable<HabilidadCuradaItem[]> {
    return this.http.get<HabilidadCuradaItem[]>(`${this.url}/habilidades/curadas`);
  }

  curarHabilidad(req: CurarHabilidadRequest): Observable<CurarHabilidadResponse> {
    return this.http.post<CurarHabilidadResponse>(`${this.url}/habilidades/curar`, req);
  }

  eliminarCuraduria(id: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.url}/habilidades/curar/${id}`);
  }
}
