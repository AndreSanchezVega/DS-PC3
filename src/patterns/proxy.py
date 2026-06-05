"""
PATRON ESTRUCTURAL: PROXY
==========================
Propósito:
    Proporciona un sustituto o representante de otro objeto para controlar
    el acceso a él. El Proxy actúa como intermediario añadiendo lógica
    antes o después de delegar al objeto real.

Aplicación en "Voz del Ciudadano":
    El ProposalService es el objeto real que registra firmas y crea
    propuestas. El CitizenVerificationProxy se interpone antes de cada
    operación sensible para validar:

      1. Que el ciudadano esté verificado (identidad confirmada)
      2. Que no haya firmado ya la misma propuesta (unicidad)
      3. Que la propuesta esté activa (estado válido)

    El resto del sistema (Flask, Facade) solo habla con el Proxy,
    nunca directamente con el servicio real.

    Cliente ──► CitizenVerificationProxy ──► ProposalService (real)
                    │
                    └── valida antes de delegar

Casos de prueba cubiertos: CP-05, CP-06, CP-07, CP-08, CP-18
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from src.models.citizen import Citizen
from src.models.proposal import Proposal, ProposalStatus
from src.models.signature import Signature


# ---------------------------------------------------------------------------
# INTERFAZ DEL SUJETO (define operaciones que Proxy y Real comparten)
# ---------------------------------------------------------------------------

class IProposalService(ABC):
    """
    Interfaz común para el servicio real y el proxy.
    Garantiza que el proxy sea intercambiable con el objeto real.
    """

    @abstractmethod
    def sign_proposal(self, citizen: Citizen, proposal: Proposal) -> Signature:
        """Registra la firma de un ciudadano en una propuesta."""
        pass

    @abstractmethod
    def create_proposal(
        self,
        citizen: Citizen,
        title: str,
        description: str,
        body: str,
        proposal_id: int,
    ) -> Proposal:
        """Crea una nueva propuesta legislativa."""
        pass


# ---------------------------------------------------------------------------
# SUJETO REAL (lógica de negocio sin validaciones de acceso)
# ---------------------------------------------------------------------------

class ProposalService(IProposalService):
    """
    Servicio real que ejecuta las operaciones sobre propuestas.
    No contiene lógica de control de acceso — eso es responsabilidad
    exclusiva del Proxy.
    """

    def sign_proposal(self, citizen: Citizen, proposal: Proposal) -> Signature:
        sig = Signature(
            signature_id=len(proposal.signatures) + 1,
            citizen_id=citizen.citizen_id,
            proposal_id=proposal.proposal_id,
            citizen_hash=citizen.get_hash(),
        )
        proposal.signatures.append(sig)
        return sig

    def create_proposal(
        self,
        citizen: Citizen,
        title: str,
        description: str,
        body: str,
        proposal_id: int,
    ) -> Proposal:
        return Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            body=body,
            proposer_id=citizen.citizen_id,
        )


# ---------------------------------------------------------------------------
# PROXY (control de acceso + delegación al objeto real)
# ---------------------------------------------------------------------------

class CitizenVerificationProxy(IProposalService):
    """
    Proxy de verificación ciudadana.

    Intercepta las operaciones de firma y creación de propuestas para
    garantizar que solo ciudadanos verificados puedan realizarlas, y que
    las reglas de negocio (unicidad de firma, estado activo) se cumplan
    antes de delegar al servicio real.

    Reglas que aplica:
      - sign_proposal:
          * Ciudadano debe estar verificado
          * Propuesta debe estar ACTIVA
          * Ciudadano no debe haber firmado ya esta propuesta
      - create_proposal:
          * Ciudadano debe estar verificado
    """

    def __init__(self, real_service: IProposalService = None):
        self._real_service = real_service or ProposalService()

    # -- Validaciones privadas ----------------------------------------------

    def _assert_citizen_verified(self, citizen: Citizen):
        if not citizen.verified:
            raise PermissionError(
                f"Ciudadano '{citizen.name}' no está verificado. "
                "Debe verificar su identidad antes de realizar esta acción."
            )

    def _assert_proposal_active(self, proposal: Proposal):
        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(
                f"La propuesta '{proposal.title}' no está activa "
                f"(estado actual: {proposal.status.value}). "
                "No se puede firmar una propuesta congelada o expirada."
            )

    def _assert_not_already_signed(self, citizen: Citizen, proposal: Proposal):
        already_signed = any(
            sig.citizen_id == citizen.citizen_id
            for sig in proposal.signatures
        )
        if already_signed:
            raise ValueError(
                f"El ciudadano '{citizen.name}' ya firmó esta propuesta. "
                "Solo se permite una firma por ciudadano."
            )

    # -- Operaciones con control de acceso ----------------------------------

    def sign_proposal(self, citizen: Citizen, proposal: Proposal) -> Signature:
        """
        Valida acceso y delega al servicio real.
        Orden de validación:
          1. Ciudadano verificado
          2. Propuesta activa
          3. No firmó ya
        """
        self._assert_citizen_verified(citizen)
        self._assert_proposal_active(proposal)
        self._assert_not_already_signed(citizen, proposal)

        # Todas las validaciones pasaron → delegar al servicio real
        signature = self._real_service.sign_proposal(citizen, proposal)
        return signature

    def create_proposal(
        self,
        citizen: Citizen,
        title: str,
        description: str,
        body: str,
        proposal_id: int,
    ) -> Proposal:
        """
        Solo ciudadanos verificados pueden crear propuestas.
        """
        self._assert_citizen_verified(citizen)
        return self._real_service.create_proposal(
            citizen, title, description, body, proposal_id
        )
