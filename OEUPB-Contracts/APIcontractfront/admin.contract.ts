export interface UsuarioResponseDto {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  sede_id: number | null;
  debe_cambiar_contrasena: boolean;
  credencial_temporal_expira_en: string | null;
  activo: boolean;
  version_autorizacion: number;
  etiqueta: 'Rector' | 'Profesor' | 'Administrativo' | null;
  permisos: string[];
  programas: string[];
}

export interface UsuarioCreateResponseDto extends UsuarioResponseDto {
  contrasena_temporal: string;
  modo_credencial: 'documento' | 'random';
}

export interface UsuarioCreateDto {
  nombre: string;
  correo: string;
  numero_documento: string;
  rol: string;
  sede_id: number | null;
  etiqueta?: 'Rector' | 'Profesor' | 'Administrativo' | null;
  permisos?: string[];
  programas?: string[];
}
