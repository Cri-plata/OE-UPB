import re

path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\application\auth_service.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_code = """
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        rol: str = payload.get("rol")
        sede_id: int = payload.get("sede_id")
        if correo is None:
            raise credentials_exception
        return {"correo": correo, "rol": rol, "sede_id": sede_id}
    except jwt.PyJWTError:
        raise credentials_exception
"""

content = content + "\n" + new_code

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("get_current_user dependency agregada a auth_service.")
