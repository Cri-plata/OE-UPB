path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\dashboard\tendencias\tendencias.scss"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_styles = """
.dashboard-container {
  padding: 1.5rem 2.5rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 100px);
}

.control-panel {
  display: flex;
  gap: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  margin-bottom: 2rem;
  align-items: flex-end;

  .control-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;

    label {
      font-weight: 600;
      color: #495057;
      font-size: 0.9rem;
    }

    .custom-select {
      padding: 0.75rem 1rem;
      border: 1px solid #ced4da;
      border-radius: 8px;
      font-size: 1rem;
      color: #212529;
      background-color: #fff;
      min-width: 250px;
      transition: border-color 0.2s, box-shadow 0.2s;
      cursor: pointer;

      &:focus {
        border-color: #e63946;
        outline: none;
        box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.1);
      }
    }
  }
}

.chart-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  
  h2 {
    margin-bottom: 1.5rem;
    color: #1d3557;
    font-size: 1.25rem;
    border-bottom: 2px solid #f1f3f5;
    padding-bottom: 1rem;
  }

  .chart-wrapper {
    height: 450px;
    width: 100%;
    position: relative;
  }
}

.loading-state {
  height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
}
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(content + new_styles)
print("tendencias.scss actualizado.")
