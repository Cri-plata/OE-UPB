import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-tendencias',
  standalone: true,
  imports: [],
  templateUrl: './tendencias.html',
  styleUrl: './tendencias.scss'
})
export class Tendencias {
  private router = inject(Router);

  irAFichaEgresado() {
    // Simulamos la búsqueda de una cédula específica para ver el perfil
    this.router.navigate(['/perfil', '1020456789']);
  }
}
