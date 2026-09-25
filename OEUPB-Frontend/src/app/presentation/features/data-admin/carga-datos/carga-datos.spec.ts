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

  it('muestra el detalle por fila cuando el backend rechaza el archivo', () => {
    const fixture = TestBed.createComponent(CargaDatosComponent);
    const componente = fixture.componentInstance;
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('http://localhost:8000/api/carga/historial').flush([]);

    componente.uploadForm.setValue({ momento: '1', anio: '2024' });
    componente.selectedFile = new File(['x'], 'datos.xlsx');
    componente.onSubmit();
    http.expectOne('http://localhost:8000/api/carga/excel').flush(
      { detail: { mensaje: 'El archivo contiene 1 documentos inválidos; no se guardó ninguna fila', errores: [{ fila: 3, columna: 'NUMERO_DOCUMENTO', error: 'Documento inválido' }] } },
      { status: 422, statusText: 'Unprocessable Entity' }
    );

    expect(componente.isSubmitting).toBe(false);
    expect(componente.mensajeValidacion).toContain('documentos inválidos');
    expect(componente.erroresTabla).toEqual([{ fila: 3, columna: 'NUMERO_DOCUMENTO', error: 'Documento inválido' }]);
    http.verify();
  });
});
