path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\dashboard\explorador\explorador.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import { NgChartsModule } from 'ng2-charts';", "import { BaseChartDirective } from 'ng2-charts';")
content = content.replace("imports: [CommonModule, FormsModule, SidebarComponent, NgChartsModule],", "imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Corregida la importación de ng2-charts en explorador.ts.")
