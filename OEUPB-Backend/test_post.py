import requests

url = "http://localhost:8000/api/carga/excel"
file_path = r"C:\Users\USUARIO\Documents\U sexto\egresados\Consolidado Momento 1 2025.xlsx"

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"momento": "1"}
        print("Enviando petición...")
        response = requests.post(url, files=files, data=data, timeout=5)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
except Exception as e:
    print("Error:", e)
