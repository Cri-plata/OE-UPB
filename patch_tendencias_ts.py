path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\dashboard\tendencias\tendencias.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure the frontend sends the query param
content = content.replace(
    "this.http.get<any>(this.API_URL)",
    "this.http.get<any>(`${this.API_URL}?indicador=${this.currentIndicator}`)"
)

# Update chart options for better styling
import re
new_options = """lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: { family: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size: 12 }
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        titleColor: '#000',
        bodyColor: '#333',
        borderColor: '#ddd',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6
      }
    },
    scales: {
      x: {
        grid: { display: false }
      },
      y: {
        beginAtZero: false,
        grid: { color: 'rgba(0, 0, 0, 0.05)' }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };"""

content = re.sub(r"lineChartOptions: ChartConfiguration\['options'\] = \{.*?\};", new_options, content, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("tendencias.ts actualizado para enviar el parámetro y mejorar el estilo de Chart.js.")
