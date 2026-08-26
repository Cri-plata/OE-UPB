import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class Login {
  private router = inject(Router);

  onLogin() {
    // Por ahora, simulamos un login exitoso y navegamos al dashboard
    console.log('Iniciando sesión...');
    this.router.navigate(['/reporte']);
  }
}
