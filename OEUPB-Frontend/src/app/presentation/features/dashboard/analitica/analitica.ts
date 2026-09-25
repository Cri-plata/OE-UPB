import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AnaliticaApi, AnaliticaResumen } from '../../../../data/api/analitica.api';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';

@Component({ selector: 'app-analitica', standalone: true, imports: [CommonModule, SidebarComponent], templateUrl: './analitica.html', styleUrls: ['./analitica.scss'] })
export class AnaliticaComponent implements OnInit {
  resumen: AnaliticaResumen | null = null;
  error = '';
  constructor(private api: AnaliticaApi) {}
  ngOnInit() { this.api.resumen().subscribe({ next: data => this.resumen = data, error: () => this.error = 'No fue posible cargar la analítica.' }); }
}
