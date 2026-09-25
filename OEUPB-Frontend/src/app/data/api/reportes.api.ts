import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import {
  ComparacionResponse,
  ExploradorInitResponse,
  ExploradorResponse,
  FiltrosDisponiblesResponse,
  KpisResponse,
  TendenciasResponse,
} from './generated-api.models';

export interface FiltrosExplorador {
  pregunta: string;
  momento?: number;
  programa?: string;
  anio?: number;
}

/** Filtros multiselección del dashboard privado (HU-09). Listas vacías = sin filtro. */
export interface FiltrosAnaliticos {
  programas: string[];
  anios: number[];
  momento?: number;
}

export const SIN_FILTROS: FiltrosAnaliticos = { programas: [], anios: [] };

function paramsDeFiltros(filtros: FiltrosAnaliticos, params = new HttpParams()): HttpParams {
  filtros.programas.forEach(programa => params = params.append('programas', programa));
  filtros.anios.forEach(anio => params = params.append('anios', anio));
  if (filtros.momento !== undefined) params = params.set('momento', filtros.momento);
  return params;
}

@Injectable({ providedIn: 'root' })
export class ReportesApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/reportes`;

  filtros(): Observable<FiltrosDisponiblesResponse> {
    return this.http.get<FiltrosDisponiblesResponse>(`${this.url}/filtros`);
  }
  general(filtros: FiltrosAnaliticos = SIN_FILTROS): Observable<KpisResponse> {
    return this.http.get<KpisResponse>(`${this.url}/general`, { params: paramsDeFiltros(filtros) });
  }
  tendencias(indicador: string, filtros: FiltrosAnaliticos = SIN_FILTROS): Observable<TendenciasResponse> {
    return this.http.get<TendenciasResponse>(`${this.url}/tendencias`, {
      params: paramsDeFiltros({ ...filtros, momento: undefined }, new HttpParams().set('indicador', indicador)),
    });
  }
  comparacion(momentoInicial: number, momentoFinal: number, indicador: string, filtros: FiltrosAnaliticos = SIN_FILTROS): Observable<ComparacionResponse> {
    const params = new HttpParams()
      .set('momento_inicial', momentoInicial)
      .set('momento_final', momentoFinal)
      .set('indicador', indicador);
    return this.http.get<ComparacionResponse>(`${this.url}/comparacion`, { params: paramsDeFiltros({ ...filtros, momento: undefined }, params) });
  }
  exploradorInit(): Observable<ExploradorInitResponse> { return this.http.get<ExploradorInitResponse>(`${this.url}/explorador/init`); }
  explorar(filtros: FiltrosExplorador): Observable<ExploradorResponse> {
    let params = new HttpParams().set('pregunta', filtros.pregunta);
    if (filtros.momento !== undefined) params = params.set('momento', filtros.momento);
    if (filtros.programa) params = params.set('programa', filtros.programa);
    if (filtros.anio !== undefined) params = params.set('anio', filtros.anio);
    return this.http.get<ExploradorResponse>(`${this.url}/explorador`, { params });
  }
}
