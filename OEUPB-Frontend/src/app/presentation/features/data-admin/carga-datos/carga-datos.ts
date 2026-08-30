import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
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
export class CargaDatosComponent implements OnInit {
  historial: any[] = [];
  uploadForm: FormGroup;
  selectedFile: File | null = null;
  erroresTabla: any[] = [];
  mensajeValidacion: string | null = null;
  isSubmitting = false;
  aniosDisponibles: number[] = [];
  mostrarInputAnioManual = false;
  
  private readonly API_URL = 'http://localhost:8000/api/carga/excel';

  constructor(private fb: FormBuilder, private http: HttpClient, private cdr: ChangeDetectorRef) {
    this.uploadForm = this.fb.group({
      momento: ['', Validators.required],
      anio: ['', Validators.required]
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
    formData.append('anio', this.uploadForm.get('anio')?.value);
      

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
  ngOnInit() {
    this.cargarHistorial();
    this.generarAnios();
  }

  cargarHistorial() {
    this.http.get<any[]>('http://localhost:8000/api/carga/historial').subscribe({
      next: (data) => {
        this.historial = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error("Error cargando historial", err)
    });
  }

  eliminarMomento(momento: number, anio: number) {
    if(confirm(`¿Estás seguro de que deseas eliminar permanentemente todos los datos y encuestas del Momento ${momento} del ${anio}?`)) {
      this.http.delete(`http://localhost:8000/api/carga/momento/${momento}/${anio}`).subscribe({
        next: () => {
          alert(`Momento ${momento} del ${anio} eliminado exitosamente.`);
          this.cargarHistorial();
    this.generarAnios();
        },
        error: (err) => alert("Error eliminando el archivo.")
      });
    }
  }
  generarAnios() {
    const currentYear = new Date().getFullYear();
    // Generar desde hace 5 años hasta el próximo año
    for (let i = currentYear - 5; i <= currentYear; i++) {
      this.aniosDisponibles.push(i);
    }
  }

  onAnioChange(event: any) {
    if (event.target.value === 'otro') {
      this.mostrarInputAnioManual = true;
      this.uploadForm.get('anio')?.setValue('');
    }
  }
}


