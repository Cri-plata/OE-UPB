import { Routes } from '@angular/router';
import { ExploradorComponent } from './presentation/features/dashboard/explorador/explorador';

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
    loadComponent: () => import('./presentation/features/dashboard/tendencias/tendencias').then(m => m.TendenciasComponent)
  },
  { path: 'explorador', component: ExploradorComponent },
  { 
    path: 'carga', 
    loadComponent: () => import('./presentation/features/data-admin/carga-datos/carga-datos').then(m => m.CargaDatosComponent)
  },
  { 
    path: 'perfil/:cedula', 
    loadComponent: () => import('./presentation/features/profile/ficha-egresado/ficha-egresado').then(m => m.FichaEgresado)
  },
  { 
    path: 'directorio', 
    loadComponent: () => import('./presentation/features/dashboard/directorio/directorio').then(m => m.DirectorioComponent)
  },
  { 
    path: 'mi-perfil', 
    loadComponent: () => import('./presentation/features/profile/perfil-usuario/perfil-usuario').then(m => m.PerfilUsuarioComponent)
  },
  { path: '**', redirectTo: 'login' }
];


