from datetime import date as date_type
from typing import List, Optional

from src.models.transaction import Transaction
from src.repositories.transaction_repo import TransactionRepository
from src.repositories.user_repo import UserRepository
from src.repositories.category_repo import CategoryRepository
from src.services.exceptions import EntidadeNaoEncontradaError, ValidacaoError
from config.settings import get_setting
from src.utils.logger import get_logger

log = get_logger("TransactionService")


class TransactionService:
    """
    Serviço responsável pelas regras de negócio relacionadas às transações financeiras.
    Inclui validações de entrada, interações entre entidades e regras de limite mensal.
    """

    def __init__(
        self,
        tx_repo: TransactionRepository,
        user_repo: UserRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.tx_repo = tx_repo
        self.user_repo = user_repo
        self.category_repo = category_repo

        # Define o limite mensal de despesas a partir do .env
        limit_str = get_setting("MONTHLY_LIMIT", "2000.0")
        self.monthly_limit = float(limit_str)

    # ==============================
    #     REGRAS AUXILIARES
    # ==============================

    def _validar_user_category(self, user_id: int, category_id: int, tipo_tx: str) -> None:
        """
        Valida se o usuário e a categoria existem e se o tipo da transação é compatível com a categoria.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise EntidadeNaoEncontradaError("Usuário não encontrado.")

        category = self.category_repo.get(category_id)
        if not category:
            raise EntidadeNaoEncontradaError("Categoria não encontrada.")

        # Interação entre entidades: tipo da transação deve coincidir com o tipo da categoria
        if category.type.lower() != tipo_tx.lower():
            raise ValidacaoError("Tipo da transação deve ser igual ao tipo da categoria.")

    def _despesas_do_mes(self, user_id: int, dt: date_type) -> float:
        """
        Calcula o total de despesas do usuário no mês e ano informados.
        """
        txs = self.tx_repo.list_by_user(user_id)
        return sum(
            t.amount
            for t in txs
            if t.type.lower() == "despesa"
            and t.date.year == dt.year
            and t.date.month == dt.month
        )

    # ==============================
    #            CRUD
    # ==============================

    def create_transaction(
        self,
        amount: float,
        date: date_type,
        description: Optional[str],
        type_: str,
        user_id: int,
        category_id: int,
    ) -> Transaction:
        """
        Cria uma nova transação, validando condições de negócio e limites mensais.
        """

        # Validações básicas
        if amount <= 0:
            raise ValidacaoError("Valor da transação deve ser maior que zero.")
        if type_ not in ("Receita", "Despesa"):
            raise ValidacaoError("Tipo deve ser 'Receita' ou 'Despesa'.")

        # Valida entidades e compatibilidade de tipo
        self._validar_user_category(user_id, category_id, type_)

        # Regra de limite mensal (somente para despesas)
        if type_ == "Despesa":
            total_mes = self._despesas_do_mes(user_id, date)
            if total_mes + amount > self.monthly_limit:
                raise ValidacaoError(
                    f"Limite mensal de R$ {self.monthly_limit:.2f} excedido. "
                    f"Total atual: R$ {total_mes:.2f}, tentativa: R$ {amount:.2f}."
                )

        # Cria a transação
        tx = Transaction(
            amount=amount,
            date=date,
            description=description,
            type=type_,
            user_id=user_id,
            category_id=category_id,
        )
        created = self.tx_repo.add(tx)
        log.info(f"Transação criada com sucesso (ID={created.id}, tipo={type_}, valor={amount:.2f}).")
        return created

    def list_transactions(
        self,
        user_id: Optional[int] = None,
        tipo: Optional[str] = None,
        order_by: str = "date",
        order: str = "asc",
    ) -> List[Transaction]:
        """
        Lista as transações com suporte a filtros (usuário, tipo) e ordenação.
        """
        txs = self.tx_repo.list_all()

        if user_id is not None:
            txs = [t for t in txs if t.user_id == user_id]
        if tipo is not None:
            txs = [t for t in txs if t.type.lower() == tipo.lower()]

        # Ordenação
        reverse = order.lower() == "desc"
        try:
            txs = sorted(txs, key=lambda t: getattr(t, order_by), reverse=reverse)
        except AttributeError:
            raise ValidacaoError(f"Campo '{order_by}' inválido para ordenação.")

        return txs

    def get_transaction(self, tx_id: int) -> Transaction:
        """
        Retorna uma transação específica por ID, ou lança exceção se não encontrada.
        """
        tx = self.tx_repo.get(tx_id)
        if not tx:
            raise EntidadeNaoEncontradaError("Transação não encontrada.")
        return tx

    def update_transaction(
        self,
        tx_id: int,
        amount: Optional[float],
        date: Optional[date_type],
        description: Optional[str],
        type_: Optional[str],
        category_id: Optional[int],
    ) -> Transaction:
        """
        Atualiza uma transação existente, validando valores e integridade das entidades.
        """
        tx = self.get_transaction(tx_id)

        if amount is not None:
            if amount <= 0:
                raise ValidacaoError("Valor da transação deve ser maior que zero.")
            tx.amount = amount

        if date is not None:
            tx.date = date

        if description is not None:
            tx.description = description.strip()

        if type_ is not None:
            if type_ not in ("Receita", "Despesa"):
                raise ValidacaoError("Tipo inválido.")
            tx.type = type_

        if category_id is not None:
            self._validar_user_category(tx.user_id, category_id, tx.type)
            tx.category_id = category_id

        updated = self.tx_repo.update(tx)
        log.info(f"Transação atualizada com sucesso (ID={tx.id}).")
        return updated

    def delete_transaction(self, tx_id: int) -> None:
        """
        Exclui uma transação, lançando exceção caso o ID não exista.
        """
        tx = self.get_transaction(tx_id)
        self.tx_repo.delete(tx)
        log.warning(f"Transação deletada (ID={tx.id}).")
