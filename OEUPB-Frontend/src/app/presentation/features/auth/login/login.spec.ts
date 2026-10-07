import { TestBed, ComponentFixture } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { LoginComponent } from './login';
import { LoginUseCase } from '../../../../domain/usecases/login.usecase';

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let component: LoginComponent;
  let mockLoginUseCase: {
    execute: ReturnType<typeof vi.fn>;
    cambiarContrasenaTemporal: ReturnType<typeof vi.fn>;
  };
  let router: Router;

  beforeEach(async () => {
    mockLoginUseCase = {
      execute: vi.fn(),
      cambiarContrasenaTemporal: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideRouter([]),
        { provide: LoginUseCase, useValue: mockLoginUseCase },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('debe crearse y renderizar la jerarquía institucional depurada', () => {
    expect(component).toBeTruthy();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('.login-institution-name')?.textContent?.trim())
      .toBe('Universidad Pontificia Bolivariana');
    expect(compiled.querySelector('.login-brand-title')?.textContent?.trim())
      .toBe('Observatorio de Egresados');
    expect(compiled.querySelector('.login-brand-acronym')?.textContent?.trim())
      .toBe('OEUPB');
    expect(compiled.querySelector('.login-brand-body')?.textContent)
      .toContain('Información para comprender las trayectorias de nuestros egresados y fortalecer la calidad académica');
    expect(compiled.querySelector('.login-brand-footer')?.textContent)
      .toContain('Acceso reservado a usuarios autorizados');
    expect(compiled.querySelector('.login-form-header h2')?.textContent?.trim())
      .toBe('Acceso institucional');

    // Validación de elementos obsoletos eliminados
    expect(compiled.querySelector('.login-institution-badge')).toBeNull();
    expect(compiled.querySelector('.login-milestones')).toBeNull();
  });

  it('debe alternar la visibilidad de la contraseña y sus atributos accesibles', () => {
    const passwordInput = fixture.nativeElement.querySelector('#contrasena') as HTMLInputElement;
    const toggleBtn = fixture.nativeElement.querySelector('.btn-toggle-password') as HTMLButtonElement;

    // Estado inicial oculto
    expect(passwordInput.type).toBe('password');
    expect(toggleBtn.getAttribute('aria-label')).toBe('Mostrar contraseña');
    expect(toggleBtn.getAttribute('aria-pressed')).toBe('false');

    // Clic para mostrar
    toggleBtn.click();
    fixture.detectChanges();

    expect(component.mostrarContrasena).toBe(true);
    expect(passwordInput.type).toBe('text');
    expect(toggleBtn.getAttribute('aria-label')).toBe('Ocultar contraseña');
    expect(toggleBtn.getAttribute('aria-pressed')).toBe('true');

    // Clic para volver a ocultar
    toggleBtn.click();
    fixture.detectChanges();

    expect(component.mostrarContrasena).toBe(false);
    expect(passwordInput.type).toBe('password');
    expect(toggleBtn.getAttribute('aria-label')).toBe('Mostrar contraseña');
    expect(toggleBtn.getAttribute('aria-pressed')).toBe('false');
  });

  it('debe mostrar errores de validación si el formulario está vacío', () => {
    component.onSubmit();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(component.loginForm.invalid).toBe(true);
    expect(compiled.textContent).toContain('El correo es obligatorio.');
    expect(compiled.textContent).toContain('La contraseña es obligatoria.');
    expect(mockLoginUseCase.execute).not.toHaveBeenCalled();
  });

  it('debe mostrar error si el formato del correo no es válido', () => {
    const correoInput = fixture.nativeElement.querySelector('#correo') as HTMLInputElement;
    correoInput.value = 'correo-invalido';
    correoInput.dispatchEvent(new Event('input'));
    correoInput.dispatchEvent(new Event('blur'));
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Debe ser un correo válido.');
  });

  it('debe evitar envíos concurrentes cuando isLoading es true', () => {
    component.loginForm.setValue({
      correo: 'coordinador@upb.edu.co',
      contrasena: 'ClaveSegura123',
    });
    component.isLoading = true;

    component.onSubmit();

    expect(mockLoginUseCase.execute).not.toHaveBeenCalled();
  });

  it('debe enviar credenciales válidas y redirigir según el rol del usuario', () => {
    const navigateSpy = vi.spyOn(router, 'navigate');
    mockLoginUseCase.execute.mockReturnValue(of({
      token: 'jwt-token',
      usuario: {
        id: 1,
        nombre: 'Coordinador BUC',
        correo: 'coordinador@upb.edu.co',
        rol: 'Coordinador_Sede',
        sedeId: 1,
        debeCambiarContrasena: false,
      },
    }));

    component.loginForm.setValue({
      correo: 'coordinador@upb.edu.co',
      contrasena: 'ClaveSegura123',
    });

    component.onSubmit();
    fixture.detectChanges();

    expect(mockLoginUseCase.execute).toHaveBeenCalledWith('coordinador@upb.edu.co', 'ClaveSegura123');
    expect(navigateSpy).toHaveBeenCalledWith(['/reporte']);
  });

  it('redirige al usuario de consulta a las gráficas publicadas', () => {
    const navigateSpy = vi.spyOn(router, 'navigate');
    mockLoginUseCase.execute.mockReturnValue(of({
      token: 'jwt-consulta',
      usuario: {
        id: 3,
        nombre: 'Usuario Consulta',
        correo: 'consulta@upb.edu.co',
        rol: 'Usuario_Consulta',
        sedeId: 1,
        debeCambiarContrasena: false,
      },
    }));

    component.loginForm.setValue({ correo: 'consulta@upb.edu.co', contrasena: 'ClaveSegura123' });
    component.onSubmit();

    expect(navigateSpy).toHaveBeenCalledWith(['/publicaciones']);
  });

  it('debe activar el modal de cambio obligatorio si debeCambiarContrasena es true', () => {
    mockLoginUseCase.execute.mockReturnValue(of({
      token: 'jwt-temp',
      usuario: {
        id: 2,
        nombre: 'Nuevo Usuario',
        correo: 'nuevo@upb.edu.co',
        rol: 'Usuario_Consulta',
        sedeId: 1,
        debeCambiarContrasena: true,
      },
    }));

    component.loginForm.setValue({
      correo: 'nuevo@upb.edu.co',
      contrasena: 'ClaveTemporal1',
    });

    component.onSubmit();
    fixture.detectChanges();

    expect(component.mostrarCambioObligatorio).toBe(true);
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.password-modal')).toBeTruthy();
  });

  it('debe mostrar mensaje de error si la autenticación falla', () => {
    mockLoginUseCase.execute.mockReturnValue(throwError(() => ({
      error: { detail: 'Credenciales inválidas' }
    })));

    component.loginForm.setValue({
      correo: 'fallo@upb.edu.co',
      contrasena: 'ClaveErronea',
    });

    component.onSubmit();
    fixture.detectChanges();

    expect(component.errorMessage).toBe('Correo o contraseña no válido. Intente de nuevo.');
    expect(fixture.nativeElement.textContent).toContain('Correo o contraseña no válido. Intente de nuevo.');
  });
});
