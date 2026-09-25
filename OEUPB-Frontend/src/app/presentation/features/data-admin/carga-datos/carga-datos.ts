import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { CargaApi } from '../../../../data/api/carga.api';
import { HistorialCargaItem } from '../../../../data/api/generated-api.models';

@Component({
  selector: 'app-carga-datos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './carga-datos.html',
  styleUrls: ['./carga-datos.scss']
})
export class CargaDatosComponent implements OnInit {
  historial: HistorialCargaItem[] = [];
  uploadForm: FormGroup;
  selectedFile: File | null = null;
  erroresTabla: any[] = [];
  mensajeValidacion: string | null = null;
  isSubmitting = false;
  aniosDisponibles: number[] = [];
  mostrarInputAnioManual = false;
  
  constructor(private fb: FormBuilder, private cargaApi: CargaApi, private cdr: ChangeDetectorRef) {
    this.uploadForm = this.fb.group({
      momento: ['', Validators.required],
      anio: ['', Validators.required]
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.name.toLowerCase().endsWith('.xlsx')) {
      this.selectedFile = file;
    } else {
      alert('Por favor, selecciona un archivo Excel válido (.xlsx)');
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
      

      this.cargaApi.cargar(formData).subscribe({
        next: (response) => {
          this.isSubmitting = false;
          this.mensajeValidacion = response.mensaje;
          this.erroresTabla = response.errores || [];
          this.cargarHistorial(); // Actualizar tabla automáticamente
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
    this.cargaApi.historial().subscribe({
      next: (data) => {
        this.historial = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error("Error cargando historial", err)
    });
  }

  eliminarCarga(carga: HistorialCargaItem) {
    if(confirm(`¿Deseas retirar la carga ${carga.nombre_archivo} (versión ${carga.version})?`)) {
      const motivo = prompt('Indica el motivo de la eliminación (mínimo 10 caracteres):');
      if (!motivo || motivo.trim().length < 10) {
        alert('Debes registrar un motivo de al menos 10 caracteres.');
        return;
      }
      this.cargaApi.eliminar(carga.id, motivo.trim()).subscribe({
        next: () => {
          alert(`Carga ${carga.nombre_archivo} eliminada exitosamente.`);
          this.cargarHistorial();
        },
        error: () => alert("Error eliminando la carga.")
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



