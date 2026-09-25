import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { SedeResponse } from './generated-api.models';

@Injectable({ providedIn: 'root' })
export class SedesApi {
  private readonly http = inject(HttpClient);
  listar(): Observable<SedeResponse[]> {
    return this.http.get<SedeResponse[]>(`${API_BASE_URL}/sedes/`);
  }
}
