import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';
import { Router } from '@angular/router';

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
    const sedes: { [key: number]: string } = {
      1: 'Bucaramanga',
      2: 'Medellín',
      3: 'Montería',
      4: 'Palmira',
      5: 'Bogotá'
    };
    this.sedeNombre = sedes[sedeId] || `Sede Desconocida (${sedeId})`;
  }
}

