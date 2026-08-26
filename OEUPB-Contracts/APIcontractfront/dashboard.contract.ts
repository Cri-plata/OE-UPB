// OEUPB-Contracts/APIcontractfront/dashboard.contract.ts

/**
 * DTO para las métricas generales del "Reporte general de egresados"
 */
export interface ResumenKpiResponseDto {
  totalEgresados: number;
  demoraPromedioMeses: number;
  satisfaccionLaboralSobre5: number;
  tasaEmpleabilidad: number; // Porcentaje 0-100
}

/**
 * DTO para la gráfica comparativa de Tendencias (Momento 1 vs Momento 5)
 */
export interface SerieTiempoDto {
  cohorte: string; // Ej. "2020"
  tasaMomento1: number;
  tasaMomento5: number;
}

export interface TendenciasResponseDto {
  series: SerieTiempoDto[];
}
