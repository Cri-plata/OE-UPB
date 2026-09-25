import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { DirectorioResponse, PerfilEgresadoResponse } from './generated-api.models';

@Injectable({ providedIn: 'root' })
export class DirectorioApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/directorio`;

  programas(): Observable<string[]> { return this.http.get<string[]>(`${this.url}/programas`); }
  buscar(page: number, limit: number, q?: string, programa?: string): Observable<DirectorioResponse> {
    let params = new HttpParams().set('page', page).set('limit', limit);
    if (q) params = params.set('q', q);
    if (programa) params = params.set('programa', programa);
    return this.http.get<DirectorioResponse>(`${this.url}/tabla`, { params });
  }
  perfil(documento: string): Observable<PerfilEgresadoResponse> {
    return this.http.get<PerfilEgresadoResponse>(`${this.url}/perfil/${encodeURIComponent(documento)}`);
  }
  crear(payload: Record<string, string | null>): Observable<{documento: string; estado: string}> {
    return this.http.post<{documento: string; estado: string}>(`${this.url}/egresados`, payload);
  }
  editar(documento: string, payload: Record<string, string | null>): Observable<{documento: string; estado: string}> {
    return this.http.patch<{documento: string; estado: string}>(`${this.url}/egresados/${encodeURIComponent(documento)}`, payload);
  }
  eliminar(documento: string, motivo: string): Observable<{documento: string; estado: string}> {
    return this.http.delete<{documento: string; estado: string}>(`${this.url}/egresados/${encodeURIComponent(documento)}`, { body: { motivo } });
  }
  exportar(q?: string, programa?: string): Observable<Blob> {
    let params = new HttpParams();
    if (q) params = params.set('q', q);
    if (programa) params = params.set('programa', programa);
    return this.http.get(`${this.url}/exportar.xlsx`, { params, responseType: 'blob' });
  }
}
