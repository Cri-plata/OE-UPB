"""
application/model_cache.py
Cache en memoria para modelos y resultados predictivos (IA-09)
==============================================================
Evita reentrenar modelos supervisados (GradientBoostingClassifier, StratifiedKFold)
innecesariamente cuando múltiples peticiones con los mismos filtros y volumen
de datos llegan en una ventana de tiempo (TTL configurable).
"""

import time
import hashlib
from typing import Any, Optional, Dict
from threading import Lock


class ModelCache:
    def __init__(self, default_ttl_seconds: int = 300, max_entries: int = 50):
        self.default_ttl = default_ttl_seconds
        self.max_entries = max_entries
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def _generate_key(
        self,
        mediciones_count: int,
        max_medicion_id: int,
        momento_origen: int,
        momento_destino: int,
        filtro_programa: Optional[str],
        filtro_anio: Optional[int],
        extra_tag: str = "",
    ) -> str:
        raw_key = f"{mediciones_count}_{max_medicion_id}_{momento_origen}_{momento_destino}_{filtro_programa}_{filtro_anio}_{extra_tag}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(
        self,
        mediciones_count: int,
        max_medicion_id: int,
        momento_origen: int,
        momento_destino: int,
        filtro_programa: Optional[str],
        filtro_anio: Optional[int],
        extra_tag: str = "",
    ) -> Optional[Dict[str, Any]]:
        key = self._generate_key(
            mediciones_count, max_medicion_id, momento_origen, momento_destino, filtro_programa, filtro_anio, extra_tag
        )
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            return entry["data"]

    def set(
        self,
        mediciones_count: int,
        max_medicion_id: int,
        momento_origen: int,
        momento_destino: int,
        filtro_programa: Optional[str],
        filtro_anio: Optional[int],
        data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        extra_tag: str = "",
    ) -> None:
        key = self._generate_key(
            mediciones_count, max_medicion_id, momento_origen, momento_destino, filtro_programa, filtro_anio, extra_tag
        )
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        with self._lock:
            # Limpieza de expirados si nos acercamos al límite
            if len(self._cache) >= self.max_entries:
                now = time.time()
                expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
                for k in expired:
                    del self._cache[k]
                if len(self._cache) >= self.max_entries:
                    oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
                    del self._cache[oldest_key]

            self._cache[key] = {
                "data": data,
                "created_at": time.time(),
                "expires_at": time.time() + ttl,
            }

    def get_by_key(self, key: str) -> Optional[Any]:
        """Obtiene una entrada de caché dada una clave arbitraria si no ha expirado."""
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None
            return entry["data"]

    def set_by_key(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        """Almacena un resultado en memoria bajo una clave arbitraria con TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        with self._lock:
            if len(self._cache) >= self.max_entries:
                now = time.time()
                expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
                for k in expired:
                    del self._cache[k]
                if len(self._cache) >= self.max_entries:
                    oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
                    del self._cache[oldest_key]

            self._cache[key] = {
                "data": data,
                "created_at": time.time(),
                "expires_at": time.time() + ttl,
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Instancia global del cache para predicciones de empleabilidad
prediccion_model_cache = ModelCache(default_ttl_seconds=300, max_entries=50)

# Instancia global del cache para habilidades demandadas, reglas y comparativas (IA NLP)
habilidades_cache = ModelCache(default_ttl_seconds=300, max_entries=100)
