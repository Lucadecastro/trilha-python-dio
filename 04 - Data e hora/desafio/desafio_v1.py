import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class ContasIterador:
    """
    Iterador para percorrer uma lista de contas bancárias.
    """

    def __init__(self, contas):
        """
        Inicializa o iterador com uma lista de contas.
        """
        self.contas = contas
        self._index = 0

    def __iter__(self):
        """
        Retorna o próprio iterador.
        """
        return self

    def __next__(self):
        """
        Retorna a próxima conta na lista.
        """
        try:
            conta = self.contas[self._index]
            self._index += 1
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
            """
        except IndexError as exc:
            raise StopIteration from exc


class Cliente:
    """
    Representa um cliente de um banco, que pode ter várias contas.
    """

    def __init__(self, endereco):
        """
        Inicializa o cliente com um endereço e uma lista de contas.
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
    Representa uma pessoa física (cliente individual).
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
    Representa uma conta bancária.
    """

    def __init__(self, numero, cliente):
        """
        Inicializa uma conta com número, cliente associado, agência, saldo e histórico.
        """
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
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
        if valor > self.saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
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
    Representa uma conta corrente, com um limite de saque e número máximo de saques permitidos.
    """

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        """
        Inicializa uma conta corrente com número, cliente, limite e limite de saques.
        """
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite=500, limite_saques=3):
        """
        Cria uma nova conta corrente associada a um cliente, número de conta,
        limite de saque e número máximo de saques.
        """
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        """
        Realiza um saque na conta corrente, verificando limites e número de saques.
        """
        # Contando apenas saques bem-sucedidos
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"]
        )

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if numero_saques >= self._limite_saques:
            print(f"\n@@@ Operação falhou! Número máximo de saques ({self._limite_saques}) excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        """
        Retorna uma representação em string da conta corrente.
        """
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    """
    Representa o histórico de transações de uma conta.
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

    def gerar_relatorio(self, tipo_transacao=None):
        """
        Gera um relatório de transações, filtrando por tipo se necessário.
        """
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao


class Transacao(ABC):
    """
    Classe abstrata que define uma transação.
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
    Representa uma transação de saque.
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
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """
    Representa uma transação de depósito.
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
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    """
    Decorador para registrar o horário de execução de uma transação.
    """
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()}")
        return resultado

    return envelope


def menu(exibir_saudacao=False):
    """
    Exibe o menu de opções do sistema bancário. A saudação é exibidas uma única vez quando o sistema inicia.
    """
    if exibir_saudacao:
        print("\nSeja bem-vindo, selecione uma das opções abaixo para seguirmos com seu atendimento!\n")

    menu_box = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [lu]\tListar usuários
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_box))

def validar_cpf(cpf):
    """
    Valida o CPF, garantindo que tenha 11 dígitos numéricos.
    """
    if len(cpf) != 11 or not cpf.isdigit():
        print("\n@@@ CPF inválido! O CPF deve conter 11 dígitos numéricos. @@@")
        return False
    return True

def buscar_cliente(clientes):
    """
    Busca um cliente a partir do CPF fornecido.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return None

    return cliente

def filtrar_cliente(cpf, clientes):
    """
    Filtra e retorna o cliente com o CPF fornecido.
    """
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def obter_valor():
    """
    Solicita o valor de uma transação, garantindo que seja um número positivo.
    """
    try:
        valor = float(input("Informe o valor: "))
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return None
        return valor
    except ValueError:
        print("\n@@@ Operação falhou! Valor inválido, tente novamente. @@@")
        return None


def recuperar_conta_cliente(cliente):
    """
    Recupera a conta do cliente, permitindo escolher se houver mais de uma.
    """
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("\nEscolha a conta:")
    for i, conta in enumerate(cliente.contas):
        print(f"{i} - Agência: {conta.agencia}, Número: {conta.numero}")

    escolha = int(input("Informe o número da conta: "))
    return cliente.contas[escolha]


@log_transacao
def depositar(clientes):
    """
    Realiza um depósito para o cliente identificado pelo CPF e atualiza o saldo e o histórico da conta.
    """
    cliente = buscar_cliente(clientes)
    if not cliente:
        return

    valor = obter_valor()
    if not valor:
        return

    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    """
    Realiza um saque para o cliente identificado pelo CPF e atualiza o saldo e o histórico da conta.
    """
    cliente = buscar_cliente(clientes)
    if not cliente:
        return

    valor = obter_valor()
    if not valor:
        return

    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    """
    Exibe o extrato de transações da conta do cliente, identificando o CPF.
    """
    cliente = buscar_cliente(clientes)
    if not cliente:
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


@log_transacao
def criar_cliente(clientes):
    """
    Cria um novo cliente no sistema, validando o CPF e solicitando os dados pessoais.
    """
    cpf = input("Informe o CPF (somente números): ")
    if not validar_cpf(cpf):
        return

    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    """
    Cria uma nova conta corrente para o cliente identificado pelo CPF.
    """
    cliente = buscar_cliente(clientes)
    if not cliente:
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    """
    Lista todas as contas registradas no sistema.
    """
    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def listar_usuarios(clientes):
    """
    Lista todos os usuários cadastrados no sistema.
    """
    print("\n========== Lista de Usuários ==========")
    for cliente in clientes:
        print(f"Nome: {cliente.nome}, CPF: {cliente.cpf}, Endereço: {cliente.endereco}")
    print("========================================")


def main():
    """
    Função principal que gerencia o fluxo do sistema bancário.
    """
    clientes = []
    contas = []
    saudacao_exibida = False

    while True:
        opcao = menu(exibir_saudacao=not saudacao_exibida)
        saudacao_exibida = True

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "lu":
            listar_usuarios(clientes)

        elif opcao == "q":
            print("\nObrigado por utilizar nossos serviços, volte sempre!")
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
