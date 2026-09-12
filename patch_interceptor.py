path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\data\interceptors\jwt.interceptor.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_content = """import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('jwt_token') : null;
  const router = inject(Router);

  let clonedRequest = req;
  if (token) {
    clonedRequest = req.clone({
      setHeaders: {
        Authorization: 'Bearer ' + token
      }
    });
  }

  return next(clonedRequest).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token expirado o inválido
        if (typeof localStorage !== 'undefined') {
          localStorage.removeItem('jwt_token');
          localStorage.removeItem('user_data');
        }
        router.navigate(['/login']);
      }
      return throwError(() => error);
    })
  );
};
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)
print("Interceptor actualizado para manejar 401 y redirigir al login.")
