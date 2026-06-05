"""
Aplicación Flask — Voz del Ciudadano
Pantalla 1: Dashboard (listado de propuestas)
Pantalla 2: Detalle de propuesta (documento, firmas, comentarios, recursos)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from src.patterns.facade import ProposalFacade

app = Flask(__name__)
app.secret_key = "voz-ciudadano-secret-2026"

# ---------------------------------------------------------------------------
# Instancia global de la Facade (en producción sería por sesión / DB)
# ---------------------------------------------------------------------------
facade = ProposalFacade(id_provider="registro_civil")


def _seed_demo_data():
    """Carga datos de demostración para mostrar el sistema funcionando."""

    # Ciudadanos de demo
    ana = facade.register_citizen("Ana López", "ana@demo.com", "1234567890101", "pass123")
    facade.verify_citizen(ana.citizen_id)

    carlos = facade.register_citizen("Carlos Méndez", "carlos@demo.com", "9876543210987", "pass123")
    facade.verify_citizen(carlos.citizen_id)

    maria = facade.register_citizen("María García", "maria@demo.com", "1122334455667", "pass123")
    facade.verify_citizen(maria.citizen_id)

    # Propuesta 1: activa con algunas firmas
    p1 = facade.create_proposal(
        citizen_id=ana.citizen_id,
        title="Ley de Transparencia en el Uso de Fondos Públicos",
        description=(
            "Propuesta para obligar a todas las instituciones del Estado a publicar "
            "en tiempo real el detalle de cada gasto con cargo al presupuesto nacional."
        ),
        body=(
            "ARTÍCULO 1. Toda institución del Estado deberá publicar mensualmente "
            "un informe detallado de sus gastos en el portal de transparencia nacional.\n\n"
            "ARTÍCULO 2. Los informes deberán incluir: monto, beneficiario, fecha, "
            "número de contrato y partida presupuestaria correspondiente.\n\n"
            "ARTÍCULO 3. El incumplimiento de esta ley será sancionado conforme "
            "al Código Penal en su artículo 418."
        ),
    )
    facade.sign_proposal(carlos.citizen_id, p1.proposal_id)
    facade.sign_proposal(maria.citizen_id, p1.proposal_id)
    facade.add_comment(p1.proposal_id, "Carlos Méndez", "Esta ley es fundamental para combatir la corrupción.")
    facade.add_resource(p1.proposal_id, "Estudio OCDE sobre Transparencia", "https://www.oecd.org/gov/ethics/")
    facade.add_modification(
        p1.proposal_id, ana.citizen_id,
        "Ampliación del artículo 2",
        "Se añade la obligación de publicar también los contratos de obra pública."
    )

    # Propuesta 2: activa sin firmas aún
    p2 = facade.create_proposal(
        citizen_id=carlos.citizen_id,
        title="Reducción del IVA a Productos de la Canasta Básica",
        description=(
            "Iniciativa para eliminar el Impuesto al Valor Agregado sobre los "
            "alimentos de la canasta básica familiar, beneficiando a los hogares "
            "de menores ingresos."
        ),
        body=(
            "ARTÍCULO 1. Se exonera del Impuesto al Valor Agregado (IVA) a los "
            "productos incluidos en la canasta básica familiar según el listado "
            "oficial del Ministerio de Economía.\n\n"
            "ARTÍCULO 2. El Ministerio de Economía actualizará dicho listado "
            "semestralmente, tomando en cuenta variaciones en el costo de vida.\n\n"
            "ARTÍCULO 3. La presente ley entra en vigencia a los 30 días "
            "de su publicación en el Diario Oficial."
        ),
    )
    facade.sign_proposal(ana.citizen_id, p2.proposal_id)
    facade.add_comment(p2.proposal_id, "Ana López", "Apoyamos esta propuesta desde nuestra asociación vecinal.")
    facade.add_resource(p2.proposal_id, "Informe de Pobreza 2025 — INE", "https://www.ine.gob.gt/estadistica/")

    return ana, carlos, maria


# Carga los datos al iniciar
_citizen_ana, _citizen_carlos, _citizen_maria = _seed_demo_data()

# ---------------------------------------------------------------------------
# PANTALLA 1: DASHBOARD — listado de propuestas
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    proposals = facade.get_all_proposals()
    return render_template("dashboard.html", proposals=proposals)


# ---------------------------------------------------------------------------
# PANTALLA 2: DETALLE DE PROPUESTA
# ---------------------------------------------------------------------------

@app.route("/proposal/<int:proposal_id>")
def proposal_detail(proposal_id):
    try:
        proposal = facade.get_proposal(proposal_id)
        document = facade.get_proposal_document(proposal_id)
        return render_template(
            "proposal_detail.html",
            proposal=proposal,
            document=document,
        )
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# ACCIÓN: FIRMAR PROPUESTA
# ---------------------------------------------------------------------------

@app.route("/proposal/<int:proposal_id>/sign", methods=["POST"])
def sign_proposal(proposal_id):
    citizen_id = int(request.form.get("citizen_id", 0))
    try:
        facade.sign_proposal(citizen_id, proposal_id)
        flash("¡Firma registrada exitosamente!", "success")
    except (PermissionError, ValueError) as e:
        flash(str(e), "danger")
    return redirect(url_for("proposal_detail", proposal_id=proposal_id))


# ---------------------------------------------------------------------------
# ACCIÓN: AÑADIR COMENTARIO
# ---------------------------------------------------------------------------

@app.route("/proposal/<int:proposal_id>/comment", methods=["POST"])
def add_comment(proposal_id):
    author = request.form.get("author", "").strip()
    text = request.form.get("text", "").strip()
    try:
        facade.add_comment(proposal_id, author, text)
        flash("Comentario añadido correctamente.", "success")
    except (ValueError, PermissionError) as e:
        flash(str(e), "danger")
    return redirect(url_for("proposal_detail", proposal_id=proposal_id))


# ---------------------------------------------------------------------------
# ACCIÓN: AÑADIR RECURSO
# ---------------------------------------------------------------------------

@app.route("/proposal/<int:proposal_id>/resource", methods=["POST"])
def add_resource(proposal_id):
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    try:
        facade.add_resource(proposal_id, title, url)
        flash("Recurso de apoyo añadido correctamente.", "success")
    except (ValueError, PermissionError) as e:
        flash(str(e), "danger")
    return redirect(url_for("proposal_detail", proposal_id=proposal_id))


if __name__ == "__main__":
    app.run(debug=True)
