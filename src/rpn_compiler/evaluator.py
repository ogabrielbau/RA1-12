import operator
from collections import deque
from typing import Iterator


class MemoryAccessError(AttributeError):
    """Erro ao acessar valor na memoria"""


class Evaluator:
    def __init__(self):
        self.memoria: dict[str, str] = {}
        self.resultados: dict[int, str | None] = {}

    def _applyBinaryOp(self, op_func, op_symbol: str, pilha: deque) -> float:
        x2 = float(pilha.pop())
        x1 = float(pilha.pop())
        result = op_func(x1, x2)
        return result

    def processarLinhas(self, linhas: list[list[str]]):
        for i, linha in enumerate(linhas, start=1):
            try:
                self.resultados[i] = self.executarExpressao(iter(linha))
            except Exception as e:
                print(f"Error processing line {i}: {e}")
                self.resultados[i] = None

    def executarExpressao(
        self, linha_iter: Iterator
    ) -> str | None:  # iterators are stateful so it will preserve when recursion
        pilha = deque()
        result = None
        for token in linha_iter:
            match token:
                case "+":
                    result = self._applyBinaryOp(operator.add, "+", pilha)

                case "-":
                    result = self._applyBinaryOp(operator.sub, "-", pilha)

                case "*":
                    result = self._applyBinaryOp(operator.mul, "*", pilha)

                case "/":
                    result = self._applyBinaryOp(operator.truediv, "/", pilha)

                case "//":
                    result = self._applyBinaryOp(operator.floordiv, "//", pilha)

                case "%":
                    result = self._applyBinaryOp(operator.mod, "%", pilha)

                case "^":
                    result = self._applyBinaryOp(operator.pow, "^", pilha)

                case "RES":
                    val = pilha.pop()
                    # Handle both integer strings "2" and float strings "2.0"
                    try:
                        linha_alvo = int(val)
                    except ValueError:
                        linha_alvo = int(float(val))

                    result = self.resultados.get(linha_alvo)

                case token if token.isalpha() and token.isupper():
                    if len(pilha) == 0:
                        if token in self.memoria:
                            result = str(self.memoria[token])
                        else:
                            raise MemoryAccessError  # TODO this might be better handled by syntax analyzer but dont know
                    else:
                        value = pilha.pop()
                        self.memoria[token] = value

                case "(":
                    result = self.executarExpressao(
                        linha_iter
                    )  # evaluate whats inside the parenthesis and return it

                case ")":  # only need the opening brackets for MEM calls
                    return (
                        pilha.pop() if len(pilha) > 0 else None
                    )  # TODO this is because of nested parenthesis

                case _:
                    pilha.append(token)

            if result is not None:
                pilha.append(result)
                result = None  # Reset result after pushing

        if len(pilha) > 0:
            return str(pilha.pop())
        return None

    def get_resultados(self):
        return self.resultados

