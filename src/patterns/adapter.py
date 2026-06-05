"""
PATRON ESTRUCTURAL: ADAPTER
=============================
Propósito:
    Permite que interfaces incompatibles trabajen juntas. Convierte la
    interfaz de una clase en otra que el cliente espera, actuando como
    puente entre dos sistemas con contratos distintos.

Aplicación en "Voz del Ciudadano":
    El sistema necesita verificar la identidad de los ciudadanos (DPI/cédula)
    pero puede integrarse con distintos proveedores externos, cada uno con
    su propia interfaz y formato de respuesta:

      - RegistroCivilService  → método check_id(id) → {"valid": bool, "name": str}
      - BiometricoService     → método validate(numero, tipo) → (bool, str)

    El IDVerificationAdapter expone una interfaz única y limpia al resto
    del sistema, ocultando las diferencias entre proveedores.

    Sistema ──► IDVerificationAdapter ──► RegistroCivilService (adaptado)
                                     └──► BiometricoService    (adaptado)

Casos de prueba cubiertos: CP-03, CP-04
"""

from __future__ import annotations
from abc import ABC, abstractmethod

from src.models.citizen import Citizen


# ---------------------------------------------------------------------------
# SERVICIOS EXTERNOS (interfaces incompatibles que hay que adaptar)
# Los simulamos ya que en un entorno real serían APIs externas del gobierno.
# ---------------------------------------------------------------------------

class RegistroCivilService:
    """
    Servicio externo simulado del Registro Civil.
    Interfaz: check_id(dpi: str) → dict con 'valid' y 'name'
    DPIs válidos en simulación: cualquier número de 13 dígitos que no sea 0000000000000
    """

    def check_id(self, dpi: str) -> dict:
        """Verifica un DPI contra la base del Registro Civil."""
        is_valid = (
            dpi.isdigit()
            and len(dpi) == 13
            and dpi != "0000000000000"
        )
        return {
            "valid": is_valid,
            "name": "Ciudadano Registrado" if is_valid else None,
            "source": "RegistroCivil",
        }


class BiometricoService:
    """
    Servicio externo simulado de verificación biométrica.
    Interfaz distinta: validate(numero, tipo) → tuple (bool, mensaje)
    """

    def validate(self, numero: str, tipo: str = "DPI") -> tuple[bool, str]:
        """Valida un documento de identidad con reconocimiento biométrico."""
        is_valid = (
            numero.isdigit()
            and len(numero) >= 8
            and numero != "00000000"
        )
        msg = f"Verificación biométrica {'exitosa' if is_valid else 'fallida'} para {tipo} {numero}"
        return is_valid, msg


# ---------------------------------------------------------------------------
# INTERFAZ OBJETIVO (lo que el sistema espera de cualquier verificador)
# ---------------------------------------------------------------------------

class IIdentityVerifier(ABC):
    """
    Interfaz unificada de verificación de identidad.
    El resto del sistema solo conoce esta interfaz, nunca los servicios
    externos directamente.
    """

    @abstractmethod
    def verify(self, citizen: Citizen) -> bool:
        """
        Verifica la identidad del ciudadano.
        Retorna True si es válida, False si no lo es.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor de verificación."""
        pass


# ---------------------------------------------------------------------------
# ADAPTER 1: adapta RegistroCivilService a IIdentityVerifier
# ---------------------------------------------------------------------------

class RegistroCivilAdapter(IIdentityVerifier):
    """
    Adapta la interfaz de RegistroCivilService (check_id → dict)
    a la interfaz IIdentityVerifier (verify → bool).
    """

    def __init__(self, service: RegistroCivilService = None):
        self._service = service or RegistroCivilService()

    def verify(self, citizen: Citizen) -> bool:
        result = self._service.check_id(citizen.dpi)
        return result.get("valid", False)

    def get_provider_name(self) -> str:
        return "Registro Civil de la República"


# ---------------------------------------------------------------------------
# ADAPTER 2: adapta BiometricoService a IIdentityVerifier
# ---------------------------------------------------------------------------

class BiometricoAdapter(IIdentityVerifier):
    """
    Adapta la interfaz de BiometricoService (validate → tuple)
    a la interfaz IIdentityVerifier (verify → bool).
    """

    def __init__(self, service: BiometricoService = None):
        self._service = service or BiometricoService()

    def verify(self, citizen: Citizen) -> bool:
        is_valid, _ = self._service.validate(citizen.dpi, tipo="DPI")
        return is_valid

    def get_provider_name(self) -> str:
        return "Sistema Biométrico Nacional"


# ---------------------------------------------------------------------------
# FACADE DE VERIFICACION (cliente que usa el Adapter — sin conocer el proveedor)
# ---------------------------------------------------------------------------

class IDVerificationAdapter:
    """
    Punto de entrada unificado para la verificación de identidad.
    Selecciona el adaptador según el proveedor configurado y aplica
    la verificación al ciudadano, actualizando su estado.

    Uso:
        verifier = IDVerificationAdapter(provider="registro_civil")
        success = verifier.verify_and_update(citizen)
    """

    _PROVIDERS = {
        "registro_civil": RegistroCivilAdapter,
        "biometrico": BiometricoAdapter,
    }

    def __init__(self, provider: str = "registro_civil"):
        if provider not in self._PROVIDERS:
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Opciones: {list(self._PROVIDERS.keys())}"
            )
        self._adapter: IIdentityVerifier = self._PROVIDERS[provider]()
        self._provider = provider

    def verify_and_update(self, citizen: Citizen) -> bool:
        """
        Verifica la identidad del ciudadano y, si es válida,
        actualiza su estado a verificado.
        Retorna True si la verificación fue exitosa.
        """
        is_valid = self._adapter.verify(citizen)
        if is_valid:
            citizen.verify()
        return is_valid

    def get_provider_name(self) -> str:
        return self._adapter.get_provider_name()
