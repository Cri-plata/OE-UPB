import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-directorio',
  standalone: true,
  imports: [CommonModule, SidebarComponent, FormsModule],
  templateUrl: './directorio.html',
  styleUrls: ['./directorio.scss']
})
export class DirectorioComponent implements OnInit {
  terminoBusqueda: string = '';
  programaSeleccionado: string = '';
  
  programasDisponibles: string[] = [];
  egresados: any[] = [];
  
  paginaActual: number = 1;
  totalRegistros: number = 0;
  registrosPorPagina: number = 50;
  
  cargando: boolean = false;

  private API_URL = 'http://localhost:8000/api/directorio';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit() {
    this.cargarProgramas();
    this.buscar();
  }

  cargarProgramas() {
    this.http.get<string[]>(`${this.API_URL}/programas`).subscribe(data => {
      this.programasDisponibles = data;
    });
  }

  buscar() {
    this.cargando = true;
    let url = `${this.API_URL}/tabla?page=${this.paginaActual}&limit=${this.registrosPorPagina}`;
    
    if (this.terminoBusqueda.trim() !== '') {
      url += `&q=${encodeURIComponent(this.terminoBusqueda)}`;
    }
    if (this.programaSeleccionado !== '') {
      url += `&programa=${encodeURIComponent(this.programaSeleccionado)}`;
    }

    this.http.get<any>(url).subscribe({
      next: (res) => {
        this.egresados = res.data;
        this.totalRegistros = res.total;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  onFiltroChange() {
    this.paginaActual = 1;
    this.buscar();
  }

  cambiarPagina(delta: number) {
    const nuevaPagina = this.paginaActual + delta;
    if (nuevaPagina >= 1 && nuevaPagina <= this.getTotalPaginas()) {
      this.paginaActual = nuevaPagina;
      this.buscar();
    }
  }

  getTotalPaginas(): number {
    return Math.ceil(this.totalRegistros / this.registrosPorPagina);
  }

  verPerfil(documento: string) {
    this.router.navigate(['/perfil', documento]);
  }
}


