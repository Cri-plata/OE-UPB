import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';

export interface AnaliticaResumen {
  textos_analizados: number;
  competencias: { categoria: string; frecuencia: number }[];
  alertas: { tipo: string; programa: string; severidad: string; mensaje: string; valor: number; muestra: number }[];
}

@Injectable({ providedIn: 'root' })
export class AnaliticaApi {
  private readonly http = inject(HttpClient);
  resumen(): Observable<AnaliticaResumen> { return this.http.get<AnaliticaResumen>(`${API_BASE_URL}/analitica/resumen`); }
}
