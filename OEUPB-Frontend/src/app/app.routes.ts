import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./features/auth/login/login').then(m => m.Login)
  },
  { 
    path: 'reporte', 
    loadComponent: () => import('./features/dashboard/reporte-general/reporte-general').then(m => m.ReporteGeneral)
  },
  { 
    path: 'tendencias', 
    loadComponent: () => import('./features/dashboard/tendencias/tendencias').then(m => m.Tendencias)
  },
  { 
    path: 'carga', 
    loadComponent: () => import('./features/data-admin/carga-datos/carga-datos').then(m => m.CargaDatos)
  },
  { 
    path: 'perfil/:cedula', 
    loadComponent: () => import('./features/profile/ficha-egresado/ficha-egresado').then(m => m.FichaEgresado)
  },
  { path: '**', redirectTo: 'login' }
];
