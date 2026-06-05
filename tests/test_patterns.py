"""
Casos de prueba — Voz del Ciudadano
Cubre los 18 CPs definidos en docs/casos_de_prueba.md

Ejecución:
    py -m pytest tests/ -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.citizen import Citizen
from src.models.proposal import Proposal, ProposalStatus
from src.models.signature import Signature
from src.patterns.adapter import IDVerificationAdapter, RegistroCivilAdapter, BiometricoAdapter
from src.patterns.proxy import CitizenVerificationProxy, ProposalService
from src.patterns.composite import ProposalDocument, ProposalSection, ProposalLeaf
from src.patterns.decorator import BaseProposalDecorable, CommentDecorator, ResourceDecorator, ModificationDecorator
from src.patterns.facade import ProposalFacade


# ===========================================================================
# FIXTURES — objetos reutilizables entre tests
# ===========================================================================

@pytest.fixture
def citizen_verified():
    c = Citizen(1, "Ana López", "ana@test.com", "1234567890101", "pass123")
    c.verify()
    return c

@pytest.fixture
def citizen_unverified():
    return Citizen(2, "Bob Sin Verificar", "bob@test.com", "9999999999999", "pass123")

@pytest.fixture
def active_proposal(citizen_verified):
    return Proposal(
        proposal_id=1,
        title="Ley de Prueba",
        description="Descripción de prueba",
        body="Artículo 1. Texto de la ley.",
        proposer_id=citizen_verified.citizen_id,
    )

@pytest.fixture
def proxy():
    return CitizenVerificationProxy(ProposalService())

@pytest.fixture
def facade():
    f = ProposalFacade(id_provider="registro_civil")
    return f


# ===========================================================================
# MÓDULO 1: CIUDADANOS Y VERIFICACIÓN
# ===========================================================================

class TestCiudadanos:

    def test_CP01_registro_exitoso(self, facade):
        """CP-01: Ciudadano registrado correctamente con estado NO_VERIFICADO."""
        citizen = facade.register_citizen("Ana López", "ana@test.com", "1234567890101", "pass")
        assert citizen.citizen_id == 1
        assert citizen.name == "Ana López"
        assert citizen.verified is False

    def test_CP02_registro_falla_correo_duplicado(self, facade):
        """CP-02: No se puede registrar dos ciudadanos con el mismo correo."""
        facade.register_citizen("Ana López", "ana@test.com", "1234567890101", "pass")
        with pytest.raises(ValueError, match="ya está registrado"):
            facade.register_citizen("Otro Nombre", "ana@test.com", "9876543210987", "pass")

    def test_CP03_verificacion_adapter_exitosa(self, facade):
        """CP-03: Adapter verifica DPI válido y actualiza estado a VERIFICADO."""
        citizen = facade.register_citizen("Ana López", "ana@test.com", "1234567890101", "pass")
        assert citizen.verified is False
        result = facade.verify_citizen(citizen.citizen_id)
        assert result is True
        assert citizen.verified is True

    def test_CP04_verificacion_adapter_falla_dpi_invalido(self):
        """CP-04: Adapter rechaza DPI inválido; ciudadano permanece NO_VERIFICADO."""
        citizen = Citizen(1, "Bob", "bob@test.com", "0000000000000", "pass")
        adapter = IDVerificationAdapter(provider="registro_civil")
        result = adapter.verify_and_update(citizen)
        assert result is False
        assert citizen.verified is False


# ===========================================================================
# MÓDULO 2: PROXY — Control de Acceso
# ===========================================================================

class TestProxy:

    def test_CP05_proxy_bloquea_ciudadano_no_verificado(
        self, proxy, citizen_unverified, active_proposal
    ):
        """CP-05: Proxy lanza PermissionError si el ciudadano no está verificado."""
        with pytest.raises(PermissionError, match="no está verificado"):
            proxy.sign_proposal(citizen_unverified, active_proposal)

    def test_CP06_proxy_permite_firma_exitosa(
        self, proxy, citizen_verified, active_proposal
    ):
        """CP-06: Ciudadano verificado firma correctamente; contador sube a 1."""
        sig = proxy.sign_proposal(citizen_verified, active_proposal)
        assert isinstance(sig, Signature)
        assert active_proposal.signature_count == 1
        assert sig.citizen_id == citizen_verified.citizen_id

    def test_CP07_proxy_bloquea_firma_duplicada(
        self, proxy, citizen_verified, active_proposal
    ):
        """CP-07: No se puede firmar dos veces la misma propuesta."""
        proxy.sign_proposal(citizen_verified, active_proposal)
        with pytest.raises(ValueError, match="ya firmó"):
            proxy.sign_proposal(citizen_verified, active_proposal)

    def test_CP08_proxy_bloquea_propuesta_congelada(
        self, proxy, citizen_verified, active_proposal
    ):
        """CP-08: No se puede firmar una propuesta en estado CONGELADA."""
        active_proposal.freeze()
        assert active_proposal.status == ProposalStatus.FROZEN
        with pytest.raises(ValueError, match="no está activa"):
            proxy.sign_proposal(citizen_verified, active_proposal)

    def test_CP18_proxy_bloquea_crear_propuesta_sin_verificar(self, facade):
        """CP-18: Ciudadano no verificado no puede crear propuesta."""
        citizen = facade.register_citizen("Bob", "bob@test.com", "9876543210987", "pass")
        assert citizen.verified is False
        with pytest.raises(PermissionError, match="no está verificado"):
            facade.create_proposal(citizen.citizen_id, "Título", "Desc", "Cuerpo")


# ===========================================================================
# MÓDULO 3: COMPOSITE — Estructura del Documento
# ===========================================================================

class TestComposite:

    def test_CP09_renderizado_arbol_composite(self, active_proposal):
        """CP-09: El árbol Composite renderiza correctamente todos los nodos."""
        doc = ProposalDocument.build_from_proposal(active_proposal)
        rendered = doc.render()
        assert "Ley de Prueba" in rendered
        assert "ENCABEZADO" in rendered
        assert "CUERPO NORMATIVO" in rendered
        assert "REGISTRO DE FIRMAS" in rendered

    def test_CP10_conteo_nodos_composite(self, active_proposal):
        """CP-10: El árbol Composite cuenta correctamente el total de nodos."""
        doc = ProposalDocument.build_from_proposal(active_proposal)
        total = doc.count()
        # Raíz + Encabezado(1+4 hojas) + Cuerpo(1+1 hoja) + Firmas(1+1 hoja) + Anexos(1)
        assert total >= 6

    def test_composite_hoja_es_nodo_simple(self):
        """Una ProposalLeaf siempre cuenta como 1 nodo."""
        leaf = ProposalLeaf("Título", "Contenido de prueba")
        assert leaf.count() == 1
        assert "Contenido de prueba" in leaf.render()
        assert leaf.get_content() == "Contenido de prueba"

    def test_composite_seccion_acumula_hijos(self):
        """Una ProposalSection cuenta sus hijos recursivamente."""
        section = ProposalSection("Sección Principal")
        section.add(ProposalLeaf("Hoja 1", "A"))
        section.add(ProposalLeaf("Hoja 2", "B"))
        subsection = ProposalSection("Subsección")
        subsection.add(ProposalLeaf("Hoja 3", "C"))
        section.add(subsection)
        # 1 (sección) + 2 hojas + 1 subsección + 1 hoja = 5
        assert section.count() == 5


# ===========================================================================
# MÓDULO 4: DECORATOR — Adición Dinámica de Elementos
# ===========================================================================

class TestDecorator:

    def test_CP11_añadir_comentario(self, active_proposal):
        """CP-11: CommentDecorator registra el comentario correctamente."""
        decorable = BaseProposalDecorable(active_proposal)
        CommentDecorator(decorable, author="Juan Pérez", text="Apoyo esta iniciativa.")
        assert len(active_proposal.comments) == 1
        assert active_proposal.comments[0].author == "Juan Pérez"
        assert active_proposal.comments[0].text == "Apoyo esta iniciativa."

    def test_CP12_añadir_recurso(self, active_proposal):
        """CP-12: ResourceDecorator registra el recurso con título y URL."""
        decorable = BaseProposalDecorable(active_proposal)
        ResourceDecorator(decorable, title="Estudio ONU", url="https://un.org/doc")
        assert len(active_proposal.resources) == 1
        assert active_proposal.resources[0].title == "Estudio ONU"
        assert active_proposal.resources[0].url == "https://un.org/doc"

    def test_CP13_añadir_modificacion(self, citizen_verified, active_proposal):
        """CP-13: ModificationDecorator registra la modificación del proponente."""
        decorable = BaseProposalDecorable(active_proposal)
        ModificationDecorator(
            decorable,
            description="Cambio artículo 1",
            new_text="Texto modificado del artículo.",
            requestor_id=citizen_verified.citizen_id,
        )
        assert len(active_proposal.modifications) == 1
        assert active_proposal.modifications[0].description == "Cambio artículo 1"

    def test_CP14_encadenamiento_multiples_decorators(self, citizen_verified, active_proposal):
        """CP-14: Se pueden encadenar Comment + Resource + Modification en secuencia."""
        decorable = BaseProposalDecorable(active_proposal)
        CommentDecorator(decorable, author="Ana", text="Comentario de prueba.")
        ResourceDecorator(decorable, title="Recurso", url="https://ejemplo.com")
        ModificationDecorator(
            decorable,
            description="Enmienda 1",
            new_text="Nuevo texto.",
            requestor_id=citizen_verified.citizen_id,
        )
        assert len(active_proposal.comments) == 1
        assert len(active_proposal.resources) == 1
        assert len(active_proposal.modifications) == 1

    def test_decorator_rechaza_url_invalida(self, active_proposal):
        """ResourceDecorator lanza ValueError si la URL no comienza con http/https."""
        decorable = BaseProposalDecorable(active_proposal)
        with pytest.raises(ValueError, match="URL"):
            ResourceDecorator(decorable, title="Doc", url="ftp://invalido.com")

    def test_decorator_rechaza_modificacion_no_proponente(self, active_proposal):
        """ModificationDecorator lanza PermissionError si no es el proponente."""
        decorable = BaseProposalDecorable(active_proposal)
        with pytest.raises(PermissionError, match="proponente"):
            ModificationDecorator(
                decorable,
                description="Intento",
                new_text="Texto.",
                requestor_id=999,   # ID que no es el proponente
            )


# ===========================================================================
# MÓDULO 5: FACADE — Flujo Completo
# ===========================================================================

class TestFacade:

    def test_CP15_crear_propuesta_via_facade(self, facade):
        """CP-15: Facade crea propuesta con estado ACTIVA y 0 firmas."""
        citizen = facade.register_citizen("Ana", "ana@test.com", "1234567890101", "pass")
        facade.verify_citizen(citizen.citizen_id)
        proposal = facade.create_proposal(
            citizen.citizen_id, "Ley de Prueba", "Desc", "Cuerpo legal."
        )
        assert proposal.status == ProposalStatus.ACTIVE
        assert proposal.signature_count == 0
        assert proposal.proposal_id == 1

    def test_CP16_congelamiento_automatico_al_alcanzar_25000(self, facade):
        """CP-16: Al firma 25,000 la propuesta se congela con hash SHA-256."""
        proposer = facade.register_citizen("Ana", "ana@test.com", "1234567890101", "pass")
        facade.verify_citizen(proposer.citizen_id)
        proposal = facade.create_proposal(
            proposer.citizen_id, "Ley de Límite", "Desc", "Cuerpo."
        )

        # Inyectamos 24,999 firmas directamente (simula el proceso)
        from src.models.signature import Signature
        for i in range(24999):
            fake_sig = Signature(
                signature_id=i + 1,
                citizen_id=1000 + i,
                proposal_id=proposal.proposal_id,
                citizen_hash=f"hash_{i}",
            )
            proposal.signatures.append(fake_sig)

        assert proposal.signature_count == 24999
        assert proposal.status == ProposalStatus.ACTIVE

        # La firma 25,000 la hace un ciudadano verificado real
        signer = facade.register_citizen("Carlos", "carlos@test.com", "9876543210987", "pass")
        facade.verify_citizen(signer.citizen_id)
        facade.sign_proposal(signer.citizen_id, proposal.proposal_id)

        assert proposal.signature_count == 25000
        assert proposal.status == ProposalStatus.SENT
        assert proposal.crypto_hash is not None
        assert len(proposal.crypto_hash) == 64   # SHA-256 → 64 hex chars

    def test_CP17_envio_al_congreso_tras_congelamiento(self, facade):
        """CP-17: Registro de envío creado correctamente tras congelar."""
        proposer = facade.register_citizen("Ana", "ana@test.com", "1234567890101", "pass")
        facade.verify_citizen(proposer.citizen_id)
        proposal = facade.create_proposal(
            proposer.citizen_id, "Ley Envío", "Desc", "Cuerpo."
        )

        from src.models.signature import Signature
        for i in range(24999):
            proposal.signatures.append(
                Signature(i + 1, 1000 + i, proposal.proposal_id, f"hash_{i}")
            )

        signer = facade.register_citizen("Carlos", "carlos@test.com", "9876543210987", "pass")
        facade.verify_citizen(signer.citizen_id)
        facade.sign_proposal(signer.citizen_id, proposal.proposal_id)

        submissions = facade.get_congress_submissions()
        assert len(submissions) == 1
        assert submissions[0]["proposal_id"] == proposal.proposal_id
        assert submissions[0]["status"] == "ENVIADO"
        assert len(submissions[0]["crypto_hash"]) == 64
