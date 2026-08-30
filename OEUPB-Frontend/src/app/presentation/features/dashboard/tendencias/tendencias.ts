import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-tendencias',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective],
  templateUrl: './tendencias.html',
  styleUrls: ['./tendencias.scss']
})
export class TendenciasComponent implements OnInit {
  isChartReady = false;
  chartType: ChartType = 'line';
  currentIndicator = 'empleabilidad';
  currentIndicatorName = 'Tasa de Empleabilidad';

  public lineChartOptions: ChartConfiguration['options'] = { 
    responsive: true, 
    maintainAspectRatio: false,
    elements: {
      line: { tension: 0.4, borderWidth: 3 },
      point: { radius: 5, hitRadius: 10, hoverRadius: 7 }
    }
  };
  
  public lineChartData: ChartData<ChartType, (number|null)[], string> = { labels: [], datasets: [] };

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.isChartReady = false;
    this.cdr.detectChanges();

    this.http.get<any>('http://localhost:8000/api/reportes/tendencias').subscribe({
      next: (data) => {
        const colors = ['#ba0c2f', '#212529', '#6c757d', '#f4a261', '#2a9d8f'];
        
        // Asignar colores a los datasets
        data.datasets.forEach((ds: any, i: number) => {
          ds.borderColor = colors[i % colors.length];
          ds.backgroundColor = colors[i % colors.length] + '33'; // Transparente
          ds.fill = false;
        });

        this.lineChartData = {
          labels: data.labels,
          datasets: data.datasets
        };

        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error("Error cargando tendencias", err);
      }
    });
  }

  changeIndicator(event: any) {
    this.currentIndicator = event.target.value;
    const select = event.target;
    this.currentIndicatorName = select.options[select.selectedIndex].text;
    
    // Aquí en el futuro se enviaría el indicador como parámetro al backend:
    // this.http.get('.../tendencias?indicador=' + this.currentIndicator)
    // Por ahora recarga la misma data de empleabilidad real.
    this.loadData();
  }

  changeChartType(event: any) {
    this.chartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }
}
