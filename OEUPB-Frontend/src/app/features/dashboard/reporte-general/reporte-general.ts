import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-reporte-general',
  standalone: true,
  imports: [],
  templateUrl: './reporte-general.html',
  styleUrl: './reporte-general.scss'
})
export class ReporteGeneral {
  private router = inject(Router);

  irACargaDatos() {
    this.router.navigate(['/carga']);
  }

  irATendencias() {
    this.router.navigate(['/tendencias']);
  }
}
