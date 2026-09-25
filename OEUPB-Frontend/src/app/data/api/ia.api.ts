import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { HabilidadesDemandadasResponse, ReglasAsociacionResponse } from './generated-api.models';

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
}
