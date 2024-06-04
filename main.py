"""

************* TRABALHO DE COMPILADORES *************** 
-------- TRABALHO PARA O TERCEIRO CRÉDITO - VALOR: 4,0 PONTOS ------
-------- ALUNO: CLEBER SANTOS PINTO JUNIOR -----
--- PROFESSORA: JACQUELINE MIDLEJ --------------

PARA EXECUTAR O PROGRAMA, DIGITE NO TERMINAL: python3 main.py (nome_do_arquivo.txt)

"""

import sys
import re

#essa função adiciona um novo escopo na pilha de escopos
def entra_no_escopo(pilha_de_escopo):
    pilha_de_escopo.append({})

#remove o escopo mais recente da pilha
def saindo_do_escopo(pilha_de_escopo):
    if pilha_de_escopo:
        pilha_de_escopo.pop()
    else:
        print("Erro ao sair do escopo!!!")

#declara nova variavel no escopo atual
def variveis(pilha_de_escopo, linha_atual, lexema, tipo):
    escopo_atual = pilha_de_escopo[-1]
    if lexema in escopo_atual:
        print(f"Erro linha {linha_atual + 1}: Variável {lexema} já declarada no escopo atual")
    else:
        if tipo == 'NUMERO':
            valor_padrao = 0
        elif tipo == 'CADEIA':
            valor_padrao = ""
        escopo_atual[lexema] = {'tipo': tipo, 'valor': valor_padrao}


#função que atribui um valor a nova variavel
def atribui_variavel(pilha_de_escopo, linha_atual, lexema, valor):
    variable = procura_variavel(pilha_de_escopo, lexema)
    if variable:
        if (variable['tipo'] == 'NUMERO' and isinstance(valor, (int, float))) or \
           (variable['tipo'] == 'CADEIA' and isinstance(valor, str)):
            variable['valor'] = valor
        else:
            print(f"Erro linha {linha_atual + 1}: Tipos não compatíveis para atribuição")
    else:
        print(f"Erro linha {linha_atual + 1}: Variável {lexema} não declarada")

#essa função procura varivavel na pilha de escopos 
def procura_variavel(pilha_de_escopo, lexema):
    for escopo in reversed(pilha_de_escopo):
        if lexema in escopo:
            return escopo[lexema]
    return None

def printa_variavel(pilha_de_escopo, linha_atual, lexema):
    variable = procura_variavel(pilha_de_escopo, lexema)
    if variable:
        if variable['valor'] is not None:
            if variable['tipo'] == 'CADEIA':
                print(f'"{variable["valor"]}"')
            else:
                print(variable["valor"])
        else:
            print("NONE")
    else:
        print(f"Erro linha {linha_atual + 1}: Variável {lexema} não declarada")

def preprocess_line(line):
    line = re.sub(r'(?<=[^\s])([=,])(?=[^\s])', r' \1 ', line)
    return line

def analisador(program):
    pilha_de_escopo = [{}] #aqui, cada dicionario representa um escopo
    lines = program.strip().split('\n')
    linha_atual = 0

    #esse laço itera sobre cada linha do arquivo
    for i, line in enumerate(lines):
        linha_atual = i
        line = line.split('#')[0].strip()
        if not line:
            continue

        line = preprocess_line(line)  #faz o preprocessamento para add espaços ao redor de = e ,
        tokens = line.strip().split()

        if not tokens:
            continue
        if tokens[0] == 'BLOCO':
            entra_no_escopo(pilha_de_escopo) 
        elif tokens[0] == 'FIM':
            saindo_do_escopo(pilha_de_escopo)

        #declara novas variaveis no escopo atual
        elif tokens[0] in ['NUMERO', 'CADEIA']:
            tipo = tokens[0]
            declarations = ' '.join(tokens[1:]).split(',')

            for declaration in declarations:
                parts = declaration.split('=') #separa nome e valor da variavel
                lexema = parts[0].strip()
                variveis(pilha_de_escopo, linha_atual, lexema, tipo)
                if len(parts) > 1:
                    valor = parts[1].strip().strip('"')
                    if tipo == 'NUMERO':
                        try:
                            valor = float(valor) if '.' in valor or 'e' in valor.lower() else int(valor)
                        except ValueError:
                            print(f"Erro linha {i+1}: Valor inválido {valor} para o tipo {tipo}")
                            continue
                    atribui_variavel(pilha_de_escopo, linha_atual, lexema, valor)

        elif tokens[0] == 'PRINT':
            printa_variavel(pilha_de_escopo, linha_atual, tokens[1].strip())
        
        #atribui valores já declarados
        elif len(tokens) > 2 and tokens[1] == '=':
            lexema = tokens[0].strip()
            valor = ' '.join(tokens[2:]).strip()

            # Verificar se o valor está entre aspas para identificar como CADEIA
            if valor.startswith('"') and valor.endswith('"'):
                valor = valor.strip('"')
            elif valor.replace('.', '', 1).isdigit() or \
                 (valor[0] in '+-' and valor[1:].replace('.', '', 1).isdigit()):
                valor = float(valor) if '.' in valor or 'e' in valor.lower() else int(valor)
            else:
                variable_valor = procura_variavel(pilha_de_escopo, valor)

                if variable_valor:
                    variable_lexema = procura_variavel(pilha_de_escopo, lexema)
                    if variable_lexema and variable_valor['tipo'] == variable_lexema['tipo']:
                        valor = variable_valor['valor']
                    else:
                        print(f"Erro linha {linha_atual + 1}: Tipos não compatíveis para atribuição")
                        continue
                else:
                    print(f"Erro linha {linha_atual + 1}: Variável {valor} não declarada")
                    continue

            atribui_variavel(pilha_de_escopo, linha_atual, lexema, valor)


def main():
    if len(sys.argv) != 2:
        print("----------- Digite no terminal: -----------")
        print("python3 main.py (nome do arquivo.txt)")
        return

    arquivo = sys.argv[1]
    try:
        with open(arquivo, 'r') as file:
            program = file.read()
        analisador(program)
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado")


if __name__ == "__main__":
    main()
