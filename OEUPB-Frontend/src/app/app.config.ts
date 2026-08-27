import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { AuthRepository } from './domain/repositories/auth.repository';
import { AuthImplementationRepository } from './data/repositories/auth-implementation.repository';
import { jwtInterceptor } from './data/interceptors/jwt.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([jwtInterceptor])),
    {
      provide: AuthRepository,
      useClass: AuthImplementationRepository
    }
  ]
};
