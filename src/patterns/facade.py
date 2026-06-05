"""
PATRON ESTRUCTURAL: FACADE
===========================
Propósito:
    Proveer una interfaz simplificada para un conjunto de subsistemas
    complejos. El cliente interactúa con un único punto de entrada en
    lugar de coordinar múltiples subsistemas manualmente.

Aplicación en "Voz del Ciudadano":
    La aplicación Flask (y cualquier cliente) solo habla con ProposalFacade.
    La Facade internamente coordina todos los patrones y modelos:

      Flask ──► ProposalFacade
                    ├── IDVerificationAdapter  (Adapter)
                    ├── CitizenVerificationProxy (Proxy)
                    ├── ProposalDocument        (Composite)
                    ├── CommentDecorator        (Decorator)
                    ├── ResourceDecorator       (Decorator)
                    └── ModificationDecorator   (Decorator)

    El cliente no necesita saber cómo funciona ninguno de estos subsistemas.

Casos de prueba cubiertos: CP-15, CP-16, CP-17, CP-18
"""

from __future__ import annotations
import hashlib
from datetime import datetime
from typing import Optional

from src.models.citizen import Citizen
from src.models.proposal import Proposal, ProposalStatus
from src.models.signature import Signature
from src.patterns.adapter import IDVerificationAdapter
from src.patterns.proxy import CitizenVerificationProxy, ProposalService
from src.patterns.composite import ProposalDocument
from src.patterns.decorator import (
    BaseProposalDecorable,
    CommentDecorator,
    ResourceDecorator,
    ModificationDecorator,
)


class ProposalFacade:
    """
    Fachada principal del sistema Voz del Ciudadano.

    Coordina todos los subsistemas (Adapter, Proxy, Composite, Decorator)
    exponiendo una API limpia y simple para la capa de presentación (Flask).

    Gestiona en memoria los ciudadanos y propuestas durante la sesión.
    En producción estos datos vendrían de una base de datos.
    """

    def __init__(self, id_provider: str = "registro_civil"):
        # Subsistemas internos
        self._verifier = IDVerificationAdapter(provider=id_provider)
        self._proxy = CitizenVerificationProxy(ProposalService())

        # Almacenamiento en memoria
        self._citizens: dict[int, Citizen] = {}
        self._proposals: dict[int, Proposal] = {}
        self._next_citizen_id = 1
        self._next_proposal_id = 1

        # Registro de envíos al Congreso
        self._congress_submissions: list[dict] = []

    # ==========================================================================
    # CIUDADANOS
    # ==========================================================================

    def register_citizen(
        self, name: str, email: str, dpi: str, password: str
    ) -> Citizen:
        """
        RF-01 / CU-01: Registra un nuevo ciudadano en el sistema.
        Valida que el correo no esté duplicado.
        """
        for c in self._citizens.values():
            if c.email == email:
                raise ValueError(f"El correo '{email}' ya está registrado en el sistema.")

        citizen = Citizen(
            citizen_id=self._next_citizen_id,
            name=name,
            email=email,
            dpi=dpi,
            password=password,
        )
        self._citizens[self._next_citizen_id] = citizen
        self._next_citizen_id += 1
        return citizen

    def verify_citizen(self, citizen_id: int) -> bool:
        """
        RF-02 / CU-04: Verifica la identidad del ciudadano usando el Adapter.
        Actualiza su estado a VERIFICADO si la verificación es exitosa.
        """
        citizen = self._get_citizen(citizen_id)
        success = self._verifier.verify_and_update(citizen)
        return success

    def get_citizen(self, citizen_id: int) -> Citizen:
        return self._get_citizen(citizen_id)

    def authenticate(self, email: str, password: str) -> Optional[Citizen]:
        """Autentica un ciudadano por email y contraseña."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        for citizen in self._citizens.values():
            if citizen.email == email and citizen.password_hash == password_hash:
                return citizen
        return None

    # ==========================================================================
    # PROPUESTAS
    # ==========================================================================

    def create_proposal(
        self,
        citizen_id: int,
        title: str,
        description: str,
        body: str,
    ) -> Proposal:
        """
        RF-03 / CU-08: Crea una propuesta legislativa.
        El Proxy valida que el ciudadano esté verificado.
        """
        citizen = self._get_citizen(citizen_id)
        proposal = self._proxy.create_proposal(
            citizen=citizen,
            title=title,
            description=description,
            body=body,
            proposal_id=self._next_proposal_id,
        )
        self._proposals[self._next_proposal_id] = proposal
        self._next_proposal_id += 1
        return proposal

    def get_proposal(self, proposal_id: int) -> Proposal:
        return self._get_proposal(proposal_id)

    def get_all_proposals(self) -> list[Proposal]:
        """CU-02: Retorna todas las propuestas ordenadas por fecha de creación."""
        return sorted(
            self._proposals.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )

    def get_proposal_document(self, proposal_id: int) -> ProposalDocument:
        """
        CU-03: Construye y retorna el árbol Composite del documento
        de la propuesta para su renderizado.
        """
        proposal = self._get_proposal(proposal_id)
        return ProposalDocument.build_from_proposal(proposal)

    # ==========================================================================
    # FIRMAS
    # ==========================================================================

    def sign_proposal(self, citizen_id: int, proposal_id: int) -> Signature:
        """
        RF-04 / CU-05: Registra la firma de un ciudadano en una propuesta.
        El Proxy valida verificación, estado activo y unicidad de firma.
        Dispara congelamiento automático al alcanzar 25,000 firmas.
        """
        citizen = self._get_citizen(citizen_id)
        proposal = self._get_proposal(proposal_id)

        signature = self._proxy.sign_proposal(citizen, proposal)

        # Verificar si se alcanzó el límite constitucional
        if proposal.signature_count >= Proposal.SIGNATURE_LIMIT:
            self._freeze_and_send(proposal)

        return signature

    # ==========================================================================
    # DECORADORES (comentarios, recursos, modificaciones)
    # ==========================================================================

    def add_comment(
        self, proposal_id: int, author: str, text: str
    ) -> Proposal:
        """RF-05 / CU-06: Añade un comentario a la propuesta (Decorator)."""
        proposal = self._get_proposal(proposal_id)
        decorable = BaseProposalDecorable(proposal)
        CommentDecorator(decorable, author=author, text=text)
        return proposal

    def add_resource(
        self, proposal_id: int, title: str, url: str
    ) -> Proposal:
        """RF-06 / CU-07: Añade un recurso externo a la propuesta (Decorator)."""
        proposal = self._get_proposal(proposal_id)
        decorable = BaseProposalDecorable(proposal)
        ResourceDecorator(decorable, title=title, url=url)
        return proposal

    def add_modification(
        self,
        proposal_id: int,
        requestor_id: int,
        description: str,
        new_text: str,
    ) -> Proposal:
        """RF-07 / CU-09: Añade una modificación al texto (Decorator)."""
        proposal = self._get_proposal(proposal_id)
        decorable = BaseProposalDecorable(proposal)
        ModificationDecorator(
            decorable,
            description=description,
            new_text=new_text,
            requestor_id=requestor_id,
        )
        return proposal

    # ==========================================================================
    # CONGELAMIENTO Y ENVÍO AL CONGRESO
    # ==========================================================================

    def _freeze_and_send(self, proposal: Proposal):
        """
        RF-09 / RF-10 / CU-10 / CU-12:
        Congela criptográficamente la propuesta y la envía al Congreso.
        Se ejecuta automáticamente al alcanzar 25,000 firmas.
        """
        crypto_hash = proposal.freeze()
        self._send_to_congress(proposal, crypto_hash)

    def _send_to_congress(self, proposal: Proposal, crypto_hash: str):
        """CU-12: Registra el envío formal al Congreso."""
        submission = {
            "proposal_id": proposal.proposal_id,
            "title": proposal.title,
            "crypto_hash": crypto_hash,
            "signature_count": proposal.signature_count,
            "submitted_at": datetime.now().isoformat(),
            "status": "ENVIADO",
        }
        self._congress_submissions.append(submission)
        proposal.mark_sent()

    def get_congress_submissions(self) -> list[dict]:
        """Retorna el registro de propuestas enviadas al Congreso."""
        return list(self._congress_submissions)

    # ==========================================================================
    # HELPERS PRIVADOS
    # ==========================================================================

    def _get_citizen(self, citizen_id: int) -> Citizen:
        citizen = self._citizens.get(citizen_id)
        if not citizen:
            raise ValueError(f"Ciudadano con ID {citizen_id} no encontrado.")
        return citizen

    def _get_proposal(self, proposal_id: int) -> Proposal:
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Propuesta con ID {proposal_id} no encontrada.")
        return proposal
