from datetime import datetime, date

# ==================== DECORADOR DE LOG ====================

def registrar_transacao(tipo):
    def decorador(func):
        def wrapper(*args, **kwargs):
            resultado = func(*args, **kwargs)
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{data_hora}] Transação realizada: {tipo.upper()}")
            return resultado
        return wrapper
    return decorador

# ==================== CLASSES AUXILIARES ====================

class ContaIterador:
    """Iterador personalizado para percorrer contas"""
    def __init__(self, contas):
        self._contas = contas
        self._indice = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._indice >= len(self._contas):
            raise StopIteration
        conta = self._contas[self._indice]
        self._indice += 1
        return f"Agência: {conta['agencia']} | Conta: {conta['numero_conta']} | Titular: {conta['usuario']['nome']}"

# ==================== GERADOR DE TRANSAÇÕES ====================

def gerar_transacoes(transacoes, tipo=None):
    """Gera transações de uma conta, com opção de filtro."""
    for transacao in transacoes:
        if tipo is None or tipo.lower() in transacao.lower():
            yield transacao

# ==================== FUNÇÕES PRINCIPAIS ====================

@registrar_transacao("depósito")
def depositar(saldo, valor, extrato, transacoes, transacoes_diarias):
    if transacoes_diarias >= 10:
        print("❌ Limite de 10 transações diárias atingido!")
        return saldo, extrato, transacoes_diarias

    if valor > 0:
        saldo += valor
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        registro = f"[{data_hora}] Depósito: R$ {valor:.2f}"
        extrato += registro + "\n"
        transacoes.append(registro)
        transacoes_diarias += 1
        print("✅ Depósito realizado com sucesso!")
    else:
        print("Valor inválido para depósito.")
    return saldo, extrato, transacoes_diarias


@registrar_transacao("saque")
def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques, transacoes, transacoes_diarias):
    if transacoes_diarias >= 10:
        print("❌ Limite de 10 transações diárias atingido!")
        return saldo, extrato, numero_saques, transacoes_diarias

    if valor > saldo:
        print("Saldo insuficiente!")
    elif valor > limite:
        print("Valor excede o limite de saque!")
    elif numero_saques >= limite_saques:
        print("Limite de saques diários atingido!")
    elif valor > 0:
        saldo -= valor
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        registro = f"[{data_hora}] Saque: R$ {valor:.2f}"
        extrato += registro + "\n"
        transacoes.append(registro)
        numero_saques += 1
        transacoes_diarias += 1
        print("✅ Saque realizado com sucesso!")
    else:
        print("Valor inválido para saque.")
    return saldo, extrato, numero_saques, transacoes_diarias


def exibir_extrato(saldo, *, extrato):
    print("\n========== EXTRATO ==========")
    print("Nenhuma movimentação." if not extrato else extrato)
    print(f"\nSaldo atual: R$ {saldo:.2f}")
    print("=============================")


def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ").strip()
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("Usuário com este CPF já existe!")
        return

    nome = input("Informe o nome completo: ").strip()
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ").strip()
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla): ").strip()

    usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco
    })
    print("Usuário criado com sucesso!")


def filtrar_usuario(cpf, usuarios):
    for usuario in usuarios:
        if usuario["cpf"] == cpf:
            return usuario
    return None


@registrar_transacao("criação de conta")
def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário: ").strip()
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Conta criada com sucesso!")
        return {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario}
    else:
        print("Usuário não encontrado. Crie o usuário antes de criar a conta.")


def listar_contas(contas):
    print("\n=== LISTA DE CONTAS ===")
    for info in ContaIterador(contas):
        print(info)
    print("========================")


# ==================== MENU E FLUXO PRINCIPAL ====================

def menu():
    return """
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo Usuário
[nc] Nova Conta
[l] Listar Contas
[t] Transações (Filtrar)
[q] Sair
=> """


def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    usuarios = []
    contas = []
    transacoes = []
    data_hoje = date.today()
    transacoes_diarias = 0

    while True:
        opcao = input(menu()).lower()

        # Reinicia contador diário se o dia mudou
        if date.today() != data_hoje:
            data_hoje = date.today()
            transacoes_diarias = 0

        if opcao == "d":
            valor = float(input("Valor do depósito: "))
            saldo, extrato, transacoes_diarias = depositar(saldo, valor, extrato, transacoes, transacoes_diarias)

        elif opcao == "s":
            valor = float(input("Valor do saque: "))
            saldo, extrato, numero_saques, transacoes_diarias = sacar(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
                transacoes=transacoes,
                transacoes_diarias=transacoes_diarias,
            )

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            conta = criar_conta(AGENCIA, numero_conta, usuarios)
            if conta:
                contas.append(conta)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "t":
            tipo = input("Filtrar por tipo (saque/depósito) ou Enter para todos: ").lower()
            for t in gerar_transacoes(transacoes, tipo if tipo else None):
                print(t)

        elif opcao == "q":
            print("Saindo do sistema... Até logo!")
            break

        else:
            print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    main()
