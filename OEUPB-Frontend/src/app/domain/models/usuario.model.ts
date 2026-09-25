export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol: 'Admin_CTIC' | 'Coordinador_Sede' | 'Usuario_Consulta';
  sedeId: number | null;
  debeCambiarContrasena: boolean;
}
