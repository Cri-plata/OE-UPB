import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { UploadExcelResponseDto, FilaErrorDto } from '../../../../../../../OEUPB-Contracts/APIcontractfront/carga.contract';

@Component({
  selector: 'app-carga-datos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './carga-datos.html',
  styleUrls: ['./carga-datos.scss']
})
export class CargaDatosComponent {
  cargaForm: FormGroup;
  selectedFile: File | null = null;
  isDragging = false;
  isUploading = false;
  uploadResult: UploadExcelResponseDto | null = null;

  constructor(private fb: FormBuilder) {
    this.cargaForm = this.fb.group({
      momento: ['', Validators.required],
      sede: ['', Validators.required]
    });
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.handleFile(event.dataTransfer.files[0]);
    }
  }

  onFileSelected(event: any) {
    if (event.target.files && event.target.files.length > 0) {
      this.handleFile(event.target.files[0]);
    }
  }

  private handleFile(file: File) {
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      this.selectedFile = file;
      this.uploadResult = null; // reset previous results
    } else {
      alert('Solo se permiten archivos Excel (.xlsx, .xls)');
    }
  }

  removeFile() {
    this.selectedFile = null;
    this.uploadResult = null;
  }

  onSubmit() {
    if (this.cargaForm.invalid || !this.selectedFile) {
      this.cargaForm.markAllAsTouched();
      return;
    }

    this.isUploading = true;

    // MOCK: Simulando carga al backend
    setTimeout(() => {
      this.isUploading = false;
      this.uploadResult = {
        filasCargadas: 206,
        filasConError: 2,
        detallesErrores: [
          { fila: 15, cedula: '1098765432', motivo: 'Cédula duplicada' },
          { fila: 84, cedula: '1090123456', motivo: 'Doble titulación detectada' }
        ]
      };
      this.selectedFile = null;
      this.cargaForm.reset();
    }, 2000);
  }
}

