import os

# 1. Fix app.routes.ts
routes_file = r'C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\app.routes.ts'
with open(routes_file, 'r', encoding='utf-8') as f:
    routes_content = f.read()

# El componente se llama LoginComponent
routes_content = routes_content.replace('m => m.Login)', 'm => m.LoginComponent)')
with open(routes_file, 'w', encoding='utf-8') as f:
    f.write(routes_content)

# 2. Fix jwt.interceptor.ts
interceptor_file = r'C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\data\interceptors\jwt.interceptor.ts'
interceptor_content = '''import { HttpInterceptorFn } from '@angular/common/http';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('jwt_token');

  if (token) {
    const clonedRequest = req.clone({
      setHeaders: {
        Authorization: Bearer 
      }
    });
    return next(clonedRequest);
  }

  return next(req);
};
'''
with open(interceptor_file, 'w', encoding='utf-8') as f:
    f.write(interceptor_content)

# 3. Fix auth-implementation.repository.ts
repo_file = r'C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\data\repositories\auth-implementation.repository.ts'
repo_content = '''import { Injectable } from '@angular/core';
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
    
    return this.http.post<LoginResponseDto>(${this.API_URL}/login, request).pipe(
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
'''
with open(repo_file, 'w', encoding='utf-8') as f:
    f.write(repo_content)

print("Archivos corregidos con Python para evitar interpolacion.")
