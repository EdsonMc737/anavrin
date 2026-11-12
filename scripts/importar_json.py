import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models import (
    Administrador,
    Terapeuta,
    TerapeutaArquivada,
    Ensaio,
    CatalogoAtendimento,
    StatusEquipe,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "app" / "data"


def carregar_json(nome):
    caminho = DATA_DIR / nome

    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def importar():
    administradores = carregar_json("administradores.json")

    dados_terapeutas = carregar_json("terapeutas.json")
    terapeutas = dados_terapeutas["terapeutas"]

    arquivadas = carregar_json("terapeutas_arquivadas.json")

    dados_ensaios = carregar_json("ensaios_terapeutas.json")
    ensaios = dados_ensaios["ensaios"]

    catalogo = dados_terapeutas["catalogo_atendimentos"]
    status = dados_terapeutas["status_equipe_disponiveis"]

    tabelas = [
        Administrador,
        Terapeuta,
        TerapeutaArquivada,
        Ensaio,
        CatalogoAtendimento,
        StatusEquipe,
    ]

    with db.session.begin():
        for modelo in tabelas:
            quantidade = db.session.query(modelo).count()

            if quantidade != 0:
                raise RuntimeError(
                    f"A tabela {modelo.__tablename__} "
                    f"não está vazia. Importação cancelada."
                )

        db.session.add_all(
            [
                Administrador(
                    id=item["id"],
                    nome=item["nome"],
                    email=item["email"],
                    senha_hash=item["senha_hash"],
                    ativo=item.get("ativo", True),
                )
                for item in administradores
            ]
        )

        db.session.add_all(
            [
                Terapeuta(
                    id=item["id"],
                    status_equipe=item.get("status_equipe"),
                    foto_apresentacao=item.get("foto_apresentacao"),
                    foto_perfil=item.get("foto_perfil"),
                    nome=item["nome"],
                    signo=item.get("signo"),
                    unidade=item.get("unidade"),
                    idade=item.get("idade"),
                    experiencia=item.get("experiencia"),
                    tipos_atendimento=item["tipos_atendimento"],
                    ativo=item.get("ativo", True),
                )
                for item in terapeutas
            ]
        )

        # Garante que os terapeutas existam antes dos ensaios.
        db.session.flush()

        db.session.add_all(
            [
                TerapeutaArquivada(
                    id=item["id"],
                    status_equipe=item.get("status_equipe"),
                    foto_apresentacao=item.get("foto_apresentacao"),
                    foto_perfil=item.get("foto_perfil"),
                    nome=item["nome"],
                    signo=item.get("signo"),
                    unidade=item.get("unidade"),
                    idade=item.get("idade"),
                    experiencia=item.get("experiencia"),
                    tipos_atendimento=item["tipos_atendimento"],
                    ativo=item.get("ativo", False),
                )
                for item in arquivadas
            ]
        )

        db.session.add_all(
            [
                Ensaio(
                    id=item["id"],
                    terapeuta_id=item["terapeuta_id"],
                    nome=item["nome"],
                    fotografias=item["fotografias"],
                )
                for item in ensaios
            ]
        )

        db.session.add_all(
            [
                CatalogoAtendimento(ordem=i, valor=valor)
                for i, valor in enumerate(catalogo, start=1)
            ]
        )

        db.session.add_all(
            [
                StatusEquipe(ordem=i, valor=valor)
                for i, valor in enumerate(status, start=1)
            ]
        )

    print("\nIMPORTAÇÃO CONCLUÍDA!")
    print("Registros gravados:")

    for modelo in tabelas:
        quantidade = db.session.query(modelo).count()
        print(f"{modelo.__tablename__}: {quantidade}")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        importar()
