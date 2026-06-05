import hashlib
from datetime import datetime


class Citizen:
    """
    Modelo de dominio: Ciudadano.
    Representa a un usuario registrado en el sistema.
    Puede estar verificado o no verificado.
    """

    def __init__(self, citizen_id: int, name: str, email: str, dpi: str, password: str):
        self.citizen_id = citizen_id
        self.name = name
        self.email = email
        self.dpi = dpi
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.verified = False
        self.created_at = datetime.now()

    def verify(self):
        """Marca al ciudadano como verificado."""
        self.verified = True

    def get_hash(self) -> str:
        """Retorna un hash unico del ciudadano basado en su DPI."""
        return hashlib.sha256(self.dpi.encode()).hexdigest()[:16]

    def __repr__(self):
        status = "VERIFICADO" if self.verified else "NO_VERIFICADO"
        return f"<Citizen id={self.citizen_id} name='{self.name}' status={status}>"
