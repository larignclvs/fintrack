class EntidadeNaoEncontradaError(Exception):
    """Erro lançado quando uma entidade não é encontrada no banco."""
    pass


class ValidacaoError(Exception):
    """Erro lançado quando alguma regra de validação de negócio falha."""
    pass