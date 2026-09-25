import { of } from 'rxjs';
import { LoginUseCase } from './login.usecase';
import { AuthRepository } from '../repositories/auth.repository';

describe('LoginUseCase', () => {
  const usuario = { id: 1, nombre: 'Ana', correo: 'ana@upb.edu.co', rol: 'Coordinador_Sede' as const, sedeId: 1, debeCambiarContrasena: false };
  const repo = {
    login: vi.fn(() => of({ token: 'token', usuario })),
    cambiarContrasenaTemporal: vi.fn(() => of({ token: 'nuevo', usuario })),
    logout: vi.fn(), getUsuarioActual: vi.fn()
  } as unknown as AuthRepository;

  it('rechaza correo no institucional', () => {
    expect(() => new LoginUseCase(repo).execute('ana@gmail.com', '123456')).toThrowError(/institucionales/);
  });

  it('delega credenciales válidas al repositorio', () => {
    new LoginUseCase(repo).execute('ana@upb.edu.co', '123456').subscribe();
    expect(repo.login).toHaveBeenCalledWith('ana@upb.edu.co', '123456');
  });

  it('valida el cambio de contraseña temporal', () => {
    expect(() => new LoginUseCase(repo).cambiarContrasenaTemporal('Clave2026A', 'otra')).toThrowError(/coinciden/);
  });
});
