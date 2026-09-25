// OEUPB-Contracts/APIcontractfront/auth.contract.ts

/**
 * DTO para la petición de Inicio de Sesión (Capa de Infraestructura / Clean Architecture)
 */
export interface LoginRequestDto {
  correoInstitucional: string;
  contrasena: string;
}

/**
 * DTO para la respuesta del Inicio de Sesión
 */
export interface LoginResponseDto {
  token: string;
  usuario: UsuarioDto;
}

/**
 * Entidad de Usuario transferida al Frontend
 */
export interface UsuarioDto {
  id: number;
  nombre: string;
  correo: string;
  rol: 'Admin_CTIC' | 'Coordinador_Sede' | 'Usuario_Consulta';
  sedeId: number | null; // Nullable para Admin_CTIC
  debeCambiarContrasena: boolean;
}

export interface CambioContrasenaTemporalRequestDto {
  nuevaContrasena: string;
  confirmarContrasena: string;
}
