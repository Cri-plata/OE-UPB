import { Observable } from 'rxjs';
import { Usuario } from '../models/usuario.model';

export abstract class AuthRepository {
  abstract login(correo: string, contrasena: string): Observable<{ token: string, usuario: Usuario }>;
  abstract logout(): void;
  abstract getUsuarioActual(): Usuario | null;
}
