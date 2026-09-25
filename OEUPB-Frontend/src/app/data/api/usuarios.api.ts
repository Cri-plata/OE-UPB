import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from './api.config';
import { ReemisionCredencialResponse, UsuarioCreateRequest, UsuarioCreateResponse, UsuarioResponse } from './generated-api.models';

@Injectable({ providedIn: 'root' })
export class UsuariosApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/usuarios`;

  listar(): Observable<UsuarioResponse[]> { return this.http.get<UsuarioResponse[]>(this.url); }
  programasAsignables(): Observable<string[]> { return this.http.get<string[]>(`${this.url}/programas-asignables`); }
  crear(payload: UsuarioCreateRequest): Observable<UsuarioCreateResponse> { return this.http.post<UsuarioCreateResponse>(this.url, payload); }
  actualizar(id: number, payload: object): Observable<UsuarioResponse> { return this.http.patch<UsuarioResponse>(`${this.url}/${id}`, payload); }
  cambiarEstado(id: number, accion: 'desactivar' | 'reactivar'): Observable<UsuarioResponse> { return this.http.post<UsuarioResponse>(`${this.url}/${id}/${accion}`, {}); }
  desactivar(id: number): Observable<unknown> { return this.http.delete(`${this.url}/${id}`); }
  regenerarCredencial(id: number, motivo: string): Observable<ReemisionCredencialResponse> {
    return this.http.post<ReemisionCredencialResponse>(`${this.url}/${id}/regenerar-credencial-temporal`, { motivo });
  }
}
