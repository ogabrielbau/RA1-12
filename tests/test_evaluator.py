import unittest

from src.rpn_compiler.evaluator import Evaluator


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.eval = Evaluator()

    def test_operacoes_basicas(self) -> None:
        linhas = [
            ["(", "3.14", "2.0", "+", ")"],
            ["(", "5.0", "2.0", "-", ")"],
            ["(", "3.0", "4.0", "*", ")"],
            ["(", "10.0", "2.0", "/", ")"],
            ["(", "10.0", "3.0", "//", ")"],
            ["(", "10.0", "3.0", "%", ")"],
            ["(", "2.0", "3.0", "^", ")"],
        ]
        self.eval.processarLinhas(linhas)
        resultados = self.eval.get_resultados()
        
        self.assertAlmostEqual(float(resultados[1]), 5.14)
        self.assertAlmostEqual(float(resultados[2]), 3.0)
        self.assertAlmostEqual(float(resultados[3]), 12.0)
        self.assertAlmostEqual(float(resultados[4]), 5.0)
        self.assertAlmostEqual(float(resultados[5]), 3.0)
        self.assertAlmostEqual(float(resultados[6]), 1.0)
        self.assertAlmostEqual(float(resultados[7]), 8.0)

    def test_parenteses_aninhados(self) -> None:
        linhas = [
            ["(", "(", "1.5", "2.0", "*", ")", "(", "3.0", "4.0", "*", ")", "/", ")"]
        ]
        self.eval.processarLinhas(linhas)
        resultados = self.eval.get_resultados()
        # (1.5 * 2.0) / (3.0 * 4.0) = 3.0 / 12.0 = 0.25
        self.assertAlmostEqual(float(resultados[1]), 0.25)

    def test_memoria_unica(self) -> None:
        linhas = [
            ["(", "10.5", "MEM", ")"],
            ["(", "MEM", ")"],
            ["(", "2.0","(", "MEM", ")", "*", ")"]
        ]
        self.eval.processarLinhas(linhas)
        resultados = self.eval.get_resultados()
        
        # A linha 1 apenas grava na memória e retorna None na implementação atual
        self.assertIsNone(resultados[1])
        # Linha 2 lê a memória
        self.assertAlmostEqual(float(resultados[2]), 10.5)
        # Linha 3 multiplica 2 por MEM
        self.assertAlmostEqual(float(resultados[3]), 21.0)

    def test_historico_resultados_res(self) -> None:
        linhas = [
            ["(", "3.14", "2.0", "+", ")"],         # Linha 1 = 5.14
            ["(", "1", "RES", ")"],                 # Linha 2 = Linha 1 = 5.14
            ["(", "2", "RES", "10.0", "*", ")"]     # Linha 3 = Linha 2 * 10 = 51.4
        ]
        self.eval.processarLinhas(linhas)
        resultados = self.eval.get_resultados()
        
        self.assertAlmostEqual(float(resultados[2]), 5.14)
        self.assertAlmostEqual(float(resultados[3]), 51.4)

    def test_varias_variaveis(self) -> None:
        linhas = [
            ["(", "42", "VAR", ")", "(", "VAR", "1", "+", ")"],
            ["(", "100", "ABC", ")", "(", "ABC", "2", "/", ")"],
        ]
        self.eval.processarLinhas(linhas)
        resultados = self.eval.get_resultados()
        
        # O evaluador retorna o último valor extraído ou processado se houver múltiplos parênteses
        self.assertAlmostEqual(float(resultados[1]), 43.0)
        self.assertAlmostEqual(float(resultados[2]), 50.0)


if __name__ == "__main__":
    unittest.main()