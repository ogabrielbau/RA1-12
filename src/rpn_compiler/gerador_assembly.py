from __future__ import annotations
from pathlib import Path

try:
    from src.rpn_compiler.lexer import LexicalError, parseExpressao
except ModuleNotFoundError:
    from lexer import LexicalError, parseExpressao  # type: ignore

def lerArquivo(nomeArquivo: str, linhas: list[str]) -> list[str]:
    caminho = Path(nomeArquivo)
    if not caminho.exists() or not caminho.is_file():
        raise FileNotFoundError(f"Erro: arquivo '{nomeArquivo}' nao encontrado.")
    with caminho.open(encoding="utf-8") as fh:
        for linha in fh:
            linha_limpa = linha.rstrip("\n").strip()
            if not linha_limpa or linha_limpa.startswith("#"):
                continue
            linhas.append(linha_limpa)
    return linhas

class _Estado:
    def __init__(self):
        self.label_n = 0
        self.const_pool = {}
        self.mem_vars = set()
        self.data = []
        self.history = []

def _compilar_bloco(tokens: list[str], estado: _Estado) -> list[str]:
    code = []
    stack = []
    v_regs = 0

    def new_label(prefix="L"):
        lbl = f"{prefix}{estado.label_n}"; estado.label_n += 1; return lbl

    def emit(line): code.append(line)

    def const_label(val):
        if val not in estado.const_pool:
            lbl = new_label("C"); estado.const_pool[val] = lbl
            estado.data.append(f"{lbl}: .double {val}")
        return estado.const_pool[val]

    def is_number(t):
        try: float(t); return True
        except: return False

    def is_mem(t):
        return bool(t) and t.isalpha() and t.isupper() and t != "RES"

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if is_number(tok):
            lbl = const_label(tok)
            reg = f"d{v_regs}"; v_regs += 1
            emit(f"    LDR r12, ={lbl}")
            emit(f"    VLDR {reg}, [r12]")
            stack.append(reg)

        elif tok in ("+", "-", "*", "/"):
            if len(stack) >= 2:
                rb = stack.pop(); ra = stack.pop()
                rd = f"d{v_regs}"; v_regs += 1
                op = {"+":"VADD","-":"VSUB","*":"VMUL","/":"VDIV"}[tok]
                emit(f"    {op}.F64 {rd}, {ra}, {rb}")
                stack.append(rd)

        elif tok == "//":
            if len(stack) >= 2:
                rb = stack.pop(); ra = stack.pop()
                rd = f"d{v_regs}"; v_regs += 1
                emit(f"    VDIV.F64 {rd}, {ra}, {rb}")
                emit(f"    VCVT.S32.F64 s28, {rd}")
                emit(f"    VCVT.F64.S32 {rd}, s28")
                stack.append(rd)

        elif tok == "%":
            if len(stack) >= 2:
                rb = stack.pop(); ra = stack.pop()
                rd = f"d{v_regs}"; v_regs += 1
                emit(f"    VDIV.F64 {rd}, {ra}, {rb}")
                emit(f"    VCVT.S32.F64 s28, {rd}")
                emit(f"    VCVT.F64.S32 {rd}, s28")
                emit(f"    VMUL.F64 {rd}, {rd}, {rb}")
                emit(f"    VSUB.F64 {rd}, {ra}, {rd}")
                stack.append(rd)

        elif tok == "^":
            if len(stack) >= 2:
                rb = stack.pop(); ra = stack.pop()
                rd = f"d{v_regs}"; v_regs += 1
                l_loop = new_label("POW_L")
                l_end  = new_label("POW_E")
                emit(f"    VCVT.S32.F64 s28, {rb}")
                emit(f"    VMOV r0, s28")
                emit(f"    LDR r1, ={const_label('1.0')}")
                emit(f"    VLDR {rd}, [r1]")
                emit(f"{l_loop}:")
                emit(f"    CMP r0, #0")
                emit(f"    BLE {l_end}")
                emit(f"    VMUL.F64 {rd}, {rd}, {ra}")
                emit(f"    SUB r0, r0, #1")
                emit(f"    B {l_loop}")
                emit(f"{l_end}:")
                stack.append(rd)

        elif tok == "RES":
            n = int(float(tokens[i-1]))
            if stack: stack.pop()  # remove o N da pilha
            idx = n - 1            # linha N = indice n-1
            if 0 <= idx < len(estado.history):
                rd = f"d{v_regs}"; v_regs += 1
                emit(f"    LDR r12, ={estado.history[idx]}")
                emit(f"    VLDR {rd}, [r12]")
                stack.append(rd)

        elif is_mem(tok):
            lbl = f"MEM_{tok}"
            if tok not in estado.mem_vars:
                estado.mem_vars.add(tok)
                estado.data.append(f"{lbl}: .double 0.0  @ var {tok}")
            # Store: token anterior e numero ou operador
            prev = tokens[i-1] if i > 0 else ""
            eh_store = is_number(prev) or prev in ("+","-","*","/","^","//","%") or is_mem(prev)
            if stack and eh_store:
                emit(f"    LDR r12, ={lbl}")
                emit(f"    VSTR {stack[-1]}, [r12]")
            else:
                rd = f"d{v_regs}"; v_regs += 1
                emit(f"    LDR r12, ={lbl}")
                emit(f"    VLDR {rd}, [r12]")
                stack.append(rd)

        i += 1

    if stack:
        res = stack[-1]
        # Salva em slot e recarrega em d0 (evita VMOV entre dregs = NEON)
        slot = new_label("RES_SLOT")
        estado.data.append(f"{slot}: .double 0.0")
        emit(f"    LDR r12, ={slot}")
        emit(f"    VSTR {res}, [r12]")
        emit(f"    VLDR d0, [r12]")
        emit(f"    BL uart_print_float1")
        emit(f"    MOV r0, #10")
        emit(f"    BL uart_putc")
        estado.history.append(slot)

    return code

_UART_HELPERS = """
@ ======== UART Helpers ========
uart_putc:
    LDR r1, =0xFF201000
uart_putc_w:
    LDR r2, [r1, #4]
    CMP r2, #0
    BEQ uart_putc_w
    STRB r0, [r1]
    BX lr

uart_print_u32:
    PUSH {r4, lr}
    MOV r4, r0
    CMP r4, #10
    BLT uart_p_digit
    MOV r0, r4
    MOV r2, #0
uart_div10:
    CMP r0, #10
    BLT uart_div10_end
    SUB r0, r0, #10
    ADD r2, r2, #1
    B uart_div10
uart_div10_end:
    MOV r4, r0
    MOV r0, r2
    BL uart_print_u32
uart_p_digit:
    ADD r0, r4, #48
    BL uart_putc
    POP {r4, lr}
    BX lr

uart_print_float1:
    @ Imprime double em d0 com 1 casa decimal
    @ Estrategia: multiplica por 10, imprime parte inteira e decimal
    PUSH {r4, r5, lr}
    @ Verifica sinal
    VCMP.F64 d0, #0
    VMRS APSR_nzcv, FPSCR
    MOV r4, #0
    BGE uart_f_pos
    MOV r4, #1
    VNEG.F64 d0, d0
uart_f_pos:
    @ Multiplica por 10 para obter 1 casa decimal
    MOV r12, #10
    VMOV s2, r12
    VCVT.F64.S32 d1, s2
    VMUL.F64 d0, d0, d1
    @ Arredonda: adiciona 0.5 e trunca
    MOV r12, #0
    VMOV s2, r12
    VCVT.F64.S32 d2, s2
    @ Adiciona 0.5 para arredondar antes de truncar
    MOV r12, #1
    VMOV s4, r12
    VCVT.F64.S32 d3, s4
    @ d3 = 0.5 via d3 = 1 / 2
    MOV r12, #2
    VMOV s4, r12
    VCVT.F64.S32 d4, s4
    VDIV.F64 d3, d3, d4
    VADD.F64 d0, d0, d3
    @ Converte para inteiro (valor * 10 arredondado)
    VCVT.S32.F64 s0, d0
    VMOV r5, s0              @ r5 = valor * 10 (ex: 818 para 81.8)
    @ Imprime sinal se negativo
    CMP r4, #1
    BNE uart_f_nosign
    MOV r0, #45              @ char '-'
    BL uart_putc
uart_f_nosign:
    @ Divide por 10 para obter parte inteira
    MOV r0, r5
    MOV r1, #0
uart_f_div:
    CMP r0, #10
    BLT uart_f_div_end
    SUB r0, r0, #10
    ADD r1, r1, #1
    B uart_f_div
uart_f_div_end:
    @ r1 = parte inteira, r0 = decimal
    MOV r4, r0               @ salva decimal
    MOV r0, r1
    BL uart_print_u32        @ imprime parte inteira
    MOV r0, #46              @ char '.'
    BL uart_putc
    ADD r0, r4, #48          @ decimal + '0'
    BL uart_putc
    POP {r4, r5, lr}
    BX lr
"""

def gerarAssemblySequencia(lista_de_tokens: list[list]) -> str:
    estado = _Estado()
    todos_code = []
    for idx, tokens in enumerate(lista_de_tokens):
        t_limpos = [t for t in tokens if t not in ("(", ")")]
        todos_code.append(f"    @ --- Expressao {idx+1} ---")
        prefixo = f"L{idx+1}: "
        for ch in prefixo:
            todos_code.append(f"    MOV r0, #{ord(ch)}")
            todos_code.append(f"    BL uart_putc")
        todos_code.extend(_compilar_bloco(t_limpos, estado))
        todos_code.append("")

    partes = [
        ".global _start",
        "",
        ".section .data",
    ] + estado.data + [
        "",
        ".section .text",
        "_start:",
        "    @ Habilita FPU",
        "    MRC p15, 0, r0, c1, c0, 2",
        "    ORR r0, r0, #0x00F00000",
        "    MCR p15, 0, r0, c1, c0, 2",
        "    VMRS r0, FPEXC",
        "    ORR r0, r0, #0x40000000",
        "    VMSR FPEXC, r0",
        "",
    ] + todos_code + [
        "    B .   @ halt",
        _UART_HELPERS,
    ]
    return "\n".join(partes)

def gerarAssembly(tokens: list[str], codigoAssembly: list[str]) -> None:
    lista = []; atual = []; p = 0
    for t in tokens:
        if t == "(": p += 1
        atual.append(t)
        if t == ")":
            p -= 1
            if p == 0: lista.append(atual); atual = []
    if lista:
        codigo = gerarAssemblySequencia(lista)
        codigoAssembly.extend(codigo.splitlines())