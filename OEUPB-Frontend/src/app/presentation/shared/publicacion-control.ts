import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs';

import { PublicacionesApi } from '../../data/api/publicaciones.api';
import { PublicacionCreate, PublicacionResponse } from '../../data/api/generated-api.models';
import { mensajeDeError } from './mensaje-error';

/**
 * Estado de publicación de las gráficas de una vista.
 *
 * La aplicación es zoneless: el estado vive en signals para que la vista se
 * actualice en cuanto responde el backend, sin depender de otra interacción.
 * Se provee por componente (`providers: [PublicacionControl]`).
 */
@Injectable()
export class PublicacionControl {
  private readonly api = inject(PublicacionesApi);

  private readonly publicaciones = signal<Record<string, PublicacionResponse>>({});
  private readonly errores = signal<Record<string, string>>({});
  /** Clave de la gráfica con una solicitud en curso; bloquea envíos duplicados. */
  readonly enCurso = signal<string | null>(null);
  readonly ocupado = computed(() => this.enCurso() !== null);
  /** Error al consultar el estado de publicación; sin él la vista no sabe qué está publicado. */
  readonly errorCarga = signal('');

  cargarPropias(): void {
    this.errorCarga.set('');
    this.api.listarPropias().subscribe({
      next: publicaciones => this.publicaciones.set(
        Object.fromEntries(publicaciones.map(publicacion => [publicacion.grafica_key, publicacion]))
      ),
      error: (error: unknown) => this.errorCarga.set(
        mensajeDeError(error, 'No fue posible consultar el estado de publicación.')
      ),
    });
  }

  publicacion(key: string): PublicacionResponse | undefined {
    return this.publicaciones()[key];
  }

  estaPublicada(key: string): boolean {
    return this.publicacion(key) !== undefined;
  }

  procesando(key: string): boolean {
    return this.enCurso() === key;
  }

  error(key: string): string {
    return this.errores()[key] ?? '';
  }

  publicar(key: string, payload: PublicacionCreate): void {
    if (this.ocupado()) return;
    this.iniciar(key);
    this.api.publicar(payload).pipe(finalize(() => this.enCurso.set(null))).subscribe({
      next: publicacion => this.publicaciones.update(actuales => ({ ...actuales, [key]: publicacion })),
      error: (error: unknown) => this.registrarError(key, error, 'No fue posible publicar la gráfica.'),
    });
  }

  retirar(key: string): void {
    const publicacion = this.publicacion(key);
    if (!publicacion || this.ocupado()) return;
    this.iniciar(key);
    this.api.retirar(publicacion.id).pipe(finalize(() => this.enCurso.set(null))).subscribe({
      next: () => this.publicaciones.update(({ [key]: _retirada, ...resto }) => resto),
      error: (error: unknown) => {
        // 409: ya no estaba activa en backend; se reconcilia la vista con ese estado.
        if (error instanceof HttpErrorResponse && error.status === 409) {
          this.publicaciones.update(({ [key]: _retirada, ...resto }) => resto);
          return;
        }
        this.registrarError(key, error, 'No fue posible retirar la publicación.');
      },
    });
  }

  private iniciar(key: string): void {
    this.enCurso.set(key);
    this.errores.update(({ [key]: _anterior, ...resto }) => resto);
  }

  private registrarError(key: string, error: unknown, respaldo: string): void {
    this.errores.update(actuales => ({ ...actuales, [key]: mensajeDeError(error, respaldo) }));
  }
}
