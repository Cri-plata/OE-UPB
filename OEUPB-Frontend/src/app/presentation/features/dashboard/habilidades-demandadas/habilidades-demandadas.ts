import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { IaApi } from '../../../../data/api/ia.api';
import { DirectorioApi } from '../../../../data/api/directorio.api';

export interface HabilidadItem {
  habilidad: string;
  tipo: 'blanda' | 'dura' | string;
  menciones: number;
}

export interface CandidataEmergente {
  termino: string;
  score_tfidf: number;
  frecuencia_documentos: number;
}

export interface ReglaItem {
  si_menciona: string;
  tambien_menciona: string;
  ocurrencias: number;
  soporte: number;
  confianza: number;
  lift: number;
}

export interface EstadisticasIA {
  total_respuestas_analizadas: number;
  respuestas_con_habilidad: number;
  respuestas_sin_habilidad: number;
}

@Component({
  selector: 'app-habilidades-demandadas',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],
  templateUrl: './habilidades-demandadas.html',
  styleUrls: ['./habilidades-demandadas.scss']
})
export class HabilidadesDemandadasComponent implements OnInit {
  activeTab: 'reglas' | 'habilidades' = 'reglas';
  isLoading = false;
  errorMensaje = '';

  // Filtros interactivos
  filtroMomento: string = '';
  filtroAnio: string = '';
  filtroPrograma: string = '';
  filtroMinOcurrencias: number = 2;
  filtroMinConfianza: number = 0.5;
  topReglas: number = 20;

  aniosDisponibles: number[] = [2026, 2025, 2024, 2023, 2022];
  programasDisponibles: string[] = [];

  // Datos obtenidos
  estadisticas: EstadisticasIA | null = null;
  habilidadesReconocidas: HabilidadItem[] = [];
  candidatasEmergentes: CandidataEmergente[] = [];
  reglasAsociacion: ReglaItem[] = [];

  totalRespuestasReglas = 0;
  transaccionesValidas = 0;
  transaccionesInsuficientes = 0;
  totalReglas = 0;

  // Gráficos de barras (ng2-charts)
  public barChartType: ChartType = 'bar';
  public isChartReady = false;

  public blandasChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` ${context.raw} menciones`
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { stepSize: 1 }
      }
    }
  };

  public durasChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` ${context.raw} menciones`
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { stepSize: 1 }
      }
    }
  };

  public blandasChartData: ChartData<'bar', number[], string> = { labels: [], datasets: [] };
  public durasChartData: ChartData<'bar', number[], string> = { labels: [], datasets: [] };

  constructor(
    private iaApi: IaApi,
    private directorioApi: DirectorioApi,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarProgramas();
    this.cargarDatosCompletos();
  }

  cargarProgramas() {
    this.directorioApi.programas().subscribe({
      next: (data) => {
        this.programasDisponibles = data || [];
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error cargando programas académicos:', err)
    });
  }

  setTab(tab: 'reglas' | 'habilidades') {
    this.activeTab = tab;
  }

  aplicarFiltros() {
    this.cargarDatosCompletos();
  }

  cargarDatosCompletos() {
    this.isLoading = true;
    this.errorMensaje = '';

    const filtrosHabs = {
      momento: this.filtroMomento,
      anio: this.filtroAnio,
      programa: this.filtroPrograma,
      top_emergentes: 15,
    };

    const filtrosReglas = {
      momento: this.filtroMomento,
      anio: this.filtroAnio,
      programa: this.filtroPrograma,
      min_soporte: 0.01,
      min_confianza: this.filtroMinConfianza,
      min_ocurrencias: this.filtroMinOcurrencias,
      top_reglas: this.topReglas,
    };

    // Cargar habilidades y reglas en paralelo
    this.iaApi.habilidadesDemandadas(filtrosHabs).subscribe({
      next: (data) => {
        this.estadisticas = data.estadisticas;
        this.habilidadesReconocidas = data.habilidades_reconocidas || [];
        this.candidatasEmergentes = data.candidatas_emergentes || [];
        this.procesarGraficosHabilidades();
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando habilidades demandadas:', err);
        this.errorMensaje = 'No se pudo conectar con el servicio de IA o no hay encuestas cargadas.';
      }
    });

    this.iaApi.reglasAsociacion(filtrosReglas).subscribe({
      next: (data) => {
        this.totalRespuestasReglas = data.total_respuestas || 0;
        this.transaccionesValidas = data.transacciones_validas || 0;
        this.transaccionesInsuficientes = data.transacciones_insuficientes || 0;
        this.totalReglas = data.total_reglas || 0;
        this.reglasAsociacion = (data.reglas as any[]) || [];
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando reglas de asociación:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  private procesarGraficosHabilidades() {
    const blandas = this.habilidadesReconocidas.filter(h => h.tipo === 'blanda').slice(0, 8);
    const duras = this.habilidadesReconocidas.filter(h => h.tipo === 'dura').slice(0, 8);

    this.blandasChartData = {
      labels: blandas.map(h => h.habilidad),
      datasets: [
        {
          data: blandas.map(h => h.menciones),
          backgroundColor: '#2a9d8f',
          hoverBackgroundColor: '#21867a',
          borderRadius: 6
        }
      ]
    };

    this.durasChartData = {
      labels: duras.map(h => h.habilidad),
      datasets: [
        {
          data: duras.map(h => h.menciones),
          backgroundColor: '#ba0c2f',
          hoverBackgroundColor: '#960a26',
          borderRadius: 6
        }
      ]
    };

    this.isChartReady = true;
  }

  getLiftBadge(lift: number): string {
    if (lift >= 5.0) return 'badge-alto';
    if (lift >= 2.0) return 'badge-medio';
    return 'badge-base';
  }

  getLiftTexto(lift: number): string {
    if (lift >= 5.0) return 'Muy Fuerte';
    if (lift >= 2.0) return 'Significativo';
    return 'Moderado';
  }

  getInsight(r: ReglaItem): string {
    const pct = Math.round(r.confianza * 100);
    return `En el ${pct}% de los casos donde una empresa exige "${r.si_menciona}", también demanda "${r.tambien_menciona}".`;
  }
}
