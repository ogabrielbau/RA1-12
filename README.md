# Compilador RPN → Assembly ARMv7

## Informações do Projeto

**Alunos**

| Nome | GitHub |
|------|--------|
| Andrei Silva Martins | @S1VM4 |
| Artur Pandolfo Meneghete | @arturpandolfo |
| Gabriel Baú Herkert | @ogabrielbau |
| Matheus Melara Girardi | @blaugi |

---

## Descrição

Programa em Python que:
1. Lê expressões aritméticas em notação polonesa reversa (RPN) de um arquivo `.txt`
2. Analisa os tokens usando um analisador léxico baseado em autômatos finitos determinísticos (AFD)
3. Executa as expressões e exibe os resultados no terminal
4. Gera código Assembly ARMv7 compatível com o **CPUlator DE1-SoC (v16.1)**
5. Exibe os resultados via **JTAG UART** no simulador


## Como Executar

### 1. Abra o terminal (PowerShell no Windows)

### 2. Navegue até a pasta correta

```bash
cd caminho\para\RA1-12\
```

Exemplo no Windows:
```bash
cd C:\Users\seu_usuario\Documents\RA1-12\
```

### 3. Execute o programa passando o arquivo de teste como argumento

```bash
python src/rpn_compiler/main.py tests/teste1.txt
```

```bash
python src/rpn_compiler/main.py tests/teste2.txt
```

```bash
python src/rpn_compiler/main.py tests/teste3.txt
```

### 4. Resultado

O terminal vai exibir os resultados de cada expressão:

```
=======================================================
          Resultados das expressoes RPN
=======================================================
  Nota: (N RES) retorna o resultado da linha N
=======================================================
  Expr  1: ((1 3 *)((15 2 +) 4 -) /)
          -> 0.2
  Expr  2: (3 2 //)
          -> 1
  ...
=======================================================
  Total: 10 expressao(oes) processada(s)
=======================================================

Assembly gerado: teste1.s
```

E um arquivo `.s` será criado na pasta `RA1-12` com o Assembly gerado.

---


## Sintaxe da Linguagem RPN

Cada linha do arquivo de entrada contém uma expressão RPN entre parênteses.


### Comandos especiais

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `(V MEM)` | Armazena o valor V na variável MEM | `(3.14 MEM)` |
| `(MEM)` | Retorna o valor armazenado em MEM | `(MEM)` |
| `(N RES)` | Retorna o resultado da linha N | `(1 RES)` |
