import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthRepository } from '../repositories/auth.repository';
import { Usuario } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class LoginUseCase {
  
  constructor(private authRepository: AuthRepository) {}

  /**
   * Ejecuta la lógica de negocio para iniciar sesión.
   * Aquí se pueden agregar validaciones puras de negocio antes de llamar al repositorio.
   */
  execute(correo: string, contrasena: string): Observable<{ token: string, usuario: Usuario }> {
    if (!correo.includes('@upb.edu.co')) {
      throw new Error('Solo se permiten correos institucionales de la UPB.');
    }
    
    if (contrasena.length < 6) {
      throw new Error('La contraseña debe tener al menos 6 caracteres.');
    }

    return this.authRepository.login(correo, contrasena);
  }
}
