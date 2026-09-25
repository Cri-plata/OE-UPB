import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse, HttpRequest, HttpResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { jwtInterceptor } from './jwt.interceptor';

describe('jwtInterceptor', () => {
  const router = { navigate: vi.fn() };

  beforeEach(() => {
    localStorage.clear();
    router.navigate.mockClear();
    TestBed.configureTestingModule({ providers: [{ provide: Router, useValue: router }] });
  });

  it('agrega el token Bearer', () => {
    localStorage.setItem('jwt_token', 'abc');
    TestBed.runInInjectionContext(() => jwtInterceptor(
      new HttpRequest('GET', '/api'),
      req => {
        expect(req.headers.get('Authorization')).toBe('Bearer abc');
        return of(new HttpResponse({ status: 200 }));
      }
    ).subscribe());
  });

  it('limpia sesión y redirige ante 401', () => {
    localStorage.setItem('jwt_token', 'abc');
    localStorage.setItem('user_data', '{}');
    TestBed.runInInjectionContext(() => jwtInterceptor(
      new HttpRequest('GET', '/api'),
      () => throwError(() => new HttpErrorResponse({ status: 401 }))
    ).subscribe({ error: () => undefined }));
    expect(localStorage.getItem('jwt_token')).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
