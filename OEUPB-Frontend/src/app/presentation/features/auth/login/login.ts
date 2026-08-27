import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginUseCase } from '../../../../domain/usecases/login.usecase';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string | null = null;
  isLoading = false;

  private fb = inject(FormBuilder);
  private loginUseCase = inject(LoginUseCase);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  constructor() {
    this.loginForm = this.fb.group({
      correo: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const { correo, contrasena } = this.loginForm.value;

    this.loginUseCase.execute(correo, contrasena).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        // Redirigir según el rol del usuario (CTIC a usuarios, el resto al dashboard)
        if (response.usuario.rol === 'Admin_CTIC') {
          this.router.navigate(['/admin-usuarios']); // Ruta futura
        } else {
          this.router.navigate(['/reporte']); // Ruta futura
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        // Extraer mensaje del error de dominio o del servidor HTTP
        this.errorMessage = 'Correo o contraseña no válido. Intente de nuevo.';
        this.cdr.detectChanges();
      }
    });
  }
}





