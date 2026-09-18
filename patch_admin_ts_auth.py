path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "AuthImplementationRepository" not in content:
    content = "import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';\n" + content

# Inject AuthImplementationRepository if not already present
if "private authRepo =" not in content:
    content = content.replace(
        "constructor(private fb: FormBuilder, private http: HttpClient, private cdr: ChangeDetectorRef) {",
        "private authRepo = inject(AuthImplementationRepository);\n  usuarioActual: any = null;\n\n  constructor(private fb: FormBuilder, private http: HttpClient, private cdr: ChangeDetectorRef) {"
    )

    content = content.replace(
        "ngOnInit() {",
        "ngOnInit() {\n    this.usuarioActual = this.authRepo.getUsuarioActual();"
    )

# Also import inject
if "import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';" not in content:
    content = content.replace("import { Component, OnInit, ChangeDetectorRef } from '@angular/core';", "import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("TS configurado con rol actual.")
