"""
Pruebas del servicio y endpoint del modelo predictivo de empleabilidad (RF-71).
"""

from infrastructure.database import SessionLocal
from domain.models import Medicion, Egresado
from application.prediccion_service import predecir_empleabilidad_servicio
from fastapi.testclient import TestClient
from main import app
from application.auth_service import create_access_token


def test_servicio_prediccion_con_datos_reales():
    db = SessionLocal()
    mediciones = db.query(Medicion).all()
    egresados = db.query(Egresado).all()

    resultado = predecir_empleabilidad_servicio(
        mediciones=mediciones,
        egresados=egresados,
        momento_origen=0,
        momento_destino=1,
    )

    assert resultado["estado"] == "exitoso"
    assert resultado["total_trayectorias"] >= 30
    assert resultado["precision_modelo"] > 0
    assert resultado["f1_score"] >= 0
    assert len(resultado["predicciones_programas"]) > 0
    assert len(resultado["importancia_factores"]) > 0
    assert "clases" in resultado["matriz_confusion"]
    assert "indicadores_robustez" in resultado
    rob = resultado["indicadores_robustez"]
    assert rob["nivel_general"] in ("Alta", "Media", "Baja")
    assert rob["color_general"] in ("verde", "amarillo", "rojo")
    assert "muestra" in rob and "balance_clases" in rob and "precision" in rob
    assert len(rob["observaciones"]) > 0
    assert "validacion_temporal" in resultado
    val_temp = resultado["validacion_temporal"]
    assert "disponible" in val_temp
    print("\n[OK] Servicio predictivo ejecutado exitosamente:")
    print(f"  - Trayectorias analizadas: {resultado['total_trayectorias']}")
    print(f"  - Precisión CV: {resultado['precision_modelo']}%")
    print(f"  - Robustez estadística: {rob['nivel_general']} ({rob['color_general']})")
    print(f"  - Validación temporal: disponible={val_temp['disponible']}")
    print(f"  - Programas proyectados: {resultado['programas_analizados']}")
    print(f"  - Alertas de riesgo: {len(resultado['alertas_riesgo'])}")


def test_servicio_fallback_datos_insuficientes():
    db = SessionLocal()
    mediciones = db.query(Medicion).all()
    egresados = db.query(Egresado).all()

    # Momento 5 no tiene suficientes trayectorias longitudinales en esta BD
    resultado = predecir_empleabilidad_servicio(
        mediciones=mediciones,
        egresados=egresados,
        momento_origen=0,
        momento_destino=5,
    )

    assert resultado["estado"] == "insuficiente_datos"
    assert resultado["total_trayectorias"] < 30
    assert "mínimo de 30" in resultado["mensaje"]
    print("\n[OK] Fallback de datos insuficientes validado correctamente para Momento 5")


def test_endpoint_api_prediccion_autorizado():
    db = SessionLocal()
    from domain.models import Usuario
    user = db.query(Usuario).filter(Usuario.rol == "Coordinador_Sede", Usuario.activo == True).first()
    if not user:
        user = db.query(Usuario).first()
        user.rol = "Coordinador_Sede"
        db.commit()

    client = TestClient(app)
    token = create_access_token({
        "sub": user.correo,
        "usuario_id": user.id,
        "rol": user.rol,
        "sede_id": user.sede_id,
        "version_autorizacion": user.version_autorizacion,
    })

    response = client.get(
        "/api/ia/prediccion-empleabilidad?momento_origen=0&momento_destino=1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["estado"] in ("exitoso", "insuficiente_datos")
    assert "total_trayectorias" in data
    assert "precision_modelo" in data
    assert "predicciones_programas" in data
    assert "validacion_temporal" in data
    print("\n[OK] Endpoint GET /api/ia/prediccion-empleabilidad responde 200 OK con esquema completo")


def test_calibracion_desbalance_clases():
    import numpy as np
    from application.prediccion_service import calcular_pesos_balanceados

    # Dataset sintético desbalanceado: 80% A, 15% B, 5% C
    y_test = np.array(["A"] * 80 + ["B"] * 15 + ["C"] * 5)
    pesos = calcular_pesos_balanceados(y_test, factor_suavizado=0.65)

    assert len(pesos) == len(y_test)
    assert np.isclose(np.mean(pesos), 1.0, atol=1e-5)

    # Las clases minoritarias deben tener mayor peso que la clase mayoritaria
    peso_A = pesos[y_test == "A"][0]
    peso_B = pesos[y_test == "B"][0]
    peso_C = pesos[y_test == "C"][0]

    assert peso_C > peso_B > peso_A, f"Esperado peso_C > peso_B > peso_A, obtenido: C={peso_C}, B={peso_B}, A={peso_A}"

    db = SessionLocal()
    mediciones = db.query(Medicion).all()
    egresados = db.query(Egresado).all()
    resultado = predecir_empleabilidad_servicio(
        mediciones=mediciones,
        egresados=egresados,
        momento_origen=0,
        momento_destino=1,
    )
    assert "estrategia_balanceo" in resultado
    assert "Cost-Sensitive" in resultado["estrategia_balanceo"]
    assert "Cost-Sensitive" in resultado["indicadores_robustez"]["estrategia_balanceo"]
    print(f"\n[OK] Calibración de desbalance de clases validada: peso_C={peso_C:.2f} > peso_B={peso_B:.2f} > peso_A={peso_A:.2f}")


if __name__ == "__main__":
    test_calibracion_desbalance_clases()
    test_servicio_prediccion_con_datos_reales()
    test_servicio_fallback_datos_insuficientes()
    test_endpoint_api_prediccion_autorizado()
    print("\nTodas las pruebas del modelo predictivo pasaron satisfactoriamente.")
