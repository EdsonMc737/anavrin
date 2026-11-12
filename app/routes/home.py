
import json
from pathlib import Path

from flask import Blueprint, abort, current_app, render_template


home_bp = Blueprint("home", __name__)


# ==================================================
# CARREGAMENTO DOS DADOS
# ==================================================

def carregar_terapeutas():
    arquivo_json = (
        Path(current_app.root_path)
        / "data"
        / "terapeutas.json"
    )

    with open(arquivo_json, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados


def terapeutas_ativas(dados):
    """
    Retorna somente terapeutas ativas.

    Cadastros antigos sem o campo 'ativo'
    continuam ativos por padrão.
    """
    return [
        terapeuta
        for terapeuta in dados.get("terapeutas", [])
        if terapeuta.get("ativo", True)
    ]


def carregar_catalogo_atendimentos():
    dados = carregar_terapeutas()
    return dados.get("catalogo_atendimentos", [])


def carregar_ensaios():
    arquivo_json = (
        Path(current_app.root_path)
        / "data"
        / "ensaios_terapeutas.json"
    )

    with open(arquivo_json, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados.get("ensaios", [])


# ==================================================
# CARREGAMENTO AUTOMÁTICO DAS FOTOS DO ENSAIO
# ==================================================

def carregar_fotografias_ensaio(terapeuta):

    foto_principal = (
        terapeuta.get("foto_perfil")
        or terapeuta.get("foto_apresentacao")
        or ""
    )

    if not foto_principal:
        return []

    caminho_foto = Path(foto_principal)
    partes = caminho_foto.parts

    if (
        len(partes) < 3
        or partes[0] != "img"
        or partes[1] != "terapeutas"
    ):
        return []

    pasta_terapeuta = partes[2]

    pasta_ensaio = (
        Path(current_app.static_folder)
        / "img"
        / "terapeutas"
        / pasta_terapeuta
        / "ensaio"
    )

    fotografias = []

    extensoes = {".jpg", ".jpeg", ".png", ".webp"}

    if not pasta_ensaio.exists() or not pasta_ensaio.is_dir():
        return []

    arquivos = sorted(
        [
            arquivo
            for arquivo in pasta_ensaio.iterdir()
            if (
                arquivo.is_file()
                and arquivo.suffix.lower() in extensoes
            )
        ],
        key=lambda arquivo: arquivo.name.lower(),
    )

    for ordem, arquivo in enumerate(arquivos, start=1):

        fotografias.append(
            {
                "foto": (
                    f"img/terapeutas/{pasta_terapeuta}"
                    f"/ensaio/{arquivo.name}"
                ),
                "descricao": (
                    arquivo.stem
                    .replace("_", " ")
                    .replace("-", " ")
                    .title()
                ),
                "ordem": ordem,
            }
        )

    return fotografias


# ==================================================
# PÁGINA INICIAL
# ==================================================

@home_bp.route("/")
def home_index():

    dados = carregar_terapeutas()

    terapeutas = terapeutas_ativas(dados)

    return render_template(
        "pages/index.html",
        title="Home Page",
        terapeutas=terapeutas,
    )


# ==================================================
# PÁGINA DE TODAS AS TERAPEUTAS
# ==================================================

@home_bp.route("/terapeutas")
def terapeutas_pro():

    dados = carregar_terapeutas()

    terapeutas = terapeutas_ativas(dados)

    catalogo_atendimentos = dados.get(
        "catalogo_atendimentos",
        [],
    )

    return render_template(
        "pages/profissionais.html",
        title="Nossas Profissionais",
        terapeutas=terapeutas,
        catalogo_atendimentos=catalogo_atendimentos,
    )


# ==================================================
# PERFIL INDIVIDUAL DA TERAPEUTA
# ==================================================

@home_bp.route("/terapeutas/<string:terapeuta_id>")
def perfil_terapeuta(terapeuta_id):

    dados = carregar_terapeutas()

    terapeutas = terapeutas_ativas(dados)

    terapeuta = next(
        (
            item
            for item in terapeutas
            if item.get("id") == terapeuta_id
        ),
        None,
    )

    # Terapeuta inexistente ou desativada
    if terapeuta is None:
        abort(404)

    ensaios = carregar_ensaios()

    ensaio = next(
        (
            item
            for item in ensaios
            if (
                item.get("id") == terapeuta.get("ensaio_id")
                and item.get("terapeuta_id") == terapeuta_id
            )
        ),
        None,
    )

    fotografias = carregar_fotografias_ensaio(terapeuta)

    # Outras terapeutas: somente as ativas
    outras_terapeutas = [
        item
        for item in terapeutas
        if item.get("id") != terapeuta_id
    ]

    return render_template(
        "pages/perfil_terapeuta.html",
        title=terapeuta.get(
            "nome",
            "Perfil da terapeuta",
        ),
        terapeuta=terapeuta,
        ensaio=ensaio,
        fotografias=fotografias,
        outras_terapeutas=outras_terapeutas,
        catalogo_atendimentos=dados.get(
            "catalogo_atendimentos",
            [],
        ),
    )


# ==================================================
# PÁGINA DE MASSAGENS E EXPERIÊNCIAS
# ==================================================

@home_bp.route("/massagens")
def massagens():

    dados = carregar_terapeutas()

    catalogo_atendimentos = dados.get(
        "catalogo_atendimentos",
        [],
    )

    # Somente terapeutas ativas
    terapeutas = terapeutas_ativas(dados)

    terapeutas_por_atendimento = {}

    for atendimento in catalogo_atendimentos:

        terapeutas_por_atendimento[atendimento] = [
            terapeuta
            for terapeuta in terapeutas
            if atendimento in (
                terapeuta.get("tipos_atendimento") or []
            )
        ]

    return render_template(
        "pages/massagens.html",
        title="Massagens e Experiências | Anavrin",
        catalogo_atendimentos=catalogo_atendimentos,
        terapeutas=terapeutas,
        terapeutas_por_atendimento=terapeutas_por_atendimento,
    )


# ==================================================
# PÁGINA DE UNIDADES
# ==================================================

@home_bp.route("/unidades")
def unidades():

    dados = carregar_terapeutas()

    outras_terapeutas = terapeutas_ativas(dados)

    return render_template(
        "pages/unidades.html",
        title="Nossas Unidades | Anavrin",
        outras_terapeutas=outras_terapeutas,
    )
