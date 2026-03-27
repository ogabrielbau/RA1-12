.global _start

.section .data
C0: .double 2.0
C1: .double 16.0
C4: .double 1.0
RES_SLOT5: .double 0.0
C6: .double 15.0
C7: .double 5.0
RES_SLOT10: .double 0.0
C13: .double 3.0
C14: .double 8.0
RES_SLOT17: .double 0.0
C18: .double 1
C19: .double 1000.0
RES_SLOT20: .double 0.0
C21: .double -3.5
RES_SLOT24: .double 0.0
MEM_MEM: .double 0.0  @ var MEM
RES_SLOT27: .double 0.0
C28: .double 99999.0
C29: .double 317.0
RES_SLOT30: .double 0.0
RES_SLOT31: .double 0.0
C32: .double 3
RES_SLOT33: .double 0.0
C34: .double 10000.0
C35: .double 5000.0
C36: .double 3000.0
C37: .double 2000.0
RES_SLOT38: .double 0.0
RES_SLOT41: .double 0.0
C42: .double 6
RES_SLOT43: .double 0.0
RES_SLOT44: .double 0.0
C45: .double 5
C46: .double 8
RES_SLOT47: .double 0.0

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
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L2:
    CMP r0, #0
    BLE POW_E3
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L2
POW_E3:
    LDR r12, =RES_SLOT5
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
    LDR r12, =C6
    VLDR d0, [r12]
    LDR r12, =C7
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L8:
    CMP r0, #0
    BLE POW_E9
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L8
POW_E9:
    LDR r12, =RES_SLOT10
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
    LDR r12, =C0
    VLDR d0, [r12]
    LDR r12, =C1
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L11:
    CMP r0, #0
    BLE POW_E12
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L11
POW_E12:
    LDR r12, =C13
    VLDR d3, [r12]
    LDR r12, =C14
    VLDR d4, [r12]
    VCVT.S32.F64 s28, d4
    VMOV r0, s28
    LDR r1, =C4
    VLDR d5, [r1]
POW_L15:
    CMP r0, #0
    BLE POW_E16
    VMUL.F64 d5, d5, d3
    SUB r0, r0, #1
    B POW_L15
POW_E16:
    VADD.F64 d6, d2, d5
    LDR r12, =RES_SLOT17
    VSTR d6, [r12]
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
    LDR r12, =C18
    VLDR d0, [r12]
    LDR r12, =RES_SLOT5
    VLDR d1, [r12]
    LDR r12, =C19
    VLDR d2, [r12]
    VDIV.F64 d3, d1, d2
    LDR r12, =RES_SLOT20
    VSTR d3, [r12]
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
    LDR r12, =C21
    VLDR d0, [r12]
    LDR r12, =C0
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L22:
    CMP r0, #0
    BLE POW_E23
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L22
POW_E23:
    LDR r12, =RES_SLOT24
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
    LDR r12, =C21
    VLDR d0, [r12]
    LDR r12, =C0
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L25:
    CMP r0, #0
    BLE POW_E26
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L25
POW_E26:
    LDR r12, =MEM_MEM
    VSTR d2, [r12]
    LDR r12, =RES_SLOT27
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
    LDR r12, =C28
    VLDR d0, [r12]
    LDR r12, =C29
    VLDR d1, [r12]
    VDIV.F64 d2, d0, d1
    VCVT.S32.F64 s28, d2
    VCVT.F64.S32 d2, s28
    LDR r12, =RES_SLOT30
    VSTR d2, [r12]
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
    LDR r12, =C28
    VLDR d0, [r12]
    LDR r12, =C29
    VLDR d1, [r12]
    VDIV.F64 d2, d0, d1
    VCVT.S32.F64 s28, d2
    VCVT.F64.S32 d2, s28
    VMUL.F64 d2, d2, d1
    VSUB.F64 d2, d0, d2
    LDR r12, =RES_SLOT31
    VSTR d2, [r12]
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
    LDR r12, =MEM_MEM
    VLDR d0, [r12]
    LDR r12, =C32
    VLDR d1, [r12]
    LDR r12, =RES_SLOT17
    VLDR d2, [r12]
    VADD.F64 d3, d0, d2
    LDR r12, =RES_SLOT33
    VSTR d3, [r12]
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
    LDR r12, =C34
    VLDR d0, [r12]
    LDR r12, =C35
    VLDR d1, [r12]
    VADD.F64 d2, d0, d1
    LDR r12, =C36
    VLDR d3, [r12]
    LDR r12, =C37
    VLDR d4, [r12]
    VSUB.F64 d5, d3, d4
    VMUL.F64 d6, d2, d5
    LDR r12, =C19
    VLDR d7, [r12]
    VDIV.F64 d8, d6, d7
    LDR r12, =RES_SLOT38
    VSTR d8, [r12]
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
    LDR r12, =C0
    VLDR d0, [r12]
    LDR r12, =C1
    VLDR d1, [r12]
    VCVT.S32.F64 s28, d1
    VMOV r0, s28
    LDR r1, =C4
    VLDR d2, [r1]
POW_L39:
    CMP r0, #0
    BLE POW_E40
    VMUL.F64 d2, d2, d0
    SUB r0, r0, #1
    B POW_L39
POW_E40:
    LDR r12, =C19
    VLDR d3, [r12]
    VDIV.F64 d4, d2, d3
    VCVT.S32.F64 s28, d4
    VCVT.F64.S32 d4, s28
    VMUL.F64 d4, d4, d3
    VSUB.F64 d4, d2, d4
    LDR r12, =RES_SLOT41
    VSTR d4, [r12]
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
    LDR r12, =C42
    VLDR d0, [r12]
    LDR r12, =RES_SLOT27
    VLDR d1, [r12]
    LDR r12, =RES_SLOT43
    VSTR d1, [r12]
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
    LDR r12, =MEM_MEM
    VLDR d0, [r12]
    LDR r12, =C0
    VLDR d1, [r12]
    VMUL.F64 d2, d0, d1
    LDR r12, =RES_SLOT44
    VSTR d2, [r12]
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
    LDR r12, =C45
    VLDR d0, [r12]
    LDR r12, =C46
    VLDR d1, [r12]
    VSUB.F64 d2, d0, d1
    LDR r12, =RES_SLOT47
    VSTR d2, [r12]
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
