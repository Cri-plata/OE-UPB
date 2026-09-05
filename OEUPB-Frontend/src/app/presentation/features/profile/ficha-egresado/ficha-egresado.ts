import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ChangeDetectorRef } from '@angular/core';

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
  private http = inject(HttpClient);
  private cdr = inject(ChangeDetectorRef);

  cedula: string = '';
  perfil: any = null;
  cargando: boolean = true;
  error: string | null = null;

  ngOnInit() {
    this.cedula = this.route.snapshot.paramMap.get('cedula') || '';
    if (this.cedula) {
      this.cargarPerfil();
    }
  }

  cargarPerfil() {
    this.http.get<any>(`http://localhost:8000/api/directorio/perfil/${this.cedula}`).subscribe({
      next: (data) => {
        this.perfil = data;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = "No se pudo cargar la información del egresado.";
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  volver() {
    this.router.navigate(['/directorio']);
  }
}
