from enum import Enum

class PrioridadeEnum(str, Enum):
    novo_contato = "novo_contato"
    em_atendimento = "em_atendimento"
    proposta_enviada = "proposta_enviada"
    negociacao = "negociacao"
    fechado = "fechado"

class CargosEnum(str, Enum):
    funcionario = 'funcionario'
    admin = 'admin'

class TiposInteracoesEnum(str, Enum):
    email = 'email'
    ligacao = 'ligacao'
    mensagens = 'mensagens'