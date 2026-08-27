import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ChartConfiguration, ChartData } from 'chart.js';
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

  public lineChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public lineChartData: ChartData<'line', number[], string | string[]> = { labels: [], datasets: [] };

  constructor(private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    setTimeout(() => {
      this.lineChartData = {
        labels: ['Momento 0 (Grado)', 'Momento 1 (1 año)', 'Momento 5 (5 años)'],
        datasets: [
          { data: [45, 82, 91], label: 'Ingeniería', borderColor: '#ba0c2f', tension: 0.4, fill: false },
          { data: [60, 75, 88], label: 'Derecho', borderColor: '#212529', tension: 0.4, fill: false }
        ]
      };
      this.isChartReady = true;
      this.cdr.detectChanges();
    }, 500);
  }
}
