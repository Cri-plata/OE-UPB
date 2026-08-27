export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  rol: 'Admin_CTIC' | 'Coordinador_Sede' | 'Directivo';
  sedeId: number | null;
}
