import { Routes } from '@angular/router';
import { ExploradorComponent } from './presentation/features/dashboard/explorador/explorador';
import { authGuard, guestGuard, rolesGuard } from './presentation/guards/session.guard';

export const routes: Routes = [
  { 
    path: 'admin-usuarios', 
    canActivate: [rolesGuard], data: { roles: ['Admin_CTIC', 'Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/admin/admin-usuarios/admin-usuarios').then(m => m.AdminUsuariosComponent)
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { 
    path: 'login', 
    canActivate: [guestGuard],
    loadComponent: () => import('./presentation/features/auth/login/login').then(m => m.LoginComponent)
  },
  { 
    path: 'reporte', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/dashboard/reporte-general/reporte-general').then(m => m.ReporteGeneralComponent)
  },
  { 
    path: 'tendencias', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/dashboard/tendencias/tendencias').then(m => m.TendenciasComponent)
  },
  { path: 'explorador', component: ExploradorComponent, canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] } },
  { path: 'analitica', canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] }, loadComponent: () => import('./presentation/features/dashboard/analitica/analitica').then(m => m.AnaliticaComponent) },
  {
    path: 'publicaciones',
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede', 'Usuario_Consulta'] },
    loadComponent: () => import('./presentation/features/dashboard/publicaciones/publicaciones').then(m => m.PublicacionesComponent)
  },
  { 
    path: 'carga', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/data-admin/carga-datos/carga-datos').then(m => m.CargaDatosComponent)
  },
  { 
    path: 'perfil/:cedula', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/profile/ficha-egresado/ficha-egresado').then(m => m.FichaEgresado)
  },
  { 
    path: 'directorio', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/dashboard/directorio/directorio').then(m => m.DirectorioComponent)
  },
  { 
    path: 'habilidades', 
    canActivate: [rolesGuard], data: { roles: ['Coordinador_Sede'] },
    loadComponent: () => import('./presentation/features/dashboard/habilidades-demandadas/habilidades-demandadas').then(m => m.HabilidadesDemandadasComponent)
  },
  { 
    path: 'mi-perfil', 
    canActivate: [authGuard],
    loadComponent: () => import('./presentation/features/profile/perfil-usuario/perfil-usuario').then(m => m.PerfilUsuarioComponent)
  },
  { path: '**', redirectTo: 'login' }
];
