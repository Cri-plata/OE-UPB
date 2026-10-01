import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { DirectorioApi } from '../../../../data/api/directorio.api';
import { PerfilEgresadoResponse } from '../../../../data/api/generated-api.models';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';

@Component({
  selector: 'app-ficha-egresado',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  templateUrl: './ficha-egresado.html',
  styleUrls: ['./ficha-egresado.scss']
})
export class FichaEgresado implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private directorioApi = inject(DirectorioApi);

  cedula: string = '';
  // Signals: la aplicación es zoneless y la vista debe reflejar la respuesta sin otra interacción.
  readonly perfil = signal<PerfilEgresadoResponse | null>(null);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit() {
    this.cedula = this.route.snapshot.paramMap.get('cedula') || '';
    if (this.cedula) {
      this.cargarPerfil();
    }
  }

  cargarPerfil() {
    this.directorioApi.perfil(this.cedula).subscribe({
      next: (data) => {
        this.perfil.set(data);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar la información del egresado.');
        this.cargando.set(false);
      }
    });
  }

  volver() {
    this.router.navigate(['/directorio']);
  }
}
