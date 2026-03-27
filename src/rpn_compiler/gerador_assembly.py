from __future__ import annotations

"""
gerador_assembly.py  —  Aluno 3
================================
lerArquivo   : lê o arquivo .txt de expressões RPN  (Aluno 3)
gerarAssembly: converte tokens em Assembly ARMv7     (núcleo do grupo)

Saída via JTAG UART — compatível com CPUlator ARMv7 DE1-SoC (v16.1).
"""

from pathlib import Path

try:
    from src.rpn_compiler.lexer import LexicalError, parseExpressao
except ModuleNotFoundError:
    from lexer import LexicalError, parseExpressao  # type: ignore


# ═══════════════════════════════════════════════════════════════════════
# lerArquivo  —  Responsabilidade: Aluno 3
# ═══════════════════════════════════════════════════════════════════════

def lerArquivo(nomeArquivo: str, linhas: list[str]) -> list[str]:
    """
    Lê *nomeArquivo* e acumula as linhas de expressão em *linhas*.
    Linhas em branco e comentários (#) são ignorados.
    Retorna a própria lista *linhas*.
    Levanta FileNotFoundError com mensagem clara se o arquivo não existir.
    """
    caminho = Path(nomeArquivo)
    if not caminho.exists() or not caminho.is_file():
        raise FileNotFoundError(
            f"Erro: arquivo '{nomeArquivo}' nao encontrado. "
            "Verifique o caminho e tente novamente."
        )
    with caminho.open(encoding="utf-8") as fh:
        for linha in fh:
            linha_limpa = linha.rstrip("\n")
            stripped = linha_limpa.strip()
            if not stripped or stripped.startswith("#"):
                continue
            linhas.append(linha_limpa)
    return linhas


# ═══════════════════════════════════════════════════════════════════════
# Núcleo do gerador de Assembly  —  baseado na implementação do grupo
# ═══════════════════════════════════════════════════════════════════════

SEG7_DIGITS = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
SEG7_BLANK  = 0x00
SEG7_MINUS  = 0x40

UART_BASE = 0xFF201000
UART_DATA = UART_BASE
UART_CTRL = UART_BASE + 0x4

_TIPOS_VALOR_DIRETO = {"NUMBER", "MEM_NAME"}
_MAPA_TIPO = {
    "KEYWORD_RES": "RES",
    "OP_ADD":  "+", "OP_SUB":  "-",
    "OP_MUL":  "*", "OP_DIV":  "/",
    "OP_POW":  "^", "OP_INTDIV": "//", "OP_MOD": "%",
}

def _token_para_str(tok) -> str:
    if not (hasattr(tok, "tipo") and hasattr(tok, "valor")):
        raise TypeError(f"Token inválido: {type(tok).__name__!r}: {tok!r}")
    tipo = tok.tipo
    if tipo in _TIPOS_VALOR_DIRETO:
        return tok.valor
    if tipo in _MAPA_TIPO:
        return _MAPA_TIPO[tipo]
    raise ValueError(f"Tipo de token desconhecido: {tipo!r}")

_TIPOS_IGNORADOS = {"LPAREN", "RPAREN"}
_STRS_IGNORADAS  = {"(", ")"}

def _normalizar_tokens(tokens: list) -> list[str]:
    resultado = []
    for i, tok in enumerate(tokens):
        if isinstance(tok, str):
            if tok in _STRS_IGNORADAS:
                continue
            if not tok:
                raise ValueError(f"Token na posição {i} é string vazia.")
            resultado.append(tok)
        else:
            if hasattr(tok, "tipo") and tok.tipo in _TIPOS_IGNORADOS:
                continue
            resultado.append(_token_para_str(tok))
    return resultado


class _Estado:
    def __init__(self):
        self.label_n    = 0
        self.dreg_n     = 0
        self.ireg_n     = 0
        self.free_iregs = ["r0","r1","r2","r3","r4","r5","r6","r7","r8","r9"]
        self.const_pool = {}
        self.mem_vars   = set()
        self.data       = []
        self.history    = []

    def reset_regs(self):
        self.dreg_n = 0
        self.ireg_n = 0
        self.free_iregs = ["r0","r1","r2","r3","r4","r5","r6","r7","r8","r9"]


def _compilar_bloco(tokens: list[str], estado: _Estado) -> tuple[list[str], dict]:
    code  = []
    stack = []

    def new_label(prefix="L"):
        lbl = f"{prefix}{estado.label_n}"
        estado.label_n += 1
        return lbl

    def dreg():
        if estado.dreg_n > 13:
            raise RuntimeError("Registradores VFP esgotados.")
        r = f"d{estado.dreg_n}"
        estado.dreg_n += 1
        return r

    def ireg():
        if not estado.free_iregs:
            raise RuntimeError("Registradores inteiros esgotados.")
        return estado.free_iregs.pop(0)

    def free_ireg(r):
        if r not in estado.free_iregs:
            estado.free_iregs.insert(0, r)

    def emit(line): code.append(line)
    def note(msg):  code.append(f"    @ {msg}")

    def is_number(t):
        try:    float(t); return True
        except: return False

    def is_mem(t):
        return bool(t) and t.isalpha() and t.isupper() and t != "RES"

    def const_label(value_str):
        if value_str not in estado.const_pool:
            lbl = new_label("C")
            estado.const_pool[value_str] = lbl
            estado.data.append(f"{lbl}:  .double {value_str}")
        return estado.const_pool[value_str]

    def mem_label(name):
        if name not in estado.mem_vars:
            estado.mem_vars.add(name)
            estado.data.append(f"MEM_{name}:  .double 0.0  @ variável {name}")
        return f"MEM_{name}"

    def sreg_low(dn):
        return f"s{2 * int(dn[1:])}"

    def double_to_int(dn, rn):
        lbl_half = const_label("0.5")
        note(f"double→int: {dn} → {rn}")
        emit(f"    VMOV.F64    d30, {dn}")
        emit(f"    LDR         r12, ={lbl_half}")
        emit(f"    VLDR        d31, [r12]")
        emit(f"    VCMP.F64    d30, #0")
        emit(f"    VMRS        APSR_nzcv, FPSCR")
        lbl_neg = new_label("ROUND_NEG")
        lbl_end = new_label("ROUND_END")
        emit(f"    BLT         {lbl_neg}")
        emit(f"    VADD.F64    d30, d30, d31")
        emit(f"    B           {lbl_end}")
        emit(f"{lbl_neg}:")
        emit(f"    VSUB.F64    d30, d30, d31")
        emit(f"{lbl_end}:")
        emit(f"    VCVT.S32.F64 s28, d30")
        emit(f"    VMOV         {rn}, s28")

    def fpu_idiv(da, db, dr, rr):
        note(f"div inteira: {da} // {db} → {dr} ({rr})")
        emit(f"    VDIV.F64    {dr}, {da}, {db}")
        double_to_int(dr, rr)

    def to_float(op):
        if op["kind"] == "float":
            return op
        d = dreg()
        emit(f"    VMOV         {sreg_low(d)}, {op['reg']}")
        emit(f"    VCVT.F64.S32 {d}, {sreg_low(d)}")
        return {"reg": d, "kind": "float"}

    def to_int(op):
        if op["kind"] == "int":
            return op
        r = ireg()
        double_to_int(op["reg"], r)
        return {"reg": r, "kind": "int"}

    def load_number(value_str):
        lbl = const_label(value_str)
        d = dreg(); r = ireg()
        note(f"push {value_str} → {d}")
        emit(f"    LDR     {r}, ={lbl}")
        emit(f"    VLDR    {d}, [{r}]")
        free_ireg(r)
        stack.append({"reg": d, "kind": "float"})

    def load_mem(name):
        lbl = mem_label(name)
        d = dreg(); r = ireg()
        note(f"load {name} → {d}")
        emit(f"    LDR     {r}, ={lbl}")
        emit(f"    VLDR    {d}, [{r}]")
        free_ireg(r)
        stack.append({"reg": d, "kind": "float"})

    def store_mem(name):
        if not stack:
            raise RuntimeError(f"Pilha vazia ao gravar em {name}.")
        op = stack[-1]; lbl = mem_label(name); r = ireg()
        note(f"store {op['reg']} → {name}")
        emit(f"    LDR     {r}, ={lbl}")
        if op["kind"] == "float":
            emit(f"    VSTR    {op['reg']}, [{r}]")
        else:
            tmp = dreg()
            emit(f"    VMOV         {sreg_low(tmp)}, {op['reg']}")
            emit(f"    VCVT.F64.S32 {tmp}, {sreg_low(tmp)}")
            emit(f"    VSTR         {tmp}, [{r}]")
        free_ireg(r)

    def load_res(n):
        history = estado.history
        if n >= len(history):
            raise RuntimeError(f"RES({n}): histórico insuficiente.")
        past = history[n]
        if "reg" in past:
            if past["kind"] == "float":
                d = dreg()
                emit(f"    VMOV    {d}, {past['reg']}")
                stack.append({"reg": d, "kind": "float"})
            else:
                r = ireg()
                emit(f"    MOV     {r}, {past['reg']}")
                stack.append({"reg": r, "kind": "int"})
        else:
            lbl = past["label"]; d = dreg(); r = ireg()
            emit(f"    LDR     {r}, ={lbl}")
            emit(f"    VLDR    {d}, [{r}]")
            free_ireg(r)
            if past["kind"] == "float":
                stack.append({"reg": d, "kind": "float"})
            else:
                r2 = ireg()
                double_to_int(d, r2)
                stack.append({"reg": r2, "kind": "int"})

    def float_op(op):
        if len(stack) < 2:
            raise RuntimeError(f"Pilha insuficiente para '{op}'.")
        b = to_float(stack.pop()); a = to_float(stack.pop()); d = dreg()
        instr = {"+":"VADD.F64", "-":"VSUB.F64", "*":"VMUL.F64", "/":"VDIV.F64"}[op]
        note(f"{a['reg']} {op} {b['reg']} → {d}")
        emit(f"    {instr}  {d}, {a['reg']}, {b['reg']}")
        result = {"reg": d, "kind": "float"}
        stack.append(result)
        estado.history.insert(0, result)

    def pow_op():
        if len(stack) < 2:
            raise RuntimeError("Pilha insuficiente para '^'.")
        exp_op = stack.pop(); base = to_float(stack.pop())
        exp_r = ireg()
        if exp_op["kind"] == "float":
            double_to_int(exp_op["reg"], exp_r)
        else:
            emit(f"    MOV     {exp_r}, {exp_op['reg']}")
        d = dreg(); cnt = ireg(); r1 = ireg()
        one = const_label("1.0")
        lp = new_label("POW_LP"); end = new_label("POW_END")
        note(f"{base['reg']} ^ {exp_r} → {d}")
        emit(f"    LDR      {r1}, ={one}")
        emit(f"    VLDR     {d}, [{r1}]")
        emit(f"    MOV      {cnt}, {exp_r}")
        emit(f"{lp}:")
        emit(f"    CMP      {cnt}, #0")
        emit(f"    BLE      {end}")
        emit(f"    VMUL.F64 {d}, {d}, {base['reg']}")
        emit(f"    SUB      {cnt}, {cnt}, #1")
        emit(f"    B        {lp}")
        emit(f"{end}:")
        result = {"reg": d, "kind": "float"}
        stack.append(result)
        estado.history.insert(0, result)

    def int_op(op):
        if len(stack) < 2:
            raise RuntimeError(f"Pilha insuficiente para '{op}'.")
        b_raw = stack.pop(); a_raw = stack.pop()
        a = to_float(a_raw); b = to_float(b_raw)
        dq = dreg(); rq = ireg()
        fpu_idiv(a["reg"], b["reg"], dq, rq)
        if op == "//":
            result = {"reg": rq, "kind": "int"}
            stack.append(result)
            estado.history.insert(0, result)
        else:
            dq_clean = dreg()
            note("módulo: reconverte quociente → double")
            emit(f"    VMOV         {sreg_low(dq_clean)}, {rq}")
            emit(f"    VCVT.F64.S32 {dq_clean}, {sreg_low(dq_clean)}")
            dprod = dreg(); dresto = dreg()
            emit(f"    VMUL.F64 {dprod}, {dq_clean}, {b['reg']}")
            emit(f"    VSUB.F64 {dresto}, {a['reg']}, {dprod}")
            rresto = ireg()
            double_to_int(dresto, rresto)
            result = {"reg": rresto, "kind": "int"}
            stack.append(result)
            estado.history.insert(0, result)

    def emit_jtag(val):
        note("=== JTAG UART output ===")
        if val["kind"] == "float":
            emit(f"    VMOV.F64    d0, {val['reg']}")
            emit(f"    BL          uart_print_float1")
        else:
            emit(f"    MOV         r0, {val['reg']}")
            emit(f"    BL          uart_print_int")
        emit(f"    MOV         r0, #10")
        emit(f"    BL          uart_putc")

    # Loop principal
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if is_number(tok):
            load_number(tok); i += 1
        elif tok in ("+", "-", "*", "/"):
            float_op(tok); i += 1
        elif tok == "^":
            pow_op(); i += 1
        elif tok in ("//", "%"):
            int_op(tok); i += 1
        elif tok == "RES":
            if i == 0 or not is_number(tokens[i - 1]):
                raise ValueError("RES precisa ser precedido de número inteiro.")
            stack.pop()
            estado.dreg_n -= 1
            load_res(int(float(tokens[i - 1]))); i += 1
        elif is_mem(tok):
            prev_is_value = i > 0 and (
                is_number(tokens[i-1]) or
                tokens[i-1] in ("+","-","*","/","^","//","%") or
                is_mem(tokens[i-1])
            )
            if stack and prev_is_value:
                store_mem(tok)
                estado.history.insert(0, stack[-1])
            else:
                load_mem(tok)
            i += 1
        else:
            raise ValueError(f"Token desconhecido: '{tok}'")

    if not stack:
        raise RuntimeError("Pilha vazia — expressão sem resultado.")

    final = stack[-1]
    emit("")
    emit_jtag(final)

    # Persiste resultado para RES entre blocos
    slot_lbl = new_label("_RES_SLOT_")
    estado.data.append(f"@ slot expressão '{' '.join(tokens)}'")
    estado.data.append(f"{slot_lbl}:  .double 0.0")
    note(f"persiste em {slot_lbl}")
    r_slot = ireg()
    emit(f"    LDR     {r_slot}, ={slot_lbl}")
    if final["kind"] == "float":
        emit(f"    VSTR    {final['reg']}, [{r_slot}]")
    else:
        emit(f"    VMOV         s28, {final['reg']}")
        emit(f"    VCVT.F64.S32 d14, s28")
        emit(f"    VSTR         d14, [{r_slot}]")

    estado.history.insert(0, {"kind": final["kind"], "label": slot_lbl})
    return code, final


# ── Helpers UART (emitidos uma vez no final do .s) ────────────────────

_UART_HELPERS = """
@ ======== UART helpers ========
uart_putc:
    PUSH {r1, r2, lr}
    LDR  r1, =0xFF201000
uart_putc_wait:
    LDR  r2, [r1, #4]
    LSR  r2, r2, #16
    BEQ  uart_putc_wait
    STRB r0, [r1]
    POP  {r1, r2, lr}
    BX   lr

uart_divmod10:
    PUSH {r2, r3, lr}
    MOV  r1, #10
    MOV  r2, #0
uart_divmod10_loop:
    CMP  r0, r1
    BLT  uart_divmod10_end
    SUB  r0, r0, r1
    ADD  r2, r2, #1
    B    uart_divmod10_loop
uart_divmod10_end:
    MOV  r1, r0
    MOV  r0, r2
    POP  {r2, r3, lr}
    BX   lr

uart_print_u32:
    PUSH {r1, r2, r3, lr}
    CMP  r0, #10
    BLT  uart_print_u32_digit
    BL   uart_divmod10
    MOV  r2, r1
    BL   uart_print_u32
    MOV  r0, r2
    ADD  r0, r0, #'0'
    BL   uart_putc
    POP  {r1, r2, r3, lr}
    BX   lr
uart_print_u32_digit:
    ADD  r0, r0, #'0'
    BL   uart_putc
    POP  {r1, r2, r3, lr}
    BX   lr

uart_print_int:
    PUSH {r1, r2, r3, r4, lr}
    MOV  r4, r0
    CMP  r4, #0
    BGE  uart_print_int_pos
    MOV  r0, #'-'
    BL   uart_putc
    RSB  r4, r4, #0
uart_print_int_pos:
    MOV  r0, r4
    BL   uart_print_u32
    POP  {r1, r2, r3, r4, lr}
    BX   lr

uart_print_float1:
    PUSH {r1, r2, r3, r4, lr}
    VCMP.F64    d0, #0
    VMRS        APSR_nzcv, FPSCR
    MOV         r4, #0
    BGE         uart_float_abs_ok
    MOV         r4, #1
    VNEG.F64    d0, d0
uart_float_abs_ok:
    LDR         r2, =UART_FLOAT10
    VLDR        d1, [r2]
    VMUL.F64    d0, d0, d1
    LDR         r2, =UART_HALF
    VLDR        d1, [r2]
    VADD.F64    d0, d0, d1
    VCVT.S32.F64 s0, d0
    VMOV        r0, s0
    BL          uart_divmod10
    MOV         r2, r0
    MOV         r3, r1
    CMP         r4, #0
    BEQ         uart_float_print_num
    MOV         r0, #'-'
    BL          uart_putc
uart_float_print_num:
    MOV         r0, r2
    BL          uart_print_u32
    MOV         r0, #'.'
    BL          uart_putc
    ADD         r0, r3, #'0'
    BL          uart_putc
    POP         {r1, r2, r3, r4, lr}
    BX          lr
"""


# ═══════════════════════════════════════════════════════════════════════
# API pública
# ═══════════════════════════════════════════════════════════════════════

def gerarAssemblySequencia(lista_de_tokens: list[list]) -> str:
    """
    Compila uma sequência de expressões RPN num único arquivo .s.
    Retorna o código Assembly como string.
    """
    if not lista_de_tokens:
        raise ValueError("Lista de expressões vazia.")

    estado     = _Estado()
    todos_code = []
    expressoes = []

    for idx, tokens in enumerate(lista_de_tokens):
        if not tokens:
            continue
        tokens = _normalizar_tokens(tokens)
        expressoes.append(" ".join(tokens))
        estado.reset_regs()
        todos_code.append(f"    @ --- bloco {idx}: {' '.join(tokens)} ---")
        code, _ = _compilar_bloco(tokens, estado)
        todos_code.extend(code)
        todos_code.append("")

    # Constantes UART no .data
    estado.data += [
        "",
        "@ constantes UART",
        "UART_FLOAT10:  .double 10.0",
        "UART_HALF:     .double 0.5",
    ]

    partes = [
        "@ Gerado automaticamente — ARMv7 DE1-SoC (CPUlator)",
        f"@ {len(expressoes)} expressao(oes) compilada(s)",
    ] + [f"@   [{i}] {e}" for i, e in enumerate(expressoes)] + [
        ".global _start",
        "",
        ".section .data",
        "",
    ] + estado.data + [
        "",
        ".section .text",
        "_start:",
        "",
    ] + todos_code + [
        "    B   .   @ halt",
        _UART_HELPERS,
    ]

    return "\n".join(partes)


def gerarAssembly(tokens: list[str], codigoAssembly: list[str]) -> None:
    """
    Interface compatível com o main.py do grupo.
    Recebe tokens acumulados de TODAS as linhas e preenche codigoAssembly.

    Os tokens são separados por expressão (delimitados por parênteses de
    nível 0) e compilados como sequência.
    """
    # Separa tokens em expressões individuais
    lista: list[list[str]] = []
    atual: list[str] = []
    prof = 0

    for tok in tokens:
        if tok == "(":
            prof += 1
            atual.append(tok)
        elif tok == ")":
            prof -= 1
            atual.append(tok)
            if prof == 0:
                lista.append(atual)
                atual = []
        else:
            atual.append(tok)

    if atual:
        lista.append(atual)

    if not lista:
        return

    codigo = gerarAssemblySequencia(lista)
    codigoAssembly.extend(codigo.splitlines())