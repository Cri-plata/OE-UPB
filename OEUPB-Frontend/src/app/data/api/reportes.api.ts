import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { ExploradorInitResponse, ExploradorResponse, KpisResponse, TendenciasResponse } from './generated-api.models';

export interface FiltrosExplorador {
  pregunta: string;
  momento?: number;
  programa?: string;
  anio?: number;
}

@Injectable({ providedIn: 'root' })
export class ReportesApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/reportes`;

  general(): Observable<KpisResponse> { return this.http.get<KpisResponse>(`${this.url}/general`); }
  tendencias(indicador: string): Observable<TendenciasResponse> {
    return this.http.get<TendenciasResponse>(`${this.url}/tendencias`, { params: { indicador } });
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
