"""
PATRON ESTRUCTURAL: COMPOSITE
==============================
Propósito:
    Componer objetos en estructuras de árbol para representar jerarquías
    parte-todo. Permite tratar objetos individuales y composiciones de
    objetos de manera uniforme.

Aplicación en "Voz del Ciudadano":
    El documento de una propuesta legislativa es una jerarquía de componentes:
    un documento raíz contiene secciones, y cada sección puede contener
    subsecciones o contenido hoja (texto, firmas, anexos).

    ProposalDocument (raíz)
    ├── ProposalSection: "Encabezado"
    │   ├── ProposalLeaf: "Título"
    │   └── ProposalLeaf: "Proponente"
    ├── ProposalSection: "Cuerpo Normativo"
    │   ├── ProposalLeaf: "Exposición de motivos"
    │   └── ProposalSection: "Articulado"
    │       ├── ProposalLeaf: "Artículo 1"
    │       └── ProposalLeaf: "Artículo 2"
    └── ProposalSection: "Anexos"
        └── ProposalLeaf: "Firma digital"

Casos de prueba cubiertos: CP-09, CP-10
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


# ---------------------------------------------------------------------------
# COMPONENTE BASE (interfaz común para hojas y composites)
# ---------------------------------------------------------------------------

class ProposalComponent(ABC):
    """
    Componente abstracto del Composite.
    Define la interfaz que comparten hojas y secciones.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def render(self, indent: int = 0) -> str:
        """Renderiza el componente como texto con indentación."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Cuenta el número total de nodos en el subárbol."""
        pass

    @abstractmethod
    def get_content(self) -> str:
        """Retorna el contenido textual plano del componente."""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}'>"


# ---------------------------------------------------------------------------
# HOJA (nodo sin hijos — contiene contenido real)
# ---------------------------------------------------------------------------

class ProposalLeaf(ProposalComponent):
    """
    Hoja del Composite.
    Representa un fragmento de contenido indivisible: un título,
    un artículo, una firma, un párrafo.
    """

    def __init__(self, name: str, content: str):
        super().__init__(name)
        self.content = content

    def render(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}[{self.name}]\n{prefix}  {self.content}"

    def count(self) -> int:
        return 1

    def get_content(self) -> str:
        return self.content


# ---------------------------------------------------------------------------
# COMPOSITE (nodo con hijos — puede contener hojas u otros composites)
# ---------------------------------------------------------------------------

class ProposalSection(ProposalComponent):
    """
    Composite del patrón.
    Representa una sección del documento que puede contener
    subsecciones u hojas. Opera sobre sus hijos de forma recursiva.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[ProposalComponent] = []

    # -- Gestión de hijos ---------------------------------------------------

    def add(self, component: ProposalComponent) -> ProposalSection:
        """Agrega un componente hijo. Retorna self para encadenamiento."""
        self._children.append(component)
        return self

    def remove(self, component: ProposalComponent):
        """Elimina un componente hijo."""
        self._children.remove(component)

    def get_children(self) -> List[ProposalComponent]:
        return list(self._children)

    # -- Operaciones del componente -----------------------------------------

    def render(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}=== {self.name.upper()} ==="]
        for child in self._children:
            lines.append(child.render(indent + 1))
        return "\n".join(lines)

    def count(self) -> int:
        """Cuenta este nodo más todos los nodos de sus hijos recursivamente."""
        return 1 + sum(child.count() for child in self._children)

    def get_content(self) -> str:
        """Concatena el contenido de todos los hijos."""
        return "\n".join(child.get_content() for child in self._children)


# ---------------------------------------------------------------------------
# DOCUMENTO RAÍZ (Composite especial que representa la propuesta completa)
# ---------------------------------------------------------------------------

class ProposalDocument:
    """
    Raíz del árbol Composite.
    Construye y gestiona la estructura jerárquica completa del
    documento de una propuesta legislativa.

    Uso:
        doc = ProposalDocument.build_from_proposal(proposal)
        print(doc.render())
        total_nodos = doc.count()
    """

    def __init__(self, proposal_id: int, title: str):
        self.proposal_id = proposal_id
        self.title = title
        self._root = ProposalSection(f"Propuesta #{proposal_id}: {title}")

    # -- Construcción del árbol ---------------------------------------------

    @classmethod
    def build_from_proposal(cls, proposal) -> "ProposalDocument":
        """
        Factory method: construye el árbol Composite completo
        a partir de un objeto Proposal.
        """
        doc = cls(proposal.proposal_id, proposal.title)

        # Sección 1: Encabezado
        header = ProposalSection("Encabezado")
        header.add(ProposalLeaf("Título", proposal.title))
        header.add(ProposalLeaf("Descripción", proposal.description))
        header.add(ProposalLeaf("Estado", proposal.status.value))
        header.add(ProposalLeaf(
            "Plazo",
            f"{proposal.days_remaining} días restantes de 90"
        ))

        # Sección 2: Cuerpo normativo
        body = ProposalSection("Cuerpo Normativo")
        body.add(ProposalLeaf("Texto del proyecto de ley", proposal.body))

        # Sección 3: Firmas
        signatures = ProposalSection("Registro de Firmas")
        signatures.add(ProposalLeaf(
            "Contador",
            f"{proposal.signature_count} / 25,000 firmas recolectadas"
        ))
        for sig in proposal.signatures[:5]:   # muestra máx 5 en el árbol
            signatures.add(ProposalLeaf(
                f"Firma #{sig.signature_id}",
                f"Ciudadano: {sig.citizen_hash} — {sig.signed_at.strftime('%Y-%m-%d %H:%M')}"
            ))

        # Sección 4: Anexos (comentarios, recursos, modificaciones)
        annexes = ProposalSection("Anexos")

        if proposal.comments:
            comments_sec = ProposalSection("Comentarios")
            for c in proposal.comments:
                comments_sec.add(ProposalLeaf(c.author, c.text))
            annexes.add(comments_sec)

        if proposal.resources:
            resources_sec = ProposalSection("Recursos de Apoyo")
            for r in proposal.resources:
                resources_sec.add(ProposalLeaf(r.title, r.url))
            annexes.add(resources_sec)

        if proposal.modifications:
            mods_sec = ProposalSection("Modificaciones")
            for m in proposal.modifications:
                mods_sec.add(ProposalLeaf(m.description, m.new_text))
            annexes.add(mods_sec)

        # Sección 5: Hash criptográfico (solo si está congelada)
        if proposal.crypto_hash:
            crypto = ProposalSection("Sellado Criptográfico")
            crypto.add(ProposalLeaf("SHA-256", proposal.crypto_hash))
            crypto.add(ProposalLeaf(
                "Congelada el",
                proposal.frozen_at.strftime("%Y-%m-%d %H:%M:%S")
            ))
            doc._root.add(crypto)

        # Ensamblar árbol
        doc._root.add(header)
        doc._root.add(body)
        doc._root.add(signatures)
        doc._root.add(annexes)

        return doc

    # -- Operaciones del documento ------------------------------------------

    def add_section(self, section: ProposalSection):
        """Agrega una sección al documento raíz."""
        self._root.add(section)

    def render(self) -> str:
        """Renderiza el árbol completo como texto."""
        return self._root.render()

    def count(self) -> int:
        """Cuenta el total de nodos en el árbol (incluye la raíz)."""
        return self._root.count()

    def get_full_content(self) -> str:
        """Retorna todo el contenido textual del documento (para hash)."""
        return self._root.get_content()

    def __repr__(self):
        return f"<ProposalDocument proposal_id={self.proposal_id} nodos={self.count()}>"
