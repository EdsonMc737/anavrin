
from app.extensions import db


class Terapeuta(db.Model):
    __tablename__ = "terapeutas"

    id = db.Column(db.String(50), primary_key=True)
    status_equipe = db.Column(db.String(100), nullable=True)
    foto_apresentacao = db.Column(db.String(255), nullable=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    nome = db.Column(db.String(150), nullable=False)
    signo = db.Column(db.String(50), nullable=True)
    unidade = db.Column(db.String(100), nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    experiencia = db.Column(db.String(100), nullable=True)
    tipos_atendimento = db.Column(db.JSON, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def get(self, chave, padrao=None):
        return getattr(self, chave, padrao)


class Administrador(db.Model):
    __tablename__ = "administradores"

    id = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    senha_hash = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def get(self, chave, padrao=None):
        return getattr(self, chave, padrao)


class TerapeutaArquivada(db.Model):
    __tablename__ = "terapeutas_arquivadas"

    id = db.Column(db.String(50), primary_key=True)
    status_equipe = db.Column(db.String(100), nullable=True)
    foto_apresentacao = db.Column(db.String(255), nullable=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    nome = db.Column(db.String(150), nullable=False)
    signo = db.Column(db.String(50), nullable=True)
    unidade = db.Column(db.String(100), nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    experiencia = db.Column(db.String(100), nullable=True)
    tipos_atendimento = db.Column(db.JSON, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=False)

    def get(self, chave, padrao=None):
        return getattr(self, chave, padrao)


class Ensaio(db.Model):
    __tablename__ = "ensaios"

    chave = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(50), nullable=False)
    terapeuta_id = db.Column(
        db.String(50),
        db.ForeignKey("terapeutas.id"),
        nullable=False
    )
    nome = db.Column(db.String(150), nullable=False)
    fotografias = db.Column(db.JSON, nullable=False)


class CatalogoAtendimento(db.Model):
    __tablename__ = "catalogo_atendimentos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ordem = db.Column(db.Integer, nullable=False, unique=True)
    valor = db.Column(db.String(150), nullable=False, unique=True)


class StatusEquipe(db.Model):
    __tablename__ = "status_equipe"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ordem = db.Column(db.Integer, nullable=False, unique=True)
    valor = db.Column(db.String(100), nullable=False, unique=True)

