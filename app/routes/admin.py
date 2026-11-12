import json
import os
import secrets

from functools import wraps
from pathlib import Path
from threading import RLock

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

json_lock = RLock()


# ==================================================
# CAMINHOS E ARQUIVOS JSON
# ==================================================


def caminho_dados(nome):
    return Path(current_app.root_path) / "data" / nome


def ler_json(nome, padrao=None):
    arquivo = caminho_dados(nome)

    if not arquivo.exists():
        return padrao if padrao is not None else {}

    with json_lock:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)


def salvar_json(nome, dados):
    arquivo = caminho_dados(nome)
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    temporario = arquivo.with_suffix(".tmp")

    with json_lock:
        if arquivo.exists():
            backup = arquivo.with_name(arquivo.stem + ".backup" + arquivo.suffix)
            backup.write_bytes(arquivo.read_bytes())

        try:
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump(
                    dados,
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
                f.flush()
                os.fsync(f.fileno())

            os.replace(temporario, arquivo)

        finally:
            if temporario.exists():
                temporario.unlink()


# ==================================================
# AUTENTICAÇÃO
# ==================================================


def administrador_logado():
    return bool(session.get("admin_id"))


def buscar_administrador_logado():
    admin_id = session.get("admin_id")

    if not admin_id:
        return None

    administradores = ler_json("administradores.json", [])

    if not isinstance(administradores, list):
        return None

    return next(
        (
            admin
            for admin in administradores
            if admin.get("id") == admin_id and admin.get("ativo", True)
        ),
        None,
    )


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        administrador = buscar_administrador_logado()

        if administrador is None:
            session.clear()
            return redirect(url_for("admin.login"))

        return func(*args, **kwargs)

    return wrapper


# ==================================================
# PROTEÇÃO CSRF
# ==================================================


def validar_csrf():
    token_formulario = request.form.get("csrf_token", "")
    token_sessao = session.get("csrf_token", "")

    if (
        not token_formulario
        or not token_sessao
        or not secrets.compare_digest(
            token_formulario,
            token_sessao,
        )
    ):
        abort(400)


@admin_bp.context_processor
def admin_context():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return {
        "csrf_token": session["csrf_token"],
        "admin_nome": session.get("admin_nome"),
    }


# ==================================================
# LOGIN
# ==================================================


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if administrador_logado():
        if buscar_administrador_logado():
            return redirect(url_for("admin.dashboard"))

        session.clear()

    if request.method == "POST":
        validar_csrf()

        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        administradores = ler_json("administradores.json", [])

        if not isinstance(administradores, list):
            administradores = []

        administrador = next(
            (
                item
                for item in administradores
                if item.get("email", "").strip().lower() == email
                and item.get("ativo", True)
            ),
            None,
        )

        senha_valida = False

        if administrador:
            senha_hash = administrador.get("senha_hash", "")

            if senha_hash:
                try:
                    senha_valida = check_password_hash(
                        senha_hash,
                        senha,
                    )
                except (ValueError, TypeError):
                    senha_valida = False

        if administrador and senha_valida:
            session.clear()

            session["admin_id"] = administrador["id"]
            session["admin_nome"] = administrador.get(
                "nome",
                "Administrador",
            )
            session["csrf_token"] = secrets.token_urlsafe(32)

            return redirect(url_for("admin.dashboard"))

        flash("E-mail ou senha incorretos.", "danger")

    return render_template("admin/login.html")


# ==================================================
# SAIR
# ==================================================


@admin_bp.route("/logout", methods=["POST"])
@login_obrigatorio
def logout():
    validar_csrf()
    session.clear()

    return redirect(url_for("admin.login"))


# ==================================================
# DASHBOARD
# ==================================================


@admin_bp.route("/")
@login_obrigatorio
def dashboard():
    dados = ler_json("terapeutas.json", {})
    terapeutas = dados.get("terapeutas", [])

    ativas = [terapeuta for terapeuta in terapeutas if terapeuta.get("ativo", True)]

    inativas = [
        terapeuta for terapeuta in terapeutas if not terapeuta.get("ativo", True)
    ]

    arquivadas = ler_json("terapeutas_arquivadas.json", [])

    return render_template(
        "admin/dashboard.html",
        total=len(terapeutas),
        ativas=len(ativas),
        inativas=len(inativas),
        arquivadas=len(arquivadas),
    )


# ==================================================
# LISTAGEM DE TERAPEUTAS
# ==================================================


@admin_bp.route("/terapeutas")
@login_obrigatorio
def terapeutas():
    dados = ler_json("terapeutas.json", {})
    lista = dados.get("terapeutas", [])

    return render_template(
        "admin/terapeutas.html",
        terapeutas=lista,
    )


# ==================================================
# ATIVAR / DESATIVAR TERAPEUTA
# ==================================================


@admin_bp.route(
    "/terapeutas/<string:terapeuta_id>/alternar",
    methods=["POST"],
)
@login_obrigatorio
def alternar_terapeuta(terapeuta_id):
    validar_csrf()

    dados = ler_json("terapeutas.json", {})
    lista = dados.get("terapeutas", [])

    terapeuta = next(
        (item for item in lista if item.get("id") == terapeuta_id),
        None,
    )

    if terapeuta is None:
        abort(404)

    terapeuta["ativo"] = not terapeuta.get("ativo", True)

    salvar_json("terapeutas.json", dados)

    flash("Status da terapeuta atualizado.", "success")

    return redirect(url_for("admin.terapeutas"))


# ==================================================
# ARQUIVAR TERAPEUTA
# ==================================================


@admin_bp.route(
    "/terapeutas/<string:terapeuta_id>/arquivar",
    methods=["POST"],
)
@login_obrigatorio
def arquivar_terapeuta(terapeuta_id):
    validar_csrf()

    dados = ler_json("terapeutas.json", {})
    lista = dados.get("terapeutas", [])

    terapeuta = next(
        (item for item in lista if item.get("id") == terapeuta_id),
        None,
    )

    if terapeuta is None:
        abort(404)

    arquivadas = ler_json("terapeutas_arquivadas.json", [])

    if not isinstance(arquivadas, list):
        abort(500)

    if any(item.get("id") == terapeuta_id for item in arquivadas):
        abort(409)

    terapeuta["ativo"] = False

    novas_arquivadas = arquivadas + [terapeuta]

    novos_dados = dict(dados)
    novos_dados["terapeutas"] = [
        item for item in lista if item.get("id") != terapeuta_id
    ]

    # Primeiro salva o arquivo de arquivo.
    # Depois remove a terapeuta da lista principal.
    salvar_json("terapeutas_arquivadas.json", novas_arquivadas)
    salvar_json("terapeutas.json", novos_dados)

    flash("Terapeuta arquivada com sucesso.", "success")

    return redirect(url_for("admin.terapeutas"))


# ==================================================
# LISTAGEM DE TERAPEUTAS ARQUIVADAS
# ==================================================


@admin_bp.route("/terapeutas/arquivadas")
@login_obrigatorio
def terapeutas_arquivadas():
    arquivadas = ler_json("terapeutas_arquivadas.json", [])

    if not isinstance(arquivadas, list):
        abort(500)

    return render_template(
        "admin/terapeutas_arquivadas.html",
        terapeutas=arquivadas,
    )


# ==================================================
# REATIVAR TERAPEUTA ARQUIVADA
# ==================================================


@admin_bp.route(
    "/terapeutas/<string:terapeuta_id>/reativar",
    methods=["POST"],
)
@login_obrigatorio
def reativar_terapeuta(terapeuta_id):
    validar_csrf()

    dados = ler_json("terapeutas.json", {})
    arquivadas = ler_json("terapeutas_arquivadas.json", [])

    if not isinstance(dados, dict):
        abort(500)

    if not isinstance(arquivadas, list):
        abort(500)

    lista = dados.get("terapeutas", [])

    if not isinstance(lista, list):
        abort(500)

    # Procura a terapeuta no arquivo de arquivadas.
    terapeuta = next(
        (item for item in arquivadas if item.get("id") == terapeuta_id),
        None,
    )

    if terapeuta is None:
        abort(404)

    # Impede que a mesma terapeuta seja cadastrada duas vezes.
    if any(item.get("id") == terapeuta_id for item in lista):
        abort(409)

    # Reativa a terapeuta preservando todos os seus dados.
    terapeuta["ativo"] = True

    novos_dados = dict(dados)
    novos_dados["terapeutas"] = lista + [terapeuta]

    novas_arquivadas = [item for item in arquivadas if item.get("id") != terapeuta_id]

    # Primeiro salva na equipe principal.
    # Depois remove do arquivo de arquivadas.
    salvar_json("terapeutas.json", novos_dados)
    salvar_json("terapeutas_arquivadas.json", novas_arquivadas)

    flash("Terapeuta reativada com sucesso!", "success")

    return redirect(url_for("admin.terapeutas_arquivadas"))
