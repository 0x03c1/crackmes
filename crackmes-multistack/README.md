# Crackmes multi-stack

Quatro desafios equivalentes em linguagens diferentes, para mostrar que **a
ferramenta de engenharia reversa depende da stack**. Use junto com o
[GUIA-PROFESSOR-PASSO-A-PASSO.md](../GUIA-PROFESSOR-PASSO-A-PASSO.md) (Parte B).

| Pasta | Linguagem | O que ensina | Ferramenta-chave | Senha (gabarito) |
|---|---|---|---|---|
| `cpp/` | C++ | name mangling; senha XOR em runtime | `c++filt`, Ghidra | `Cpp_M4ngl3d!` |
| `python/` | Python (.pyc) | bytecode guarda constantes; string invertida | `strings`, `dis`, decompyle3 | `Pyth0n_R3v3rs3` |
| `java/` | Java (.jar) | bytecode decompila quase 100% | `javap`, jadx/CFR | `J4v4_D3c0mp1l3d` |
| `go/` | Go | binário estático gigante; símbolos vazam | `strings`, GoReSym, Ghidra | `G0_r3v3rs1ng!!` |

## Como compilar (professor)

```bash
# C++  (ELF para a demo no Kali)
g++ -O0 -g -no-pie -o cpp/crackme_cpp cpp/crackme_cpp.cpp
# também para Windows, se quiser distribuir:
x86_64-w64-mingw32-g++ -O0 -static -o cpp/crackme_cpp.exe cpp/crackme_cpp.cpp

# Python -> bytecode (distribua SÓ o .pyc, nunca o .py)
python3 -c "import py_compile; py_compile.compile('python/crackme.py', cfile='python/crackme.pyc')"

# Java -> .jar
( cd java && javac CrackMe.java && jar cfe CrackMe.jar CrackMe CrackMe.class )

# Go (stripped: -s -w)
go build -ldflags "-s -w" -o go/crackme go/crackme.go
# Windows:
GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o go/crackme.exe go/crackme.go
```

> **Importante:** os arquivos `.c/.cpp/.py/.java/.go` são o **gabarito**. Distribua aos
> alunos apenas os **binários compilados** (`crackme_cpp`, `crackme.pyc`, `CrackMe.jar`,
> `crackme`), nunca o código-fonte.

## Dependências

`g++`, `python3`, `default-jdk` (javac/jar/javap), `golang`. Para decompilar:
`ghidra`, `jadx` (`apt install jadx`), `pip install decompyle3`.
