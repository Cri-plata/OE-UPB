import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from './api.config';
import { PublicacionCreate, PublicacionResponse } from './generated-api.models';


@Injectable({ providedIn: 'root' })
export class PublicacionesApi {
  private readonly http = inject(HttpClient);

  listarAutorizadas(): Observable<PublicacionResponse[]> {
    return this.http.get<PublicacionResponse[]>(`${API_BASE_URL}/publicaciones/`);
  }

  listarPropias(): Observable<PublicacionResponse[]> {
    return this.http.get<PublicacionResponse[]>(`${API_BASE_URL}/publicaciones/mias`);
  }

  publicar(payload: PublicacionCreate): Observable<PublicacionResponse> {
    return this.http.post<PublicacionResponse>(`${API_BASE_URL}/publicaciones/`, payload);
  }

  retirar(id: number): Observable<PublicacionResponse> {
    return this.http.delete<PublicacionResponse>(`${API_BASE_URL}/publicaciones/${id}`);
  }
}
