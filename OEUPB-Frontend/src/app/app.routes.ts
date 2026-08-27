import { TendenciasComponent } from './presentation/features/data-admin/tendencias/tendencias';
import { ReporteGeneralComponent } from './presentation/features/data-admin/reporte-general/reporte-general';
import { Routes } from '@angular/router';

export const routes: Routes = [
  { 
    path: 'admin-usuarios', 
    loadComponent: () => import('./presentation/features/admin/admin-usuarios/admin-usuarios').then(m => m.AdminUsuariosComponent)
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./presentation/features/auth/login/login').then(m => m.LoginComponent)
  },
  { 
    path: 'reporte', 
    loadComponent: () => import('./presentation/features/dashboard/reporte-general/reporte-general').then(m => m.ReporteGeneralComponent)
  },
  { 
    path: 'tendencias', 
    loadComponent: () => import('./presentation/features/dashboard/tendencias/tendencias').then(m => m.Tendencias)
  },
  { 
    path: 'carga', 
    loadComponent: () => import('./presentation/features/data-admin/carga-datos/carga-datos').then(m => m.CargaDatosComponent)
  },
  { 
    path: 'perfil/:cedula', 
    loadComponent: () => import('./presentation/features/profile/ficha-egresado/ficha-egresado').then(m => m.FichaEgresado)
  },
  { path: '**', redirectTo: 'login' }
];






