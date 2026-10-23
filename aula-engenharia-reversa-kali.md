# Aula Prática — Engenharia Reversa no Kali Linux

> 📌 **Para executar a aula comando a comando (com a narração de cada saída), use o
> [GUIA-PROFESSOR-PASSO-A-PASSO.md](GUIA-PROFESSOR-PASSO-A-PASSO.md).** Este arquivo é o
> **plano** (objetivos, cronograma, gabarito); o guia é o **teleprompter** da execução.
> Novidades: crackmes multi-stack (C++/Python/Java/Go) em [crackmes-multistack/](crackmes-multistack/)
> e a **prova individual** (1 executável único por aluno) em [prova-individual/](prova-individual/).

**Disciplina:** Segurança da Informação
**Duração:** 2 horas
**Formato:** ~45 min de demonstração (professor) + ~65 min de atividade prática (alunos) + 10 min de correção
**Material do professor:** este roteiro + `GUIA-PROFESSOR-PASSO-A-PASSO.md` + pastas `crackmes/` e `crackmes-multistack/`
**Material do aluno:** `atividade-alunos.md` (sem gabarito) e, na avaliação, `prova-individual/INSTRUCOES-ALUNO.md`

---

## 1. Objetivos de aprendizagem

Ao final da aula, o aluno deverá ser capaz de:

1. Explicar o que é engenharia reversa de software e seus usos legítimos (análise de malware, auditoria, interoperabilidade, CTFs).
2. Diferenciar **análise estática** (sem executar o programa) de **análise dinâmica** (executando/monitorando).
3. Utilizar as ferramentas: `file`, `checksec`, `strings`, `objdump`, `ltrace`, `strace`, `gdb` e **Ghidra**.
4. Aplicar as técnicas para extrair segredos de binários e alterar o fluxo de execução de um programa (patch).

**Pré-requisitos dos alunos:** noções de terminal Linux e lógica de programação (desejável: já ter visto C e assembly x86-64 superficialmente).

---

## 2. Cronograma

| Horário | Duração | Atividade |
|---------|---------|-----------|
| 0:00 – 0:05 | 5 min | Abertura: o que é engenharia reversa, ética e legislação |
| 0:05 – 0:15 | 10 min | **Demo 1** — Análise estática: `file`, `checksec`, `strings` |
| 0:15 – 0:25 | 10 min | **Demo 2** — Análise dinâmica: `strace` e `ltrace` |
| 0:25 – 0:40 | 15 min | **Demo 3** — Depuração com GDB (breakpoint, registradores, forçar fluxo) |
| 0:40 – 0:45 | 5 min | **Demo 4** — Patch permanente do binário (`hexedit` / `r2 -w`) |
| 0:45 – 0:55 | 10 min | **Demo 5** — Decompilação com Ghidra |
| 0:55 – 1:50 | ~55 min | **Atividade prática dos alunos** (4 desafios) |
| 1:50 – 2:00 | 10 min | Correção coletiva e discussão |

---

## 3. Preparação do ambiente (ANTES da aula)

Execute no Kali (ou peça aos alunos para executarem no início):

```bash
# 1. Atualizar e instalar as ferramentas (a maioria já vem no Kali)
sudo apt update
sudo apt install -y gcc make gdb ltrace strace hexedit ghidra radare2 checksec

# 2. Desativar o ASLR (endereços de memória estáveis — facilita a demonstração)
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

# 3. Compilar os desafios
cd crackmes/
make            # gera crackme1, crackme2, crackme3 e crackme4
```

> **Por que `-O0 -g -no-pie` na compilação?** Sem otimização o assembly gerado é fiel ao código C; `-g` mantém os símbolos (nomes de funções) para o GDB; `-no-pie` mantém os endereços fixos, então o endereço visto no `objdump` é o mesmo em execução.

> **Opcional (turmas avançadas):** rode `strip crackme3` para remover símbolos e aumentar a dificuldade.

---

## 4. Roteiro das demonstrações (professor)

### 4.0 Abertura (5 min)

**Talking points:**
- Engenharia reversa = entender como um software funciona **sem ter o código-fonte**.
- Usos legítimos: análise de malware, descoberta de vulnerabilidades, bug bounty, recuperação de sistemas legados, CTF.
- **Ética/lei:** só pratique em binários próprios ou com autorização (no Brasil, art. 154-A do CP — "crime cibernético"). Tudo nesta aula roda em binários criados para fins didáticos.
- Conceito-chave da aula: **análise estática** (olhar o arquivo parado) vs. **análise dinâmica** (olhar o programa rodando).

---

### 4.1 Demo 1 — Análise estática: `file`, `checksec`, `strings` (10 min)

**Alvo:** `crackme1`

```bash
# Que tipo de arquivo é?
file crackme1
# ELF 64-bit LSB pie executable, x86-64, ... not stripped

# Quais proteções o binário tem? (canary, NX, PIE, RELRO)
checksec --file=crackme1

# Executar e errar a senha de propósito
./crackme1

# Extrair as strings legíveis do binário
strings crackme1
# ou filtrando:
strings crackme1 | grep -i "senha\|acesso\|S3"
```

**O que mostrar:** entre as strings aparecem as mensagens do programa **e a senha `Un1r10s_R3v_2026`**, porque o compilador guarda literais de string na seção `.rodata` do ELF. Rode de novo com a senha encontrada → "Acesso concedido".

**Pergunta para a turma:** *"Como um programador esconderia a senha do `strings`?"* → gancho para o crackme2.

---

### 4.2 Demo 2 — Análise dinâmica: `strace` e `ltrace` (10 min)

**Alvo:** `crackme2` (a senha é montada em memória em tempo de execução; `strings` não a revela — mostre isso primeiro!)

```bash
# Provar que a análise estática falhou
strings crackme2 | grep -i "k4l1"   # não encontra nada

# strace: monitora CHAMADAS DE SISTEMA (read, write, open...)
echo "teste" | strace ./crackme2

# ltrace: monitora CHAMADAS DE BIBLIOTECA (printf, strcmp...)
echo "teste" | ltrace ./crackme2
# Saída esperada (destaque):
#   strcmp("teste", "k4l1_r3v") = ...
# => o ltrace interceptou a comparação e revelou a senha!
```

**O que explicar:**
- `strace` → enxerga a conversa do programa com o **kernel** (syscalls).
- `ltrace` → enxerga a conversa do programa com as **bibliotecas** (libc). Como `strcmp` é uma função da libc, o `ltrace` mostra **os dois argumentos**.
- Lição de defesa: comparações com funções de biblioteca são "visíveis" para quem monitora o processo.

---

### 4.3 Demo 3 — Depuração com GDB (15 min)

**Alvo:** `crackme3` (comparação byte a byte em loop → `ltrace` não ajuda)

```bash
# Mostrar que ltrace não revela o serial
echo "AAAA" | ltrace ./crackme3     # sem strcmp na saída

gdb -q ./crackme3
```

Dentro do GDB:

```gdb
(gdb) info functions          # lista as funções (main, validar)
(gdb) disas main              # assembly da main
(gdb) disas validar           # assembly da função de validação
(gdb) break validar           # breakpoint no início da validação
(gdb) run                     # executa; digite um serial qualquer: AAAAAAAA
(gdb) disas                   # mostra onde o programa parou
(gdb) x/s $rbp-0x20           # dica: inspecionar variáveis locais próximas
                              # (o array 'alvo' estará na stack — ajuste o offset
                              #  conforme o disassembly; procure os bytes 'R3V3RS0!')
(gdb) continue
```

**Roteiro da demonstração:**

1. Mostrar no `disas main` a sequência: `call validar` → `test eax, eax` → `je/jne` (desvio condicional que decide "válido" ou "inválido").
2. Breakpoint **logo após** o `call validar`:
   ```gdb
   (gdb) disas main
   # anote o endereço da instrução logo depois de: call <validar>
   (gdb) break *0x0000000000401XXX
   (gdb) run          # digite: AAAAAAAA
   (gdb) p/x $eax     # 0x0  -> função retornou "falso"
   (gdb) set $eax = 1 # "mentimos" para o programa
   (gdb) continue     # [+] Serial válido! Acesso concedido.
   ```
3. Mostrar também como **ler o serial correto da memória**: no disassembly de `validar`, os `mov byte ptr [rbp-X], 0x52` etc. revelam os bytes; ou use `x/s` no endereço do array `alvo` durante a execução. Serial correto: `R3V3RS0!`.

**O que explicar:** o GDB controla a execução — pausar, inspecionar memória/registradores e **alterar** valores em tempo de execução. O desvio condicional (`je`/`jne`) é o "portão" que queremos transpor.

> Dica: quem quiser um GDB mais amigável pode instalar o **GEF**: `bash -c "$(curl -fsSL https://gef.blah.cat/sh)"`

---

### 4.4 Demo 4 — Patch permanente do binário (5 min)

**Alvo:** `crackme3` — tornar o bypass **permanente**, sem GDB.

**Opção A — `hexedit` (visual):**
```bash
objdump -d crackme3 | grep -A2 "call.*validar"
# anote o endereço do 'je'/'jne' logo após o 'test eax,eax'
hexedit crackme3
# Ctrl+W para buscar os bytes (ex.: 74 XX), trocar 74 (JE) por 75 (JNE)
#   -> inverte a lógica: qualquer serial errado passa!
```

**Opção B — `radare2` (uma linha por endereço):**
```bash
r2 -w ./crackme3
[0x00401000]> s 0x00401XXX     # endereço do je
[0x00401XXX]> wx 75            # escreve o byte 0x75 (JNE) por cima do 0x74 (JE)
[0x00401XXX]> q
./crackme3                     # agora qualquer serial é aceito
```

**O que explicar:** `0x74` = JE (jump if equal), `0x75` = JNE. Trocar um único byte inverte a decisão do programa. É exatamente assim que funcionam os "cracks" de software — e por isso existem proteções como assinatura de código e verificação de integridade.

> Para desfazer: `make clean && make` recompila o binário original.

---

### 4.5 Demo 5 — Decompilação com Ghidra (10 min)

**Alvo:** `crackme4` (senha verificada com XOR — exige entender o algoritmo)

1. Abrir o Ghidra → `File > New Project` (non-shared) → arrastar o `crackme4` para o projeto → duplo clique → `Analyze` (Yes, manter padrões).
2. Na árvore de símbolos (Symbol Tree) → `Functions` → `main`.
3. Mostrar a **janela de decompilação** (C pseudo-code) lado a lado com o assembly.
4. Apontar no código decompilado:
   - o array `cifrado` com os bytes `0x24, 0x2e, ...`;
   - o loop `for` com a condição `(senha[i] ^ 0x42) != cifrado[i]`;
   - a checagem `strlen(senha) != 16` (a senha tem 16 caracteres).
5. Resolver ao vivo com a turma:
   ```bash
   python3 -c "
   c = [0x24,0x2e,0x23,0x25,0x39,0x25,0x2a,0x73,0x26,0x30,0x76,0x1d,0x24,0x36,0x35,0x3f]
   print(''.join(chr(b ^ 0x42) for b in c))"
   # => flag{gh1dr4_ftw}
   ```

**O que explicar:** o decompilador "traduz" assembly de volta para algo parecido com C. Não é o código-fonte original, mas é legível o suficiente para entender o algoritmo — e entendendo o algoritmo, revertemos a operação (XOR é reversível: `a ^ b ^ b = a`).

---

## 5. Atividade prática dos alunos (~55 min)

> Distribuir o arquivo **`atividade-alunos.md`** (já pronto nesta pasta, sem gabarito).
> Resumo do que os alunos devem fazer:

| Desafio | Binário | Técnica esperada | Pontos |
|---------|---------|------------------|--------|
| 1 | `crackme1` | `strings` / análise estática | 20 |
| 2 | `crackme2` | `ltrace` / análise dinâmica | 25 |
| 3 | `crackme3` | GDB (ler memória **ou** forçar `eax`) **ou** patch | 30 |
| 4 (bônus) | `crackme4` | Ghidra + reversão do XOR | +25 |

**Regras e entrega:**
- Duplas ou individual. Cada aluno/dupla entrega um relatório curto (PDF ou MD) contendo, **para cada desafio**: a senha/serial encontrado, os comandos utilizados e um print da tela de "Acesso concedido".
- No desafio 3, vale qualquer uma das três abordagens (ler o serial na memória, `set $eax=1` no GDB, ou patch no arquivo) — bônus de criatividade para quem fizer duas.
- Circule pela sala; use as **dicas progressivas** do `atividade-alunos.md` para destravar quem estiver parado há mais de 10 minutos.

---

## 6. Gabarito (SOMENTE PROFESSOR)

### Desafio 1 — `crackme1` → senha: `Un1r10s_R3v_2026`
```bash
strings crackme1 | grep -i un1r10s     # ou simplesmente: strings crackme1
./crackme1   # digite a senha encontrada
```

### Desafio 2 — `crackme2` → senha: `k4l1_r3v`
```bash
strings crackme2          # não revela nada (proposital)
echo "teste" | ltrace ./crackme2
# strcmp("teste", "k4l1_r3v")  <- senha vazou na chamada de biblioteca
```

### Desafio 3 — `crackme3` → serial: `R3V3RS0!` (ou bypass)

**Solução A — ler o serial na memória (GDB):**
```gdb
gdb -q ./crackme3
(gdb) disas validar          # observe os mov byte ptr [rbp-0x..], 0x52/0x33/...
(gdb) break validar
(gdb) run                    # digite qualquer coisa
(gdb) x/s $rbp-0x20          # ajuste o offset conforme o disassembly -> "R3V3RS0!"
```
(Alternativa: break em `main` após `call validar`, `set $eax=1`, `continue`.)

**Solução B — patch do binário:**
```bash
objdump -d crackme3 | grep -A3 "call.*<validar>"
# localize o 'je' (74) ou 'jne' (75) que decide o acesso
hexedit crackme3     # troque 74 <-> 75  (ou substitua por 90 90 = NOP NOP)
./crackme3           # qualquer serial passa
```

### Desafio 4 (bônus) — `crackme4` → senha: `flag{gh1dr4_ftw}`
1. Ghidra → decompilar `main` → identificar o loop `senha[i] ^ 0x42 != cifrado[i]`.
2. Reverter:
```bash
python3 -c "
c = [0x24,0x2e,0x23,0x25,0x39,0x25,0x2a,0x73,0x26,0x30,0x76,0x1d,0x24,0x36,0x35,0x3f]
print(''.join(chr(b ^ 0x42) for b in c))"
# flag{gh1dr4_ftw}
```

---

## 7. Fechamento e discussão (10 min)

Perguntas para a roda de conversa:

1. Qual técnica funcionou em cada desafio e **por quê** as outras falharam?
2. O que o desenvolvedor do crackme2/3 fez para dificultar? Funcionou?
3. Se você fosse proteger um software real, o que faria? (→ ofuscação, packers, checagem de integridade, assinatura de código, anti-debugging...)
4. Como isso se conecta com análise de malware e bug bounty?

**Mensagem final:** a mesma técnica usada para "crackear" um programa é usada defensivamente para entender malware, encontrar vulnerabilidades e auditar software sem código-fonte.

---

## 8. Troubleshooting rápido

| Problema | Solução |
|----------|---------|
| `ltrace: command not found` | `sudo apt install ltrace` |
| Endereços do GDB diferentes do `objdump` | Recompilar com `-no-pie` (o Makefile já faz isso) e desativar ASLR (seção 3) |
| `strings` mostra demais | `strings -n 6 crackme1` filtra strings curtas |
| Ghidra não abre | Requer Java: `sudo apt install default-jdk` |
| Aluno apagou/quebrou o binário | `make clean && make` restaura tudo |

---

## 9. Referência rápida de comandos (cheatsheet)

| Ferramenta | Comando | Para quê |
|------------|---------|----------|
| `file` | `file crackme1` | Identificar o tipo do binário |
| `checksec` | `checksec --file=crackme1` | Ver proteções (NX, PIE, canary) |
| `strings` | `strings crackme1` | Extrair textos legíveis |
| `objdump` | `objdump -d crackme3` | Disassemblar o binário |
| `strace` | `strace ./crackme2` | Monitorar syscalls |
| `ltrace` | `ltrace ./crackme2` | Monitorar chamadas de biblioteca |
| `gdb` | `gdb -q ./crackme3` | Depurar: breakpoints, memória, registradores |
| `hexedit` | `hexedit crackme3` | Editar bytes do arquivo (patch) |
| `radare2` | `r2 -w ./crackme3` | Análise + patch (`s <end>`; `wx 75`) |
| Ghidra | GUI | Decompilação (assembly → pseudo-C) |
