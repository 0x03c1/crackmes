# Atividade Prática — Engenharia Reversa no Kali Linux

**Nome(s):** ______________________________________
**Tempo:** ~55 minutos **Entrega:** relatório (PDF ou MD) ao final da aula

---

## Missão

Você recebeu 4 programas (`crackme1` a `crackme4`). Cada um exige uma senha/serial
que você **não conhece**. Sua missão é usar as técnicas de engenharia reversa
demonstradas na aula para descobrir as credenciais — ou fazer o programa aceitar
qualquer entrada. **Não é permitido olhar os arquivos `.c`** (eles são o "gabarito"
do professor). Vale apenas o que você extrair dos binários.

## O que entregar (para CADA desafio)

1. A senha/serial encontrado **ou** descrição do bypass aplicado;
2. Os comandos exatos que você utilizou;
3. Um print da tela mostrando `[+] Acesso concedido!`.

---

## Desafio 1 — `crackme1` (20 pontos)

> "Às vezes o segredo está escrito em texto puro."

```bash
./crackme1        # tente uma senha qualquer primeiro
```

**Tarefa:** descubra a senha usando apenas **análise estática**.
Dica: `file`, `strings`.

**Senha encontrada:** ______________________________

---

## Desafio 2 — `crackme2` (25 pontos)

> "Desta vez, o programador escondeu a senha do `strings`..."

**Tarefa:** confirme que a análise estática falha e use **análise dinâmica**
para interceptar a comparação da senha enquanto o programa roda.
Dica: `ltrace` intercepta chamadas de biblioteca como `strcmp`.

**Senha encontrada:** ______________________________

---

## Desafio 3 — `crackme3` (30 pontos)

> "Sem `strcmp`, sem `ltrace`. Hora de abrir o capô."

**Tarefa:** obtenha o "Acesso concedido" por **pelo menos uma** das vias:

- **(a)** Use o **GDB** para inspecionar a memória durante a execução de
  `validar()` e descobrir o serial correto;
- **(b)** Use o **GDB** para alterar o valor de retorno da função
  (dica: `set $eax = 1` logo após o `call validar`);
- **(c)** Aplique um **patch** no binário, invertendo o desvio condicional
  (`74` ↔ `75`) com `hexedit` ou `r2 -w`.

Fez por mais de uma via? Descreva — vale pontos extras de criatividade.

**Serial / método utilizado:** ______________________________

---

## Desafio 4 (BÔNUS, +25 pontos) — `crackme4`

> "A senha não existe em lugar nenhum. Só existe um algoritmo."

**Tarefa:** abra o binário no **Ghidra**, decompile a função `main`,
entenda o algoritmo de verificação (preste atenção no operador `^`)
e **calcule** a senha original. Dica: XOR é reversível; um script de
3 linhas em Python resolve.

**Senha encontrada:** ______________________________

---

## Dicas progressivas (só olhe se travar!)

<details>
<summary>Desafio 1</summary>

1. Toda string literal de um programa C vai parar dentro do arquivo binário.
2. `strings crackme1` lista todos os textos legíveis — procure algo com
   formato de senha entre as mensagens do programa.

</details>

<details>
<summary>Desafio 2</summary>

1. `strings crackme2` — a senha aparece? Por quê não?
2. O programa precisa **comparar** sua entrada com a senha correta. Com que
   função da libc isso normalmente é feito?
3. `echo "teste" | ltrace ./crackme2` — observe os argumentos da comparação.

</details>

<details>
<summary>Desafio 3</summary>

1. `gdb -q ./crackme3` → `info functions` → `disas validar`.
2. No disassembly de `validar`, procure instruções `mov byte ptr [rbp-0x..], 0x..`
   — cada constante hexadecimal é um caractere ASCII da senha (use
   `man ascii` ou uma tabela ASCII para converter).
3. Alternativa: breakpoint logo após `call <validar>` em `main`,
   `p/x $eax`, `set $eax = 1`, `continue`.
4. Para o patch: `objdump -d crackme3 | grep -A3 "call.*validar"` e troque
   o byte do salto condicional.

</details>

<details>
<summary>Desafio 4</summary>

1. Ghidra → importar `crackme4` → Analyze → Functions → main → janela Decompile.
2. O programa faz: `senha[i] ^ 0x42` e compara com um byte do array `cifrado`.
   Logo, `senha[i] = cifrado[i] ^ 0x42`.
3. A senha tem 16 caracteres (veja o `strlen` no decompilado).
4. Resolva com:
   ```python
   python3 -c "c=[0x24,0x2e,0x23,0x25,0x39,0x25,0x2a,0x73,0x26,0x30,0x76,0x1d,0x24,0x36,0x35,0x3f]; print(''.join(chr(b^0x42) for b in c))"
   ```
   (entenda o script antes de rodar!)

</details>

---

## Pontuação

| Desafio | Pontos | Nota |
|---------|:------:|:----:|
| 1 — Análise estática | 20 | |
| 2 — Análise dinâmica | 25 | |
| 3 — GDB / Patch | 30 | |
| Relatório (organização, comandos, prints) | 25 | |
| 4 — Bônus (Ghidra + XOR) | +25 | |
| **Total** | **100 (+25)** | |
