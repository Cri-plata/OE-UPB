import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-ficha-egresado',
  standalone: true,
  imports: [],
  templateUrl: './ficha-egresado.html',
  styleUrl: './ficha-egresado.scss'
})
export class FichaEgresado {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  cedula: string = '';

  ngOnInit() {
    // Obtenemos la cédula de la URL (ej: /perfil/1020456789)
    this.cedula = this.route.snapshot.paramMap.get('cedula') || 'Desconocida';
  }

  volver() {
    this.router.navigate(['/tendencias']);
  }
}
