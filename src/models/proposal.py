import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class ProposalStatus(Enum):
    ACTIVE = "ACTIVA"
    FROZEN = "CONGELADA"
    EXPIRED = "EXPIRADA"
    SENT = "ENVIADA_AL_CONGRESO"


class Comment:
    """Comentario añadido a una propuesta."""

    def __init__(self, author: str, text: str):
        self.author = author
        self.text = text
        self.created_at = datetime.now()


class Resource:
    """Recurso externo de apoyo a una propuesta (URL + título)."""

    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url
        self.added_at = datetime.now()


class Modification:
    """Modificación o enmienda al texto original de la propuesta."""

    def __init__(self, description: str, new_text: str):
        self.description = description
        self.new_text = new_text
        self.created_at = datetime.now()


class Proposal:
    """
    Modelo de dominio: Propuesta Legislativa Ciudadana.

    Estados posibles:
      ACTIVA          → acepta firmas y comentarios
      CONGELADA       → alcanzó 25,000 firmas; hash generado
      EXPIRADA        → pasaron 90 días sin alcanzar el límite
      ENVIADA_AL_CONGRESO → ya fue enviada formalmente
    """

    SIGNATURE_LIMIT = 25_000
    DAYS_LIMIT = 90

    def __init__(
        self,
        proposal_id: int,
        title: str,
        description: str,
        body: str,
        proposer_id: int,
    ):
        self.proposal_id = proposal_id
        self.title = title
        self.description = description
        self.body = body
        self.proposer_id = proposer_id
        self.status = ProposalStatus.ACTIVE
        self.created_at = datetime.now()
        self.deadline = self.created_at + timedelta(days=self.DAYS_LIMIT)
        self.frozen_at: Optional[datetime] = None
        self.sent_at: Optional[datetime] = None
        self.crypto_hash: Optional[str] = None

        # Colecciones gestionadas por los Decorators y el Proxy
        self.signatures: list = []
        self.comments: list[Comment] = []
        self.resources: list[Resource] = []
        self.modifications: list[Modification] = []

    # ------------------------------------------------------------------
    # Propiedades de conveniencia
    # ------------------------------------------------------------------

    @property
    def signature_count(self) -> int:
        return len(self.signatures)

    @property
    def days_remaining(self) -> int:
        delta = self.deadline - datetime.now()
        return max(0, delta.days)

    @property
    def is_active(self) -> bool:
        return self.status == ProposalStatus.ACTIVE

    # ------------------------------------------------------------------
    # Operaciones de estado
    # ------------------------------------------------------------------

    def freeze(self) -> str:
        """
        Congela la propuesta y genera su hash criptográfico SHA-256.
        Retorna el hash generado.
        """
        self.status = ProposalStatus.FROZEN
        self.frozen_at = datetime.now()
        raw = f"{self.proposal_id}-{self.title}-{self.signature_count}-{self.frozen_at.isoformat()}"
        self.crypto_hash = hashlib.sha256(raw.encode()).hexdigest()
        return self.crypto_hash

    def mark_sent(self):
        """Marca la propuesta como enviada al Congreso."""
        self.status = ProposalStatus.SENT
        self.sent_at = datetime.now()

    def expire(self):
        """Expira la propuesta por vencimiento de plazo."""
        self.status = ProposalStatus.EXPIRED

    def __repr__(self):
        return (
            f"<Proposal id={self.proposal_id} "
            f"title='{self.title[:30]}' "
            f"status={self.status.value} "
            f"signatures={self.signature_count}>"
        )
