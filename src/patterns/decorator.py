"""
PATRON ESTRUCTURAL: DECORATOR
==============================
Propósito:
    Añadir responsabilidades a un objeto dinámicamente sin modificar su
    clase. Los Decorators envuelven al objeto original y añaden
    comportamiento antes o después de delegar a él.

Aplicación en "Voz del Ciudadano":
    Una propuesta legislativa puede enriquecerse dinámicamente con
    distintos tipos de elementos: comentarios ciudadanos, recursos
    externos de apoyo y modificaciones al texto. En lugar de meter
    toda esa lógica en la clase Proposal, cada tipo de elemento es
    un Decorator independiente que envuelve la propuesta.

    Propuesta base
        └── CommentDecorator      → añade comentarios
                └── ResourceDecorator  → añade recursos de apoyo
                        └── ModificationDecorator  → añade modificaciones

    Se pueden encadenar en cualquier orden y cantidad.

Casos de prueba cubiertos: CP-11, CP-12, CP-13, CP-14
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from src.models.proposal import Proposal, Comment, Resource, Modification, ProposalStatus


# ---------------------------------------------------------------------------
# COMPONENTE BASE (interfaz que Proposal y Decorators comparten)
# ---------------------------------------------------------------------------

class ProposalDecorable(ABC):
    """
    Interfaz base del patrón Decorator.
    Define las operaciones que tanto la propuesta concreta como
    todos sus decoradores deben implementar.
    """

    @abstractmethod
    def get_proposal(self) -> Proposal:
        """Retorna la propuesta subyacente."""
        pass

    @abstractmethod
    def describe(self) -> str:
        """Retorna una descripción del estado actual de la propuesta."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def status(self):
        pass


# ---------------------------------------------------------------------------
# COMPONENTE CONCRETO (la propuesta base que se va a decorar)
# ---------------------------------------------------------------------------

class BaseProposalDecorable(ProposalDecorable):
    """
    Componente concreto: envuelve una Proposal real y la hace
    compatible con la interfaz del Decorator.
    """

    def __init__(self, proposal: Proposal):
        self._proposal = proposal

    def get_proposal(self) -> Proposal:
        return self._proposal

    def describe(self) -> str:
        return (
            f"Propuesta: '{self._proposal.title}' | "
            f"Estado: {self._proposal.status.value} | "
            f"Firmas: {self._proposal.signature_count}"
        )

    @property
    def title(self) -> str:
        return self._proposal.title

    @property
    def status(self):
        return self._proposal.status


# ---------------------------------------------------------------------------
# DECORATOR BASE (envuelve cualquier ProposalDecorable)
# ---------------------------------------------------------------------------

class ProposalDecorator(ProposalDecorable, ABC):
    """
    Decorator abstracto base.
    Mantiene una referencia al componente que envuelve y delega
    las operaciones base a él.
    """

    def __init__(self, component: ProposalDecorable):
        self._component = component

    def get_proposal(self) -> Proposal:
        return self._component.get_proposal()

    def describe(self) -> str:
        return self._component.describe()

    @property
    def title(self) -> str:
        return self._component.title

    @property
    def status(self):
        return self._component.status


# ---------------------------------------------------------------------------
# DECORATOR CONCRETO 1: Comentarios
# ---------------------------------------------------------------------------

class CommentDecorator(ProposalDecorator):
    """
    Decorator que añade un comentario ciudadano a la propuesta.

    RF-05 / CU-06: Ciudadanos verificados pueden añadir comentarios
    de análisis o apoyo a propuestas activas.
    """

    def __init__(self, component: ProposalDecorable, author: str, text: str):
        super().__init__(component)

        proposal = self.get_proposal()

        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(
                f"No se pueden añadir comentarios a una propuesta "
                f"en estado '{proposal.status.value}'."
            )
        if not text.strip():
            raise ValueError("El comentario no puede estar vacío.")
        if len(text) > 1000:
            raise ValueError("El comentario no puede superar los 1,000 caracteres.")

        comment = Comment(author=author, text=text)
        proposal.comments.append(comment)
        self._added_comment = comment

    def describe(self) -> str:
        base = super().describe()
        total = len(self.get_proposal().comments)
        return f"{base} | Comentarios: {total}"


# ---------------------------------------------------------------------------
# DECORATOR CONCRETO 2: Recursos de apoyo
# ---------------------------------------------------------------------------

class ResourceDecorator(ProposalDecorator):
    """
    Decorator que adjunta un recurso externo de apoyo a la propuesta.

    RF-06 / CU-07: Ciudadanos pueden añadir URLs de estudios,
    documentos o referencias que respalden la propuesta.
    """

    def __init__(self, component: ProposalDecorable, title: str, url: str):
        super().__init__(component)

        proposal = self.get_proposal()

        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(
                f"No se pueden añadir recursos a una propuesta "
                f"en estado '{proposal.status.value}'."
            )
        if not url.startswith(("http://", "https://")):
            raise ValueError("La URL del recurso debe comenzar con http:// o https://")
        if not title.strip():
            raise ValueError("El título del recurso no puede estar vacío.")

        resource = Resource(title=title, url=url)
        proposal.resources.append(resource)
        self._added_resource = resource

    def describe(self) -> str:
        base = super().describe()
        total = len(self.get_proposal().resources)
        return f"{base} | Recursos: {total}"


# ---------------------------------------------------------------------------
# DECORATOR CONCRETO 3: Modificaciones al texto
# ---------------------------------------------------------------------------

class ModificationDecorator(ProposalDecorator):
    """
    Decorator que registra una modificación o enmienda al texto
    original de la propuesta.

    RF-07 / CU-09: Solo el proponente puede añadir modificaciones
    a su propia propuesta mientras esté activa.
    """

    def __init__(
        self,
        component: ProposalDecorable,
        description: str,
        new_text: str,
        requestor_id: int,
    ):
        super().__init__(component)

        proposal = self.get_proposal()

        if proposal.status != ProposalStatus.ACTIVE:
            raise ValueError(
                f"No se pueden añadir modificaciones a una propuesta "
                f"en estado '{proposal.status.value}'."
            )
        if requestor_id != proposal.proposer_id:
            raise PermissionError(
                "Solo el proponente puede añadir modificaciones a su propuesta."
            )
        if not description.strip() or not new_text.strip():
            raise ValueError("La descripción y el texto modificado son obligatorios.")

        modification = Modification(description=description, new_text=new_text)
        proposal.modifications.append(modification)
        self._added_modification = modification

    def describe(self) -> str:
        base = super().describe()
        total = len(self.get_proposal().modifications)
        return f"{base} | Modificaciones: {total}"
