import { Component, OnInit, ChangeDetectorRef, ViewChild, ElementRef } from '@angular/core';
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

  public pieChartType: ChartType = 'doughnut';
  public barChartType: ChartType = 'bar';

  public pieChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public pieChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  public barChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public barChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  @ViewChild('colorPickerPie') colorPickerPie!: ElementRef<HTMLInputElement>;
  @ViewChild('colorPickerBar') colorPickerBar!: ElementRef<HTMLInputElement>;
  clickedBarIndex: number | null = null;
  clickedPieIndex: number | null = null;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.http.get<any>('http://localhost:8000/api/reportes/general').subscribe({
      next: (data) => {
        this.kpis = {
          total_egresados: data.total_egresados,
          tasa_empleabilidad: data.tasa_empleabilidad,
          promedio_salarial: data.promedio_salarial
        };

        const programas = Object.keys(data.distribucion_programas);
        const cantidades = Object.values(data.distribucion_programas) as number[];
        
        // Agregar la cantidad exacta al label
        const labelsConCantidad = programas.map((prog, i) => `${prog} (${cantidades[i]})`);
        
        const baseColors = ['#e63946', '#f4a261', '#e9c46a', '#2a9d8f', '#264653', '#457b9d', '#a8dadc', '#1d3557', '#6c757d', '#343a40', '#000000', '#8338ec', '#ff006e', '#3a86ff', '#ba0c2f'];
        // Asegurar que cada barra tenga su propio color independiente en memoria para que no se vinculen al editarlos
        const bgColors = programas.map((_, i) => baseColors[i % baseColors.length]);

        this.pieChartData = {
          labels: labelsConCantidad,
          datasets: [{ data: cantidades, backgroundColor: bgColors }]
        };

        const satis_keys = Object.keys(data.nivel_satisfaccion);
        const satis_vals = Object.values(data.nivel_satisfaccion) as number[];

        this.barChartData = {
          labels: satis_keys,
          datasets: [
            { data: satis_vals, label: 'Satisfacción Promedio', backgroundColor: ['#ba0c2f', '#cddc39', '#6c757d', '#000000'] }
          ]
        };

        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error("Error cargando reporte general", err);
      }
    });
  }

  changePieChartType(event: any) {
    this.pieChartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }

  changeBarChartType(event: any) {
    this.barChartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }

  onChartClickPie({ event, active }: { event?: any, active?: any[] }) {
    if (active && active.length > 0) {
      this.clickedPieIndex = active[0].index;
      if (this.colorPickerPie) {
        this.colorPickerPie.nativeElement.click();
      }
    }
  }

  onColorChangePie(event: any) {
    const newColor = event.target.value;
    if (this.clickedPieIndex !== null && this.pieChartData.datasets && this.pieChartData.datasets.length > 0) {
      const bgColors = this.pieChartData.datasets[0].backgroundColor as string[];
      bgColors[this.clickedPieIndex] = newColor;
      
      this.pieChartData = {
        labels: this.pieChartData.labels,
        datasets: [{
          ...this.pieChartData.datasets[0],
          backgroundColor: [...bgColors]
        }]
      };
      this.cdr.detectChanges();
    }
    this.clickedPieIndex = null;
  }
  onChartClickBar({ event, active }: { event?: any, active?: any[] }) {
    if (active && active.length > 0) {
      this.clickedBarIndex = active[0].index;
      if (this.colorPickerBar) {
        this.colorPickerBar.nativeElement.click();
      }
    }
  }

  onColorChangeBar(event: any) {
    const newColor = event.target.value;
    if (this.clickedBarIndex !== null && this.barChartData.datasets && this.barChartData.datasets.length > 0) {
      const bgColors = this.barChartData.datasets[0].backgroundColor as string[];
      bgColors[this.clickedBarIndex] = newColor;
      
      this.barChartData = {
        labels: this.barChartData.labels,
        datasets: [{
          ...this.barChartData.datasets[0],
          backgroundColor: [...bgColors]
        }]
      };
      this.cdr.detectChanges();
    }
    this.clickedBarIndex = null;
  }
}

