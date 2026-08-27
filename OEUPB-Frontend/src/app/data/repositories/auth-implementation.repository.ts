import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { AuthRepository } from '../../domain/repositories/auth.repository';
import { Usuario } from '../../domain/models/usuario.model';
import { LoginRequestDto, LoginResponseDto } from '../../../../../OEUPB-Contracts/APIcontractfront/auth.contract';

@Injectable({
  providedIn: 'root'
})
export class AuthImplementationRepository implements AuthRepository {
  private readonly API_URL = 'http://localhost:8000/api/auth';
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

