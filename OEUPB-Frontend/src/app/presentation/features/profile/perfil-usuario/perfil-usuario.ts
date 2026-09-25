import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';
import { Router } from '@angular/router';
import { SedesApi } from '../../../../data/api/sedes.api';

@Component({
  selector: 'app-perfil-usuario',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  templateUrl: './perfil-usuario.html',
  styleUrls: ['./perfil-usuario.scss']
})
export class PerfilUsuarioComponent implements OnInit {
  private authRepo = inject(AuthImplementationRepository);
  private router = inject(Router);
  private sedesApi = inject(SedesApi);

  usuario: any = null;
  sedeNombre: string = 'Sin Sede Asignada';

  ngOnInit() {
    this.usuario = this.authRepo.getUsuarioActual();
    if (!this.usuario) {
      this.router.navigate(['/login']);
    } else {
      this.determinarSede(this.usuario.sedeId);
    }
  }

  determinarSede(sedeId: number | null) {
    if (!sedeId) {
      this.sedeNombre = 'Nivel Nacional (Todas las sedes)';
      return;
    }
    this.sedesApi.listar().subscribe({
      next: sedes => {
        this.sedeNombre = sedes.find(s => s.id === sedeId)?.nombre || `Sede desconocida (${sedeId})`;
      },
      error: () => this.sedeNombre = `Sede ${sedeId}`
    });
  }
}

