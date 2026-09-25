import { HttpErrorResponse } from '@angular/common/http';

/** Mensaje accionable para un error HTTP: detalle del backend, falta de conexión o texto de respaldo. */
export function mensajeDeError(error: unknown, respaldo: string): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'No hay conexión con el servidor. Verifica tu conexión e inténtalo de nuevo.';
    }
    const detalle = error.error?.detail;
    if (typeof detalle === 'string') return detalle;
    if (typeof detalle?.mensaje === 'string') return detalle.mensaje;
  }
  return `${respaldo} Inténtalo de nuevo.`;
}
