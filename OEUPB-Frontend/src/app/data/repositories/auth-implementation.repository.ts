import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { AuthRepository } from '../../domain/repositories/auth.repository';
import { Usuario } from '../../domain/models/usuario.model';
import {
  CambioContrasenaTemporalRequest as CambioContrasenaTemporalRequestDto,
  LoginRequest as LoginRequestDto,
  LoginResponse as LoginResponseDto
} from '../api/generated-api.models';
import { API_BASE_URL } from '../api/api.config';

@Injectable({
  providedIn: 'root'
})
export class AuthImplementationRepository implements AuthRepository {
  private readonly API_URL = `${API_BASE_URL}/auth`;
  private readonly TOKEN_KEY = 'jwt_token';
  private readonly USER_KEY = 'user_data';

  constructor(private http: HttpClient) {}

  login(correo: string, contrasena: string): Observable<{ token: string; usuario: Usuario }> {
    const request: LoginRequestDto = { correoInstitucional: correo, contrasena };
    
    return this.http.post<LoginResponseDto>(this.API_URL + '/login', request).pipe(
      tap((response) => {
        localStorage.setItem(this.TOKEN_KEY, response.token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(response.usuario));
      })
    );
  }

  cambiarContrasenaTemporal(nuevaContrasena: string, confirmarContrasena: string): Observable<{ token: string; usuario: Usuario }> {
    const request: CambioContrasenaTemporalRequestDto = { nuevaContrasena, confirmarContrasena };
    return this.http.post<LoginResponseDto>(this.API_URL + '/cambiar-contrasena-temporal', request).pipe(
      tap((response) => {
        localStorage.setItem(this.TOKEN_KEY, response.token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(response.usuario));
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  getUsuarioActual(): Usuario | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (!userStr) return null;
    return JSON.parse(userStr) as Usuario;
  }
}

