export interface UsuarioResponseDto {
  id: number;
  nombre: string;
  correo: string;
  rol: string;
  sede_id: string | null;
}

export interface UsuarioCreateDto {
  nombre: string;
  correo: string;
  rol: string;
  sede: string | null;
}
