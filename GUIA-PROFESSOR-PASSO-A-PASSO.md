# Guia do Professor — Passo a Passo Narrado (Aula ao vivo / remota)

> **Como usar este guia:** é o seu "teleprompter". Cada bloco traz, nesta ordem:
> **① o comando** que você digita no terminal (compartilhando a tela) →
> **② o que aparece** (para você não ser pego de surpresa) →
> **③ o que explicar** para a turma enquanto a saída está no telão.
> Vá devagar: digite, deixe a saída aparecer, **leia a saída junto com a turma** e só então explique.

**Dica para aula remota:** aumente a fonte do terminal (`Ctrl+Shift++`), use tema de alto contraste e, ao rodar um comando, **pause e pergunte** "o que vocês acham que vai aparecer?" antes de apertar Enter. Isso mantém a turma ativa.

---

## 0. Preparação (fazer ANTES de começar a gravar/compartilhar)

```bash
# Ferramentas (a maioria já vem no Kali)
sudo apt update
sudo apt install -y gcc g++ make gdb ltrace strace hexedit ghidra radare2 checksec \
                    default-jdk python3 golang binutils

# Endereços de memória estáveis (facilita o GDB na demo)
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

# Compilar os crackmes em C (crackme1..4)
cd crackmes/ && make && cd ..

# Compilar os crackmes multi-stack (C++, Python, Java, Go)
cd crackmes-multistack/
g++  -O0 -g -no-pie -o cpp/crackme_cpp cpp/crackme_cpp.cpp
python3 -c "import py_compile; py_compile.compile('python/crackme.py', cfile='python/crackme.pyc')"
( cd java && javac CrackMe.java && jar cfe CrackMe.jar CrackMe CrackMe.class )
go build -ldflags "-s -w" -o go/crackme go/crackme.go
cd ..
```

> **Teste rápido antes da aula:** rode cada binário uma vez com a senha correta (veja o
> quadro de gabarito no fim deste guia) e confirme que aparece `[+] Acesso concedido!`.
> Se algo falhar, resolva **agora**, não no ar.

**Abra o terminal já dentro da pasta certa** e deixe um segundo terminal aberto para o GDB/Ghidra.

---

## 1. Abertura (5 min) — o que dizer antes de qualquer comando

- "Engenharia reversa é entender como um programa funciona **sem ter o código-fonte**."
- Usos legítimos: **análise de malware, bug bounty, auditoria, CTF, interoperabilidade**.
- **Ética/lei:** só em binários próprios ou com autorização (Brasil: art. 154-A do CP). Tudo aqui é didático.
- Conceito-chave do dia: **análise estática** (olhar o arquivo parado) × **análise dinâmica** (olhar o programa rodando).
- "Vamos ver que **cada linguagem esconde — ou entrega — seus segredos de um jeito diferente**."

---

# PARTE A — Crackmes em C (`crackmes/`)

## A.1 — `crackme1`: a senha em texto puro (análise estática)

### ① Comando
```bash
file crackme1
```
### ② O que aparece
```
crackme1: ELF 64-bit LSB executable, x86-64, ... not stripped
```
### ③ O que explicar
"É um executável **ELF** de 64 bits, **not stripped** (ainda tem os nomes das funções). Antes de abrir, sempre pergunte ao arquivo *o que ele é*."

---
### ① Comando
```bash
./crackme1          # digite uma senha qualquer: teste
```
### ② O que aparece
```
=== CRACKME 1 ===
Digite a senha: teste
[-] Acesso negado.
```
### ③ O que explicar
"Ele compara minha entrada com uma senha que **está dentro do arquivo**. Onde o compilador guarda textos? Numa seção chamada `.rodata`. Vamos ler."

---
### ① Comando
```bash
strings crackme1 | grep -i "senha\|s3\|acesso"
```
### ② O que aparece (destaque)
```
Digite a senha:
[+] Acesso concedido!
Un1r10s_R3v_2026
```
### ③ O que explicar
"A senha **`Un1r10s_R3v_2026`** estava escrita em texto puro! `strings` extrai toda sequência legível do binário. Lição: **nunca** guarde segredo como string literal."

### ✅ Fechamento do desafio
```bash
./crackme1          # agora digite Un1r10s_R3v_2026  ->  [+] Acesso concedido!
```
**Gancho:** "E se o programador montasse a senha letra por letra, para o `strings` não ver? → crackme2."

---

## A.2 — `crackme2`: senha montada em runtime (análise dinâmica / `ltrace`)

### ① Comando — provar que a estática falha
```bash
strings crackme2 | grep -i "k4l1"
```
### ② O que aparece
```
(nada)
```
### ③ O que explicar
"Dessa vez `strings` **não acha nada** — a senha é montada caractere a caractere na memória. A estática falhou. Hora de olhar o programa **rodando**."

---
### ① Comando
```bash
echo "teste" | ltrace ./crackme2
```
### ② O que aparece (destaque)
```
...
strcmp("teste", "k4l1_r3v")   = -1
...
```
### ③ O que explicar
"`ltrace` intercepta as **chamadas de biblioteca** (libc). Quando o programa chamou `strcmp`, o `ltrace` mostrou **os dois argumentos** — e o segundo é a senha: **`k4l1_r3v`**. Compare com `strace`, que mostra as *syscalls* (conversa com o kernel), não as funções da libc."

### ✅ Fechamento
```bash
echo "k4l1_r3v" | ./crackme2    #  [+] Acesso concedido!
```
**Gancho:** "E se não houvesse `strcmp`? Se a comparação fosse feita byte a byte, na mão? → crackme3."

---

## A.3 — `crackme3`: GDB e patch (sem `strcmp`)

### ① Comando — mostrar que o ltrace agora não ajuda
```bash
echo "AAAAAAAA" | ltrace ./crackme3
```
### ② O que aparece
```
(sem strcmp na saída — só puts/printf)
```
### ③ O que explicar
"A comparação virou um **laço byte a byte** dentro da função `validar`. Sem `strcmp`, o `ltrace` não revela o serial. Vamos **abrir o capô** com o GDB."

---
### ① Comando
```bash
gdb -q ./crackme3
```
Dentro do GDB:
```gdb
(gdb) info functions
(gdb) disas main
```
### ② O que aparece (trecho-chave do `disas main`)
```
  ... call   0x40xxxx <validar>
  ... test   eax, eax
  ... je     0x40xxxx        <- o "portão": pula se validar() deu 0
```
### ③ O que explicar
"Veja a sequência `call validar` → `test eax,eax` → `je`. Esse **desvio condicional** é o portão que decide 'válido' ou 'inválido'. Temos 3 formas de passar."

---
**Via (b) — mentir sobre o retorno (a mais didática ao vivo):**
```gdb
(gdb) break *main+NN        # endereço LOGO APÓS o 'call validar' (veja no disas)
(gdb) run                   # digite: AAAAAAAA
(gdb) p/x $eax              # $1 = 0x0   -> validar() retornou "falso"
(gdb) set $eax = 1          # mentimos para o programa
(gdb) continue
```
### ② O que aparece
```
[+] Serial válido! Acesso concedido.
```
### ③ O que explicar
"O GDB **pausa, inspeciona e altera** a execução. Mudamos o resultado de `validar()` de 0 para 1 e o programa nos deixou entrar — sem nunca saber o serial."

---
**Via (a) — ler o serial correto da memória:**
```gdb
(gdb) disas validar         # repare nos 'mov byte ptr [rbp-0x..], 0x52' etc.
(gdb) break validar
(gdb) run                   # digite qualquer coisa
(gdb) x/s $rbp-0x20         # ajuste o offset conforme o disas -> "R3V3RS0!"
```
### ③ O que explicar
"Cada `mov byte ptr [...], 0x52` escreve um caractere ASCII (`0x52`='R'). Lendo a memória durante a execução, recuperamos o serial: **`R3V3RS0!`**."

### ✅ Fechamento
```gdb
(gdb) quit
```
```bash
echo "R3V3RS0!" | ./crackme3     #  [+] Serial válido!
```

---

## A.4 — `crackme3` vira "crack": patch permanente (5 min)

### ① Comando
```bash
objdump -d crackme3 | grep -A3 "call.*<validar>"
```
### ② O que aparece
```
  ... call   <validar>
  ... test   eax,eax
  ... 74 XX  je ...          <- 0x74 = JE
```
### ③ O que explicar
"`0x74` é o opcode do **JE** (jump if equal). Se eu trocar por `0x75` (**JNE**), inverto a decisão: qualquer serial errado passa."

### ① Comando — patch com radare2
```bash
r2 -w ./crackme3
[0x...]> s 0x40xxxx      # endereço do 'je'
[0x...]> wx 75           # grava 0x75 por cima do 0x74
[0x...]> q
./crackme3               # agora QUALQUER serial é aceito
```
### ③ O que explicar
"Trocamos **1 byte** e o programa está 'crackeado'. É assim que funcionam cracks reais — e por isso existem **assinatura de código e verificação de integridade**."
> Para restaurar: `cd crackmes && make clean && make`.

---

## A.5 — `crackme4`: Ghidra + XOR (bônus)

### ① Comando
```bash
ghidra &      # abre a GUI; crie um projeto, importe crackme4, Analyze (Yes)
```
### ③ O que explicar (navegando na GUI)
"No **Symbol Tree → Functions → main**, a janela **Decompile** traduz o assembly de volta para um pseudo-C legível. Procurem o laço."
### ② O que aparece no decompilado (essência)
```c
if ((senha[i] ^ 0x42) != cifrado[i]) { ... "Acesso negado" ... }
```
### ③ O que explicar
"A senha é verificada com **XOR 0x42**. XOR é **reversível**: se `senha ^ 0x42 == cifrado`, então `senha == cifrado ^ 0x42`. Vamos reverter."

### ① Comando — resolver ao vivo
```bash
python3 -c "
c=[0x24,0x2e,0x23,0x25,0x39,0x25,0x2a,0x73,0x26,0x30,0x76,0x1d,0x24,0x36,0x35,0x3f]
print(''.join(chr(b ^ 0x42) for b in c))"
```
### ② O que aparece
```
flag{gh1dr4_ftw}
```
### ③ O que explicar
"O decompilador não dá o código-fonte original, mas dá **o algoritmo** — e entendendo o algoritmo, nós o invertemos. Senha: **`flag{gh1dr4_ftw}`**."

---

# PARTE B — Crackmes multi-stack (`crackmes-multistack/`)

> **Mensagem desta parte:** "A ferramenta certa depende da linguagem. Binário nativo (C/C++/Go) pede
> `strings`/GDB/Ghidra; **bytecode** (Java/Python) pede **decompilador** — e muitas vezes devolve quase o código-fonte."

## B.1 — C++ (`cpp/crackme_cpp`): name mangling

### ① Comando
```bash
cd crackmes-multistack/cpp
strings crackme_cpp | grep -i "Cpp_M4ngl3d"
```
### ② O que aparece
```
(nada)
```
### ③ O que explicar
"Aqui a senha está **cifrada (XOR)** e montada em runtime — `strings` não acha. Mas o C++ deixa outra pista: os **nomes das funções 'mangled'**."

---
### ① Comando
```bash
strings crackme_cpp | grep "_Z"
```
### ② O que aparece
```
_Z13montarSegredov
...
```
### ③ O que explicar
"`_Z13montarSegredov` é **name mangling**: o C++ codifica o nome e os tipos dos parâmetros no símbolo. Uma função chamada 'montarSegredo' é suspeita! Vamos **demanglar**."

---
### ① Comando
```bash
echo "_Z13montarSegredov" | c++filt
```
### ② O que aparece
```
montarSegredo()
```
### ③ O que explicar
"`c++filt` reverte o mangling. Agora abrimos no **Ghidra** → função `montarSegredo` → vemos o laço `b ^ 0x37` reconstruindo a senha. Revertendo: **`Cpp_M4ngl3d!`**."
```bash
# conferência:
python3 -c "print(''.join(chr(b^0x37) for b in [0x74,0x47,0x47,0x68,0x7a,0x03,0x59,0x50,0x5b,0x04,0x53,0x16]))"
# Cpp_M4ngl3d!
echo "Cpp_M4ngl3d!" | ./crackme_cpp     #  [+] Acesso concedido!
cd ../..
```

---

## B.2 — Python (`python/crackme.pyc`): bytecode não é segredo

> Entregue ao aluno **só o `.pyc`**, nunca o `.py`.

### ① Comando
```bash
cd crackmes-multistack/python
file crackme.pyc
strings crackme.pyc | grep -i "3sr3v3R\|htyP"
```
### ② O que aparece
```
crackme.pyc: data
3sr3v3R_n0htyP
```
### ③ O que explicar
"O `.pyc` é **bytecode**, não código-fonte. Mas as **constantes de string sobrevivem**: apareceu `3sr3v3R_n0htyP`. Está **invertida** (de trás pra frente). Quem lê ao contrário? `Pyth0n_R3v3rs3`."

---
### ① Comando — desmontar o bytecode de verdade
```bash
python3 -c "import dis,marshal; f=open('crackme.pyc','rb'); f.read(16); dis.dis(marshal.load(f))"
```
### ② O que aparece (trecho)
```
  LOAD_CONST   '3sr3v3R_n0htyP'
  ...
  <slice / subscript com passo -1>   # a inversão [::-1]
```
### ③ O que explicar
"`dis` mostra as instruções da máquina virtual do Python. Vemos a string sendo **carregada e invertida** (`[::-1]`). Para recuperar o código quase inteiro, existe o **decompyle3/uncompyle6** (`pip install decompyle3`). Senha: **`Pyth0n_R3v3rs3`**."
```bash
echo "Pyth0n_R3v3rs3" | python3 crackme.pyc     #  [+] Acesso concedido!
cd ../..
```

---

## B.3 — Java (`java/CrackMe.jar`): decompilação quase perfeita

### ① Comando
```bash
cd crackmes-multistack/java
javap -c -p CrackMe        # o .jar contém CrackMe.class; aqui usamos o .class extraído
```
### ② O que aparece (trecho-chave)
```
  getstatic  CIFRADO:[I
  ...
  ixor                     # <- o XOR da verificação aparece no bytecode
```
### ③ O que explicar
"`javap` é o 'disassembler' oficial do Java. Dá para ver o array `CIFRADO` e a instrução `ixor`. Mas o Java vai além: **jadx** devolve algo quase idêntico ao fonte."

---
### ① Comando (se tiver jadx; senão, mostre o `javap` acima)
```bash
jadx CrackMe.jar -d saida_jadx   # pip/apt: apt install jadx
cat saida_jadx/sources/CrackMe.java
```
### ② O que aparece
```java
private static final int[] CIFRADO = {0x1f,0x61,...,0x31};
... (entrada.charAt(i) ^ 0x55) != CIFRADO[i] ...
```
### ③ O que explicar
"O decompilador Java reconstrói o código praticamente inteiro — chave `0x55`, array cifrado, tudo. Revertendo o XOR achamos a senha: **`J4v4_D3c0mp1l3d`**."
```bash
python3 -c "print(''.join(chr(b^0x55) for b in [0x1f,0x61,0x23,0x61,0x0a,0x11,0x66,0x36,0x65,0x38,0x25,0x64,0x39,0x66,0x31]))"
# J4v4_D3c0mp1l3d
echo "J4v4_D3c0mp1l3d" | java -jar CrackMe.jar     #  [+] Acesso concedido!
cd ../..
```

---

## B.4 — Go (`go/crackme`): binário gigante e estático

### ① Comando
```bash
cd crackmes-multistack/go
file crackme
ls -lh crackme
```
### ② O que aparece
```
crackme: ELF 64-bit LSB executable, x86-64, statically linked, ... stripped
-rwxr-xr-x  ...  ~1.8M crackme
```
### ③ O que explicar
"Binário Go é **estático** (carrega o runtime inteiro) e **gigante** — por isso ~2 MB para um 'hello'. Mesmo **stripped**, o Go deixa seus próprios metadados."

---
### ① Comando
```bash
strings crackme | grep "main\."
```
### ② O que aparece
```
main.main
main.verifica
```
### ③ O que explicar
"Mesmo sem símbolos de debug, os nomes `main.verifica`/`main.main` vazam (o runtime do Go precisa deles). Ferramentas como **GoReSym** recuperam ainda mais. A senha em si está XOR — `strings` não a mostra:"
```bash
strings crackme | grep -F "G0_r3v3rs1ng" || echo "(senha nao vaza — esta cifrada)"
```
### ③ O que explicar (fechamento)
"Abrindo `main.verifica` no Ghidra vemos o laço `entrada[i] ^ 0x33 == cifrado[i]`. Revertendo: **`G0_r3v3rs1ng!!`**."
```bash
python3 -c "print(''.join(chr(b^0x33) for b in [0x74,0x03,0x6c,0x41,0x00,0x45,0x00,0x41,0x40,0x02,0x5d,0x54,0x12,0x12]))"
# G0_r3v3rs1ng!!
echo "G0_r3v3rs1ng!!" | ./crackme     #  [+] Acesso concedido!
cd ../..
```

---

## 2. Fechamento e discussão (10 min)

Perguntas para a roda:
1. Qual técnica funcionou em cada linguagem e **por que** as outras falharam?
2. Onde `strings` bastou? Onde foi preciso **decompilar** (Java/Python)? Onde foi preciso **debugar/decompilar nativo** (C/C++/Go)?
3. O que o desenvolvedor fez para dificultar (XOR, montar em runtime, strip)? Funcionou?
4. Como proteger software real? → ofuscação, packers, anti-debug, assinatura de código, verificação de integridade.
5. **Conexão final:** a mesma técnica que "crackeia" um programa é a que analisa **malware** e encontra **vulnerabilidades**.

Em seguida → **aplicar a prova individual** (`prova-individual/`): cada aluno recebe um executável com senha única. Veja `prova-individual/LEIAME-PROFESSOR.md`.

---

## 3. Quadro-resumo de gabarito (SÓ PROFESSOR)

| Desafio | Pasta | Técnica | Senha |
|---|---|---|---|
| crackme1 | `crackmes/` | `strings` | `Un1r10s_R3v_2026` |
| crackme2 | `crackmes/` | `ltrace` | `k4l1_r3v` |
| crackme3 | `crackmes/` | GDB / patch | `R3V3RS0!` (ou bypass) |
| crackme4 | `crackmes/` | Ghidra + XOR 0x42 | `flag{gh1dr4_ftw}` |
| C++ | `crackmes-multistack/cpp/` | `c++filt` + Ghidra (XOR 0x37) | `Cpp_M4ngl3d!` |
| Python | `crackmes-multistack/python/` | `strings`/`dis` (string invertida) | `Pyth0n_R3v3rs3` |
| Java | `crackmes-multistack/java/` | `javap`/jadx (XOR 0x55) | `J4v4_D3c0mp1l3d` |
| Go | `crackmes-multistack/go/` | `strings`/Ghidra (XOR 0x33) | `G0_r3v3rs1ng!!` |

---

## 4. Troubleshooting ao vivo

| Problema | Solução rápida |
|---|---|
| Endereços do GDB diferentes do `objdump` | Recompile `-no-pie` (o Makefile já faz) e desative ASLR (seção 0) |
| `ltrace` não mostra `strcmp` | No crackme3 é esperado (comparação byte a byte) — use GDB |
| `python3 -m dis crackme.pyc` dá erro | Use o one-liner com `marshal` (seção B.2) — `-m dis` não lê `.pyc` direto |
| `jadx` não instalado | Mostre `javap -c -p CrackMe` (já ilustra o `ixor`) |
| Ghidra não abre | `sudo apt install default-jdk` |
| Binário quebrado após patch | `cd crackmes && make clean && make` |
