// OEUPB-Contracts/APIcontractfront/carga.contract.ts

/**
 * DTO para el detalle de un error al subir Excel
 */
export interface FilaErrorDto {
  fila: number;
  cedula: string;
  motivo: 'Cédula duplicada' | 'Cédula vacía' | 'Formato inválido' | 'Doble titulación detectada' | string;
}

/**
 * DTO de respuesta al procesar el Excel (Representa el Mockup del Modal de Errores)
 */
export interface UploadExcelResponseDto {
  filasCargadas: number;
  filasConError: number;
  detallesErrores: FilaErrorDto[];
}
