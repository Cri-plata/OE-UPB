import { HttpInterceptorFn } from '@angular/common/http';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('jwt_token') : null;

  if (token) {
    const clonedRequest = req.clone({
      setHeaders: {
        Authorization: 'Bearer ' + token
      }
    });
    return next(clonedRequest);
  }

  return next(req);
};

