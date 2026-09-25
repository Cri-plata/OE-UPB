import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router } from '@angular/router';

type Rol = 'Admin_CTIC' | 'Coordinador_Sede' | 'Usuario_Consulta';

interface SesionLocal {
  rol?: Rol;
  debeCambiarContrasena?: boolean;
}

function leerSesion(): { token: string; usuario: SesionLocal } | null {
  if (typeof localStorage === 'undefined') return null;
  const token = localStorage.getItem('jwt_token');
  const raw = localStorage.getItem('user_data');
  if (!token || !raw) return null;
  try {
    return { token, usuario: JSON.parse(raw) as SesionLocal };
  } catch {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_data');
    return null;
  }
}

function inicioPorRol(rol?: Rol): string {
  if (rol === 'Admin_CTIC') return '/admin-usuarios';
  if (rol === 'Usuario_Consulta') return '/publicaciones';
  return '/reporte';
}

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);
  const sesion = leerSesion();
  if (!sesion || sesion.usuario.debeCambiarContrasena) return router.parseUrl('/login');
  return true;
};

export const rolesGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const router = inject(Router);
  const sesion = leerSesion();
  if (!sesion || sesion.usuario.debeCambiarContrasena) return router.parseUrl('/login');
  const roles = (route.data['roles'] || []) as Rol[];
  return roles.includes(sesion.usuario.rol as Rol)
    ? true
    : router.parseUrl(inicioPorRol(sesion.usuario.rol));
};

export const guestGuard: CanActivateFn = () => {
  const router = inject(Router);
  const sesion = leerSesion();
  if (!sesion || sesion.usuario.debeCambiarContrasena) return true;
  return router.parseUrl(inicioPorRol(sesion.usuario.rol));
};
