export function exportChart(selector: string, filename: string): void {
  const canvas = document.querySelector<HTMLCanvasElement>(selector);
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = filename;
  link.href = canvas.toDataURL('image/png', 1);
  link.click();
}
