import struct
import sys
from typing import Iterator

def ler_arquivo_entrada(self, nome_arquivo: str) -> list[list[str]]:
    try:
        with open(nome_arquivo, 'r') as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []
    
class GeradorAssemblyARM:
    def __init__(self):
        self.instrucoes = [] # guarda as instrucoes (text)
        self.dados_constantes = [] # guarda as constantes (data)
        self.variaveis_mem = set() # guarda as variaveis MEM (data)
        self.contador_const = 0 # contador para criar labels unicas para cada numeri

    def _floar_to_hex(self, valor: str) -> str:
        # Converte uma string para sua representação hexadecimal
        return hex(struct.unpack('<Q', struct.pack('<d', float(valor)))[0])
    
    def gerar_instrucoes_rpn(self, tokens_iter: Iterator):
        # Gerar as instrucoes assembly a partir dos tokens
        for token in tokens_iter:
            match token:
                case "+":
                    self.instrucoes.append("VADD.F64", "Soma")
                case "-":
                    self.instrucoes.append("VSUB.F64", "Subtracao")
                case "*":
                    self.instrucoes.append("VMUL.F64", "Multiplicacao")
                case "/":
                    self.instrucoes.append("VDIV.F64", "Divisao")

                case "//": 
                    self.gerar_divisao_inteira()
                case "%": 
                    self.gerar_resto_divisao()
                
                case "^":
                    self.instrucoes.append("@ Potenciacao(^)")
                    self.instrucoes.append("VPOP {D1} @ Expoente")
                    self.instrucoes.append("VPOP {D0} @ Base")
                    self.instrucoes.append("BL sub_potencia @ Chama a funcao de potencia")
                    self.instrucoes.append("VPUSH {D0} @ Resultado da potencia")

                case "(":
                    self.gerar_instrucoes_rpn(tokens_iter)
                case ")":
                    return
                
                case token if token.isupper():
                    self.variaveis_mem.add(token)
                    self.instrucoes.append(f" @Acesso MEM: {token}")
                    self.instrucoes.append(f"LDR R), ={token}")
                    self.instrucoes.append("VLDR.64 D0, [R0]")
                    self.instrucoes.append("VPUSH {{D0}}")
                
                case _:
                    if self._is_numeric(token):
                        label_const = f"const_{self.contador_const}"
                        valor_hex = self._floar_to_hex_64(token)
                        self.dados_constantes.append(f"{label_const}: .8byte {valor_hex} @ {token}")
                        self.instrucoes.append(f"LDR R0, ={label_const}")
                        self.instrucoes.append("VLDR.64 D0, [R0]")
                        self.instrucoes.append("VPUSH {D0}")
                        self.contador_const += 1