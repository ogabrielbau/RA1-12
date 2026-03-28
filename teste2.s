.global _start

.section .data
C0: .double 100.0
C1: .double 200.0
RES_SLOT2: .double 0.0
C3: .double 500.0
C4: .double 3.0
RES_SLOT5: .double 0.0
C6: .double 1000.0
C7: .double 4.0
RES_SLOT8: .double 0.0
C9: .double 99.0
C10: .double 14.0
RES_SLOT11: .double 0.0
RES_SLOT12: .double 0.0
C13: .double 2.0
C14: .double 10.0
C17: .double 1.0
RES_SLOT18: .double 0.0
C19: .double 1
RES_SLOT20: .double 0.0
C21: .double 2
RES_SLOT22: .double 0.0
C23: .double 50.5
MEM_TOTAL: .double 0.0  @ var TOTAL
RES_SLOT24: .double 0.0
RES_SLOT25: .double 0.0
RES_SLOT26: .double 0.0
RES_SLOT27: .double 0.0
C28: .double 5.0
RES_SLOT31: .double 0.0
C32: .double 6
RES_SLOT33: .double 0.0

.section .text
_start:
    @ Habilita FPU
    MRC p15, 0, r0, c1, c0, 2
    ORR r0, r0, #0x00F00000
    MCR p15, 0, r0, c1, c0, 2
    VMRS r0, FPEXC
    ORR r0, r0, #0x40000000
    VMSR FPEXC, r0

    @ --- Expressao 1 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C0
    VLDR d0, [r12]
    LDR r12, =C1
    VLDR d1, [r12]
    VADD.F64 d2, d0, d1
    LDR r12, =RES_SLOT2
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 2 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #50
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C3
    VLDR d0, [r12]
    LDR r12, =C4
    VLDR d1, [r12]
    VMUL.F64 d2, d0, d1
    LDR r12, =RES_SLOT5
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 3 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #51
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C6
    VLDR d0, [r12]
    LDR r12, =C7
    VLDR d1, [r12]
    VDIV.F64 d2, d0, d1
    LDR r12, =RES_SLOT8
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 4 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #52
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C9
    VLDR d0, [r12]
    LDR r12, =C10
    VLDR d1, [r12]
    VDIV.F64 d2, d0, d1
    VCVT.S32.F64 s28, d2
    VCVT.F64.S32 d2, s28
    LDR r12, =RES_SLOT11
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 5 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #53
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C9
    VLDR d0, [r12]
    LDR r12, =C10
    VLDR d1, [r12]
    VDIV.F64 d2, d0, d1
    VCVT.S32.F64 s28, d2
    VCVT.F64.S32 d2, s28
    VMUL.F64 d2, d2, d1
    VSUB.F64 d2, d0, d2
    LDR r12, =RES_SLOT12
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 6 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #54
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C13
    VLDR d0, [r12]
    LDR r12, =C14
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C17
    VLDR d2, [r1]
POW_L15:
    CMP r0, #0
    BLE POW_E16
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L15
POW_E16:
    LDR r12, =RES_SLOT18
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 7 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #55
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C19
    VLDR d0, [r12]
    LDR r12, =RES_SLOT2
    VLDR d1, [r12]
    LDR r12, =RES_SLOT20
    VSTR d1, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 8 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #56
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C21
    VLDR d0, [r12]
    LDR r12, =RES_SLOT5
    VLDR d1, [r12]
    LDR r12, =RES_SLOT22
    VSTR d1, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 9 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #57
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C23
    VLDR d0, [r12]
    LDR r12, =MEM_TOTAL
    VSTR d0, [r12]
    LDR r12, =RES_SLOT24
    VSTR d0, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 10 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #48
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =MEM_TOTAL
    VLDR d0, [r12]
    LDR r12, =RES_SLOT25
    VSTR d0, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 11 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =MEM_TOTAL
    VLDR d0, [r12]
    LDR r12, =C13
    VLDR d1, [r12]
    VMUL.F64 d2, d0, d1
    LDR r12, =RES_SLOT26
    VSTR d2, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 12 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #50
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =MEM_TOTAL
    VLDR d0, [r12]
    LDR r12, =C19
    VLDR d1, [r12]
    LDR r12, =RES_SLOT2
    VLDR d2, [r12]
    VADD.F64 d3, d0, d2
    LDR r12, =RES_SLOT27
    VSTR d3, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 13 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #51
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C0
    VLDR d0, [r12]
    LDR r12, =C1
    VLDR d1, [r12]
    VADD.F64 d2, d0, d1
    LDR r12, =C4
    VLDR d3, [r12]
    LDR r12, =C7
    VLDR d4, [r12]
    VMUL.F64 d5, d3, d4
    VDIV.F64 d6, d2, d5
    LDR r12, =C13
    VLDR d7, [r12]
    LDR r12, =C28
    VLDR d8, [r12]
    VCVT.S32.F64 s28, d8
    VMOV r0, s28
    LDR r1, =C17
    VLDR d9, [r1]
POW_L29:
    CMP r0, #0
    BLE POW_E30
    VMUL.F64 d9, d9, d7
    SUB r0, r0, #1
    B POW_L29
POW_E30:
    VADD.F64 d10, d6, d9
    LDR r12, =RES_SLOT31
    VSTR d10, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    @ --- Expressao 14 ---
    MOV r0, #76
    BL uart_putc
    MOV r0, #49
    BL uart_putc
    MOV r0, #52
    BL uart_putc
    MOV r0, #58
    BL uart_putc
    MOV r0, #32
    BL uart_putc
    LDR r12, =C32
    VLDR d0, [r12]
    LDR r12, =RES_SLOT18
    VLDR d1, [r12]
    LDR r12, =RES_SLOT33
    VSTR d1, [r12]
    VLDR d0, [r12]
    BL uart_print_float1
    MOV r0, #10
    BL uart_putc

    B .   @ halt

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
