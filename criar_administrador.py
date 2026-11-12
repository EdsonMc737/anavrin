
import json
import uuid

from pathlib import Path
from getpass import getpass

from werkzeug.security import generate_password_hash


arquivo = (
    Path(__file__).parent
    / "app"
    / "data"
    / "administradores.json"
)

arquivo.parent.mkdir(
    parents=True,
    exist_ok=True
)

if arquivo.exists():
    with open(arquivo, "r", encoding="utf-8") as f:
        administradores = json.load(f)
else:
    administradores = []

nome = input("Nome do administrador: ").strip()
email = input("E-mail: ").strip().lower()
senha = getpass("Senha: ")
confirmacao = getpass("Confirme a senha: ")

if not nome or not email:
    raise SystemExit("Nome e e-mail são obrigatórios.")

if senha != confirmacao:
    raise SystemExit("As senhas não coincidem.")

if len(senha) < 12:
    raise SystemExit("Use uma senha com pelo menos 12 caracteres.")

if any(a["email"].lower() == email for a in administradores):
    raise SystemExit("Este e-mail já está cadastrado.")

administradores.append({
    "id": "ADM-" + uuid.uuid4().hex[:8].upper(),
    "nome": nome,
    "email": email,
    "senha_hash": generate_password_hash(senha),
    "ativo": True
})

temporario = arquivo.with_suffix(".tmp")

with open(temporario, "w", encoding="utf-8") as f:
    json.dump(
        administradores,
        f,
        ensure_ascii=False,
        indent=2
    )

temporario.replace(arquivo)

print("Administrador cadastrado com sucesso!")
