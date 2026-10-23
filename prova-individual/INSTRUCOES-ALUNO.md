# Prova Individual — Engenharia Reversa (Aluno)

Você recebeu **um executável** com uma senha secreta embutida. A senha **não aparece
em texto puro** (ela está cifrada dentro do programa). Sua missão é usar as técnicas
da aula para **descobrir o conteúdo da senha** e informá-la no relatório.

- Alunos de **Windows** receberam um arquivo `.exe`.
- Alunos de **Linux/Kali** receberam um arquivo `.elf`.

O formato da senha é: `UNIRIOS{...}`.

## O que entregar (relatório em PDF ou MD)

1. **A senha** que você descobriu (o conteúdo dentro de `UNIRIOS{...}`);
2. **Os comandos/passos** que você usou para chegar nela;
3. Um **print** mostrando `[+] Acesso concedido! Senha correta.`

## Como executar o seu binário

**Linux / Kali:**
```bash
chmod +x prova_aXX.elf
./prova_aXX.elf
```
**Windows (Prompt de Comando ou PowerShell):**
```cmd
prova_aXX.exe
```
Ao digitar a senha certa, aparece `[+] Acesso concedido!`.

## Como descobrir a senha (dicas progressivas)

> `strings` **sozinho não resolve** desta vez — a senha está cifrada (XOR). Você vai
> precisar olhar o **algoritmo** de verificação. Qualquer uma das vias abaixo vale.

<details>
<summary>Via 1 — Ghidra (recomendada)</summary>

1. Abra o Ghidra, crie um projeto, importe seu binário e mande **Analyze**.
2. Vá em `Functions → main` e abra a janela **Decompile**.
3. Procure: um **array de bytes** (`cifrado[]`), uma **chave** (ex.: `0x..`) e um laço
   comparando `entrada[i] ^ chave` com `cifrado[i]`.
4. XOR é reversível: `senha[i] = cifrado[i] ^ chave`. Calcule, por exemplo:
   ```bash
   python3 -c "c=[0x.., 0x.., ...]; k=0x..; print(''.join(chr(b^k) for b in c))"
   ```
</details>

<details>
<summary>Via 2 — GDB (Linux): ler a senha na memória</summary>

1. `gdb -q ./prova_aXX.elf` → `info functions` → `disas main`.
2. Coloque um breakpoint no laço de comparação e inspecione a memória onde a senha
   é reconstruída (`x/s` no endereço, ou examine os registradores durante o XOR).
</details>

<details>
<summary>Via 3 — objdump / radare2: ler os bytes e a chave do disassembly</summary>

1. `objdump -d prova_aXX.elf | less` (ou `r2 prova_aXX.elf` → `aaa` → `pdf @ main`).
2. Localize os bytes cifrados e a constante do XOR; reverta com o one-liner de Python acima.
</details>

## Ferramentas (se você não usa Kali)

- **Windows/macOS:** instale o **Ghidra** (precisa de Java/JDK) — funciona nos três SOs.
- Alternativa: rode seu binário dentro de uma **VM Kali** ou no **WSL** (Windows).
- `python3` para reverter o XOR (vem no Linux/macOS; no Windows, instale pela Microsoft Store).

**Importante:** descubra a senha **pelo binário** — a graça é a engenharia reversa, não
adivinhar. Bônus para quem resolver por **duas** vias diferentes e documentar.
