import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { CargaDatosComponent } from './carga-datos';

describe('CargaDatosComponent', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [CargaDatosComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
  }));

  it('consulta el historial autorizado al iniciar', () => {
    const fixture = TestBed.createComponent(CargaDatosComponent);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    const req = http.expectOne('http://localhost:8000/api/carga/historial');
    expect(req.request.method).toBe('GET');
    req.flush([]);
    http.verify();
  });

  it('acepta únicamente archivos xlsx', () => {
    const componente = TestBed.createComponent(CargaDatosComponent).componentInstance;
    vi.spyOn(window, 'alert').mockImplementation(() => undefined);
    componente.onFileSelected({ target: { files: [new File(['x'], 'datos.xls')] } });
    expect(componente.selectedFile).toBeNull();
    componente.onFileSelected({ target: { files: [new File(['x'], 'datos.xlsx')] } });
    expect(componente.selectedFile?.name).toBe('datos.xlsx');
  });
});
