// OEUPB-Contracts/APIcontractfront/ia.contract.ts

/**
 * DTO para la alerta predictiva de Riesgo de Desempleo (Scikit-Learn)
 */
export interface RiesgoDesempleoResponseDto {
  cohorte: string;
  programa: string;
  probabilidadDesempleo: number; // 0.0 a 100.0
  nivelAlerta: 'Alta' | 'Media' | 'Baja';
}

/**
 * DTO para la gráfica de habilidades (NLP) extraídas de texto libre
 */
export interface HabilidadDto {
  nombreHabilidad: string;
  frecuenciaPorcentaje: number; // Ej. 78% "Análisis de datos"
}

export interface HabilidadesNLPResponseDto {
  habilidades: HabilidadDto[];
}
