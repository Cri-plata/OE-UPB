"""Contrato común de errores HTTP (API-02).

Toda respuesta de error lleva `detail`: un texto o, cuando el cliente necesita
distinguir el caso, un objeto con `codigo` y `mensaje`. El 422 de validación de
Pydantic conserva el esquema estándar de FastAPI (`HTTPValidationError`).
"""

from pydantic import BaseModel


class ErrorCodificado(BaseModel):
    codigo: str
    mensaje: str


class ErrorResponse(BaseModel):
    detail: str | ErrorCodificado


DESCRIPCIONES = {
    400: "Solicitud inválida",
    401: "Sesión ausente, vencida o revocada, o credenciales incorrectas",
    403: "El rol, la sede o los permisos no autorizan la operación",
    404: "El recurso no existe dentro del alcance autorizado",
    409: "La operación entra en conflicto con el estado actual",
    413: "El contenido supera el tamaño permitido",
    500: "Error interno; la operación no aplicó cambios",
}


def errores(*codigos: int, **descripciones: str) -> dict:
    """Bloque `responses` para FastAPI. Las descripciones se pasan como `d404="..."`."""
    return {
        codigo: {"model": ErrorResponse, "description": descripciones.get(f"d{codigo}", DESCRIPCIONES[codigo])}
        for codigo in codigos
    }


RESPUESTAS_PROTEGIDAS = errores(401, 403)
