import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-carga-datos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './carga-datos.html',
  styleUrls: ['./carga-datos.scss']
})
export class CargaDatosComponent {
  uploadForm: FormGroup;
  selectedFile: File | null = null;
  erroresTabla: any[] = [];
  mensajeValidacion: string | null = null;
  isSubmitting = false;
  
  private readonly API_URL = 'http://localhost:8000/api/carga/excel';

  constructor(private fb: FormBuilder, private http: HttpClient, private cdr: ChangeDetectorRef) {
    this.uploadForm = this.fb.group({
      momento: ['', Validators.required]
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
      this.selectedFile = file;
    } else {
      alert('Por favor, selecciona un archivo Excel válido (.xlsx o .xls)');
      this.selectedFile = null;
    }
  }

  onSubmit() {
    if (this.uploadForm.valid && this.selectedFile) {
      this.isSubmitting = true;
      this.mensajeValidacion = null;
      this.erroresTabla = [];

      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('momento', this.uploadForm.get('momento')?.value);
      

      this.http.post<any>(this.API_URL, formData).subscribe({
        next: (response) => {
          this.isSubmitting = false;
          this.mensajeValidacion = response.mensaje;
          this.erroresTabla = response.errores || [];
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.isSubmitting = false;
          let msg = 'Error del servidor al procesar el archivo.'; if (err.error && err.error.detail) { msg = typeof err.error.detail === 'string' ? err.error.detail : JSON.stringify(err.error.detail); } this.mensajeValidacion = msg;
          this.cdr.detectChanges();
        }
      });
    } else {
      alert('Faltan datos por seleccionar o no se ha adjuntado el archivo.');
    }
  }
}




