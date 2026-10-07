import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';
import { UsuarioResponse } from '../../../../data/api/generated-api.models';
import { AdminUsuariosComponent } from './admin-usuarios';

const API = 'http://localhost:8000/api';
const profe: UsuarioResponse = {
  id: 7, nombre: 'Profe', correo: 'profe@upb.edu.co', rol: 'Usuario_Consulta', sede_id: 1,
  debe_cambiar_contrasena: false, activo: true, version_autorizacion: 1, etiqueta: 'Profesor',
  permisos: ['ver_publicaciones'], programas: ['Derecho', 'Programa Retirado'], programas_sin_datos: ['Programa Retirado'],
};

describe('AdminUsuariosComponent', () => {
  it('conserva y señala los programas asignados sin datos actuales (PRG-01)', async () => {
    TestBed.configureTestingModule({
      imports: [AdminUsuariosComponent],
      providers: [
        provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
        { provide: AuthImplementationRepository, useValue: { getUsuarioActual: () => ({ rol: 'Coordinador_Sede', sedeId: 1 }) } },
      ]
    });
    const fixture = TestBed.createComponent(AdminUsuariosComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/sedes/`).flush([{ id: 1, codigo: 'BUC', nombre: 'Bucaramanga' }]);
    http.expectOne(`${API}/usuarios/programas-asignables`).flush(['Derecho']);
    http.expectOne(r => r.url === `${API}/usuarios/`).flush([profe]);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Sin datos actuales: Programa Retirado');

    const componente = fixture.componentInstance;
    componente.editarUsuario(profe);
    fixture.detectChanges();
    const opciones = Array.from(fixture.nativeElement.querySelectorAll('select[formcontrolname=programas] option')).map(o => (o as HTMLOptionElement).textContent?.trim());
    expect(opciones).toEqual(['Derecho', 'Programa Retirado (sin datos actuales)']);
    expect(componente.userForm.value.programas).toEqual(['Derecho', 'Programa Retirado']);

    componente.userForm.patchValue({ numero_documento: 'ce-00123 4' });
    expect(componente.userForm.get('numero_documento')?.valid).toBe(true);
    componente.cancelarEdicion();
    expect(componente.programasSinDatos).toEqual([]);
    http.verify();
  });

  it('filtra por búsqueda (nombre, correo, id) insensible a mayúsculas y tildes, y permite limpiar', async () => {
    TestBed.configureTestingModule({
      imports: [AdminUsuariosComponent],
      providers: [
        provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
        { provide: AuthImplementationRepository, useValue: { getUsuarioActual: () => ({ rol: 'Coordinador_Sede', sedeId: 1 }) } },
      ]
    });
    const fixture = TestBed.createComponent(AdminUsuariosComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/sedes/`).flush([{ id: 1, codigo: 'BUC', nombre: 'Bucaramanga' }]);
    http.expectOne(`${API}/usuarios/programas-asignables`).flush(['Derecho']);
    const usuario2: UsuarioResponse = {
      id: 99, nombre: 'Álvaro Gómez', correo: 'alvaro.gomez@upb.edu.co', rol: 'Usuario_Consulta', sede_id: 1,
      debe_cambiar_contrasena: false, activo: false, version_autorizacion: 1, etiqueta: 'Administrativo',
      permisos: [], programas: [], programas_sin_datos: []
    };
    http.expectOne(r => r.url === `${API}/usuarios/`).flush([profe, usuario2]);
    await fixture.whenStable();

    const comp = fixture.componentInstance;
    expect(comp.usuariosFiltrados.length).toBe(2);

    // Búsqueda con tildes / mayúsculas
    comp.terminoBusqueda = 'alvaro';
    comp.onBusquedaChange();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(1);
    expect(comp.usuariosFiltrados[0].nombre).toBe('Álvaro Gómez');

    // Búsqueda por correo
    comp.terminoBusqueda = 'profe@upb';
    comp.onBusquedaChange();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(1);
    expect(comp.usuariosFiltrados[0].id).toBe(7);

    // Búsqueda por id numérico
    comp.terminoBusqueda = '99';
    comp.onBusquedaChange();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(1);
    expect(comp.usuariosFiltrados[0].id).toBe(99);

    // Limpiar búsqueda
    comp.limpiarBusqueda();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(2);
    http.verify();
  });

  it('filtra por estado, sede y alcance combinados, mostrando mensaje vacío cuando no hay coincidencias', async () => {
    TestBed.configureTestingModule({
      imports: [AdminUsuariosComponent],
      providers: [
        provideHttpClient(), provideHttpClientTesting(), provideRouter([]),
        { provide: AuthImplementationRepository, useValue: { getUsuarioActual: () => ({ rol: 'Coordinador_Sede', sedeId: 1 }) } },
      ]
    });
    const fixture = TestBed.createComponent(AdminUsuariosComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/sedes/`).flush([{ id: 1, codigo: 'BUC', nombre: 'Bucaramanga' }]);
    http.expectOne(`${API}/usuarios/programas-asignables`).flush(['Derecho']);
    const usuario2: UsuarioResponse = {
      id: 99, nombre: 'Álvaro Gómez', correo: 'alvaro.gomez@upb.edu.co', rol: 'Usuario_Consulta', sede_id: 1,
      debe_cambiar_contrasena: false, activo: false, version_autorizacion: 1, etiqueta: 'Administrativo',
      permisos: [], programas: [], programas_sin_datos: []
    };
    http.expectOne(r => r.url === `${API}/usuarios/`).flush([profe, usuario2]);
    await fixture.whenStable();

    const comp = fixture.componentInstance;

    // Verificar que los filtros de Sede y Alcance están en el DOM
    const selectSede = fixture.nativeElement.querySelector('#filter-sede');
    const selectAlcance = fixture.nativeElement.querySelector('#filter-alcance');
    expect(selectSede).toBeTruthy();
    expect(selectAlcance).toBeTruthy();

    // Filtro por estado activo
    comp.filtroEstado = 'activo';
    comp.aplicarFiltros();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(1);
    expect(comp.usuariosFiltrados[0].id).toBe(7);

    // Filtro por alcance Administrativo mientras estado es activo -> 0 coincidencias
    comp.filtroAlcance = 'Administrativo';
    comp.aplicarFiltros();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(0);
    expect(fixture.nativeElement.textContent).toContain('No se encontraron usuarios con estos criterios');

    // Acción restablecer búsqueda y filtros
    const btnReset = fixture.nativeElement.querySelector('.btn-reset-filters');
    expect(btnReset).toBeTruthy();
    btnReset.click();
    fixture.detectChanges();
    expect(comp.usuariosFiltrados.length).toBe(2);
    expect(comp.hayFiltrosActivos).toBe(false);
    http.verify();
  });
});
