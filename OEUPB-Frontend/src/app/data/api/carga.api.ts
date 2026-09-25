import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { CargaResponse, HistorialCargaItem, MensajeResponse } from './generated-api.models';

@Injectable({ providedIn: 'root' })
export class CargaApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/carga`;

  cargar(formData: FormData): Observable<CargaResponse> { return this.http.post<CargaResponse>(`${this.url}/excel`, formData); }
  historial(): Observable<HistorialCargaItem[]> { return this.http.get<HistorialCargaItem[]>(`${this.url}/historial`); }
  eliminar(id: number, motivo: string): Observable<MensajeResponse> {
    return this.http.request<MensajeResponse>('DELETE', `${this.url}/archivo/${id}`, { body: { motivo } });
  }
}
