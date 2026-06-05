import hashlib
from datetime import datetime


class Signature:
    """
    Modelo de dominio: Firma digital.
    Registra que un ciudadano firmó una propuesta en un momento específico.
    """

    def __init__(self, signature_id: int, citizen_id: int, proposal_id: int, citizen_hash: str):
        self.signature_id = signature_id
        self.citizen_id = citizen_id
        self.proposal_id = proposal_id
        self.citizen_hash = citizen_hash
        self.signed_at = datetime.now()
        self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Genera un hash unico para esta firma."""
        raw = f"{self.citizen_id}-{self.proposal_id}-{self.signed_at.isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def __repr__(self):
        return (
            f"<Signature id={self.signature_id} "
            f"citizen={self.citizen_id} "
            f"proposal={self.proposal_id} "
            f"at={self.signed_at.strftime('%Y-%m-%d %H:%M')}>"
        )
