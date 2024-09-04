"""
Este módulo contém classes para modelar um sistema bancário simples, incluindo
clientes, contas, transações e históricos de transações.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    """
    Classe que representa um cliente.
    """

    def __init__(self, endereco):
        """
        Inicializa um cliente com um endereço e uma lista de contas.
        """
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        """
        Realiza uma transação em uma conta específica.
        """
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """
        Adiciona uma conta à lista de contas do cliente.
        """
        self.contas.append(conta)

class PessoaFisica(Cliente):
    """
    Classe que representa um cliente pessoa física.
    """

    def __init__(self, nome, data_nascimento, cpf, endereco):
        """
        Inicializa uma pessoa física com nome, data de nascimento, CPF e endereço.
        """
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    """
    Classe que representa uma conta bancária.
    """

    AGENCIA_PADRAO = "0001"

    def __init__(self, numero, cliente):
        """
        Inicializa uma conta com número, cliente associado, agência, saldo e histórico.
        """
        self._saldo = 0
        self._numero = numero
        self._agencia = self.AGENCIA_PADRAO
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        """
        Cria uma nova conta associada a um cliente e número de conta.
        """
        return cls(numero, cliente)

    @property
    def saldo(self):
        """
        Retorna o saldo atual da conta.
        """
        return self._saldo

    @property
    def numero(self):
        """
        Retorna o número da conta.
        """
        return self._numero

    @property
    def agencia(self):
        """
        Retorna o número da agência.
        """
        return self._agencia

    @property
    def cliente(self):
        """
        Retorna o cliente associado à conta.
        """
        return self._cliente

    @property
    def historico(self):
        """
        Retorna o histórico de transações da conta.
        """
        return self._historico

    def sacar(self, valor):
        """
        Realiza um saque na conta, verificando se há saldo suficiente.
        """
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        """
        Realiza um depósito na conta.
        """
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

class ContaCorrente(Conta):
    """
    Classe que representa uma conta corrente, com um limite máximo de valor para cada saque e um número máximo de saques permitidos por dia.
    """

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        """
        Inicializa uma conta corrente com número, cliente, limite e limite de saques.
        """
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        """
        Realiza um saque na conta corrente, verificando limites e número de saques.
        """
        numero_saques = sum(1 for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__)

        if valor > self.limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if numero_saques >= self.limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        """
        Retorna uma representação em string da conta corrente.
        """
        return (
            f"Agência:\t{self.agencia}\n"
            f"C/C:\t\t{self.numero}\n"
            f"Titular:\t{self.cliente.nome}\n"
        )

class Historico:
    """
    Classe que representa o histórico de transações de uma conta.
    """

    def __init__(self):
        """
        Inicializa um histórico de transações vazio.
        """
        self._transacoes = []

    @property
    def transacoes(self):
        """
        Retorna a lista de transações realizadas.
        """
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """
        Adiciona uma transação ao histórico.
        """
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    """
    Classe abstrata que representa uma transação.
    """

    @property
    @abstractmethod
    def valor(self):
        """
        Retorna o valor da transação.
        """

    @abstractmethod
    def registrar(self, conta):
        """
        Registra a transação em uma conta específica.
        """

class Saque(Transacao):
    """
    Classe que representa uma transação de saque.
    """

    def __init__(self, valor):
        """
        Inicializa um saque com um valor específico.
        """
        self._valor = valor

    @property
    def valor(self):
        """
        Retorna o valor do saque.
        """
        return self._valor

    def registrar(self, conta):
        """
        Registra o saque na conta, atualizando o saldo e o histórico.
        """
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """
    Classe que representa uma transação de depósito.
    """

    def __init__(self, valor):
        """
        Inicializa um depósito com um valor específico.
        """
        self._valor = valor

    @property
    def valor(self):
        """
        Retorna o valor do depósito.
        """
        return self._valor

    def registrar(self, conta):
        """
        Registra o depósito na conta, atualizando o saldo e o histórico.
        """
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

if __name__ == "__main__":
    # Criar um cliente
    cliente = PessoaFisica(nome="Luca Castro", data_nascimento="29/08/1994", cpf="123.456.789-00", endereco="Rua A, 123")

    # Criar uma conta para o cliente
    conta = ContaCorrente(numero=1001, cliente=cliente)

    # Adicionar a conta ao cliente
    cliente.adicionar_conta(conta)

    # Testar depósito
    conta.depositar(1000)
    print(conta.saldo)  # Deve imprimir 1000

    # Testar saque dentro do limite
    conta.sacar(200)
    print(conta.saldo)  # Deve imprimir 800

    # Testar saque que excede o saldo
    conta.sacar(900)  # Deve falhar e imprimir uma mensagem de erro

    # Testar o limite de saques
    conta.sacar(200)  # Saque 1
    conta.sacar(200)  # Saque 2
    conta.sacar(200)  # Saque 3 - Deve passar
    conta.sacar(200)  # Saque 4 - Deve falhar por excesso de saques

    # Imprimir detalhes da conta
    print(conta)
