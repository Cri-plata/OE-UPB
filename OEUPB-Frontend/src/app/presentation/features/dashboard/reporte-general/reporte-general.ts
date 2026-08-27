import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';

@Component({
  selector: 'app-reporte-general',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  templateUrl: './reporte-general.html',
  styleUrls: ['./reporte-general.scss']
})
export class ReporteGeneralComponent implements OnInit {
  // Datos mockeados funcionales para los KPIs
  kpis = {
    totalEgresados: 0,
    demoraPromedio: 0,
    satisfaccion: 0,
    empleabilidad: 0
  };

  ngOnInit(): void {
    // Simulando carga de datos desde el backend (Dominio)
    setTimeout(() => {
      this.kpis = {
        totalEgresados: 1250,
        demoraPromedio: 3.5,
        satisfaccion: 4.2,
        empleabilidad: 85.5
      };
    }, 800);
  }
}

