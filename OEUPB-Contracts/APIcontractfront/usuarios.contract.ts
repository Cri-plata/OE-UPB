// OEUPB-Contracts/APIcontractfront/usuarios.contract.ts
import { UsuarioDto } from './auth.contract';

/**
 * DTO para la creación de un nuevo usuario por parte del Admin CTIC
 */
export interface CreateUsuarioRequestDto {
  nombre: string;
  correo: string;
  rol: 'Admin_CTIC' | 'Coordinador_Sede' | 'Directivo';
  sedeId?: number; // Requerido si el rol es Coordinador o Directivo
}

/**
 * DTO para listar usuarios en la tabla de administración
 */
export interface GetUsuariosResponseDto {
  usuarios: UsuarioDto[];
  totalRegistros: number;
}
