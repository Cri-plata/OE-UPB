// OEUPB-Contracts/APIcontractfront/usuarios.contract.ts
import { UsuarioDto } from './auth.contract';

/**
 * DTO para la creación de un nuevo usuario por parte del Admin CTIC
 */
export interface CreateUsuarioRequestDto {
  nombre: string;
  correo: string;
  numero_documento: string;
  rol: 'Coordinador_Sede' | 'Usuario_Consulta';
  sede_id?: number;
  etiqueta?: 'Rector' | 'Profesor' | 'Administrativo';
  permisos?: Array<'ver_reporte_general' | 'ver_tendencias' | 'ver_explorador' | 'ver_publicaciones'>;
  programas?: string[];
}

/**
 * DTO para listar usuarios en la tabla de administración
 */
export interface GetUsuariosResponseDto {
  usuarios: UsuarioDto[];
  totalRegistros: number;
}
