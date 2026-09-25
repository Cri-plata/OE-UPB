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
    http.expectOne(r => r.url === `${API}/usuarios`).flush([profe]);
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
});
