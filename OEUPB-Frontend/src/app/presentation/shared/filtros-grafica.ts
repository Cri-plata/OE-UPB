import { FiltrosAnaliticos } from '../../data/api/reportes.api';

/** Hash corto y estable para derivar claves de publicación a partir de filtros. */
export function hashCorto(texto: string): string {
  let hash = 0;
  for (let i = 0; i < texto.length; i++) hash = ((hash << 5) - hash + texto.charCodeAt(i)) | 0;
  return Math.abs(hash).toString(36);
}

/**
 * Clave de publicación de una gráfica con filtros: cada combinación de filtros es
 * una gráfica distinta, de modo que publicar un filtro no reemplaza a otro.
 */
export function claveConFiltros(base: string, filtros: FiltrosAnaliticos): string {
  const sinFiltros = !filtros.programas.length && !filtros.anios.length && filtros.momento === undefined;
  if (sinFiltros) return base;
  return `${base}_${hashCorto(`${filtros.programas.join('|')}#${filtros.anios.join('|')}#${filtros.momento ?? ''}`)}`;
}

/** Campos de `DefinicionGrafica` que reproducen los filtros en el recálculo del backend. */
export function definicionDeFiltros(filtros: FiltrosAnaliticos): { programas?: string[]; anios?: number[]; momento?: 0 | 1 | 5 } {
  return {
    ...(filtros.programas.length ? { programas: filtros.programas } : {}),
    ...(filtros.anios.length ? { anios: filtros.anios } : {}),
    ...(filtros.momento !== undefined ? { momento: filtros.momento as 0 | 1 | 5 } : {}),
  };
}

/** Sufijo legible para el título publicado. */
export function descripcionFiltros(filtros: FiltrosAnaliticos): string {
  const partes = [
    filtros.programas.length ? filtros.programas.join(', ') : '',
    filtros.anios.length ? `cohorte ${filtros.anios.join(', ')}` : '',
    filtros.momento !== undefined ? `M${filtros.momento}` : '',
  ].filter(Boolean);
  return partes.length ? ` (${partes.join('; ')})`.slice(0, 120) : '';
}
