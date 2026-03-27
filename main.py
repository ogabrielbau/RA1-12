from __future__ import annotations

"""
main.py  —  Aluno 4
Uso: python main.py <arquivo_entrada.txt>
"""

import sys
from pathlib import Path

try:
    from src.rpn_compiler.lexer import LexicalError, parseExpressao
    from src.rpn_compiler.gerador_assembly import lerArquivo, gerarAssembly
    from src.rpn_compiler.evaluator import Evaluator
except ModuleNotFoundError:
    from lexer import LexicalError, parseExpressao
    from gerador_assembly import lerArquivo, gerarAssembly
    from evaluator import Evaluator


def exibirResultados(resultados: dict, linhas: list[str]) -> None:
    print(f"  {'Resultados das expressoes RPN':^51}")
    print("-" * 55)
    print(f"  (N RES) = resultado de tal linha")

    for i, valor in resultados.items():
        expr = linhas[i - 1] if i <= len(linhas) else "?"
        print(f"  Linha {i:>2}: {expr}")

        if valor is None:
            print(f" ")
            continue

        try:
            numero = float(valor)
            if numero == int(numero):
                print(f" resultado: {int(numero)}")
                print( "\n")
            else:
                print(f" resultado: {numero:.1f}")
                print( "\n")
        except (ValueError, OverflowError):
            print(f" resultado da expressao:{valor}")

def exibirErroLexico(num_linha: int, linha: str, erro: str) -> None:
    print(f"  ERRO LEXICO na linha {num_linha}")
    print(f"  Expressao : {linha}")
    print(f"  Problema  : {erro}")
    print(f"  Esta linha sera ignorada.")
    print(f"{'=' * 55}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_entrada.txt>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    linhas: list[str] = []

    try:
        lerArquivo(nome_arquivo, linhas)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    if not linhas:
        print(f"Aviso: arquivo '{nome_arquivo}' nao contem expressoes validas.")
        sys.exit(0)

    linhas_tokens:  list[list[str]] = []
    todos_tokens:   list[str]       = []
    linhas_validas: list[str]       = []
    houve_erro = False

    for num_linha, linha in enumerate(linhas, start=1):
        tokens_linha: list[str] = []
        try:
            parseExpressao(linha, tokens_linha)
            linhas_tokens.append(tokens_linha)
            todos_tokens.extend(tokens_linha)
            linhas_validas.append(linha)
        except LexicalError as exc:
            exibirErroLexico(num_linha, linha, str(exc))
            houve_erro = True

    if not linhas_tokens:
        print("Nenhuma expressao valida encontrada.")
        sys.exit(1)

    evaluator = Evaluator()
    evaluator.processarLinhas(linhas_tokens)
    resultados = evaluator.get_resultados()

    exibirResultados(resultados, linhas_validas)

    if houve_erro:
        print("Aviso: algumas linhas tinham erros lexicos e foram ignoradas.\n")

    codigo: list[str] = []
    gerarAssembly(todos_tokens, codigo)

    nome_saida = Path(nome_arquivo).stem + ".s"
    Path(nome_saida).write_text("\n".join(codigo) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()