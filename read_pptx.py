import zipfile
import re
import os

pptx_path = r"C:\Users\USUARIO\Documents\U sexto\otros\OEUPB.pptx"

if not os.path.exists(pptx_path):
    print("El archivo no existe en esa ruta.")
else:
    with zipfile.ZipFile(pptx_path, "r") as z:
        slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
        
        # Sort them numerically
        slide_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
        
        print(f"Total diapositivas: {len(slide_files)}\n")
        
        for slide in slide_files:
            xml_content = z.read(slide).decode("utf-8")
            # Extract text from <a:t> tags
            texts = re.findall(r'<a:t>(.*?)</a:t>', xml_content)
            print(f"--- Diapositiva {re.search(r'(\d+)', slide).group()} ---")
            for t in texts:
                if t.strip():
                    print("- " + t)
            print("\n")
