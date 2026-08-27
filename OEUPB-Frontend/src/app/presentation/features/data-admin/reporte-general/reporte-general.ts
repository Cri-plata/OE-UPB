import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-reporte-general',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective],
  templateUrl: './reporte-general.html',
  styleUrls: ['./reporte-general.scss']
})
export class ReporteGeneralComponent implements OnInit {
  kpis: any = null;
  isChartReady = false;

  public pieChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public pieChartData: ChartData<'doughnut', number[], string | string[]> = { labels: [], datasets: [] };

  public barChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public barChartData: ChartData<'bar', number[], string | string[]> = { labels: [], datasets: [] };

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    // Por ahora usamos datos simulados para impactar en la reunión
    setTimeout(() => {
      this.kpis = {
        total_egresados: 1245,
        tasa_empleabilidad: 87.5,
        promedio_salarial: 3.2
      };

      this.pieChartData = {
        labels: ['Ing. Sistemas', 'Derecho', 'Psicología', 'Arquitectura'],
        datasets: [{ data: [450, 300, 280, 215], backgroundColor: ['#ba0c2f', '#212529', '#6c757d', '#adb5bd'] }]
      };

      this.barChartData = {
        labels: ['Aplicación Conocimientos', 'Retos Intelectuales', 'Estabilidad', 'Ascenso'],
        datasets: [
          { data: [3.8, 3.5, 3.1, 2.8], label: 'Satisfacción', backgroundColor: '#ba0c2f' }
        ]
      };

      this.isChartReady = true;
      this.cdr.detectChanges();
    }, 500);
  }
}
