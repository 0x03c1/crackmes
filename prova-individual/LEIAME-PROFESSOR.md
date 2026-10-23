# Prova Individual — Leia-me do Professor

Cada aluno recebe **um** executável com uma **senha única embutida (XOR)**. Como a
senha não aparece no `strings`, o aluno precisa aplicar as técnicas da aula
(Ghidra / GDB / objdump / radare2) para recuperá-la e **informar o conteúdo** no relatório.

## Conteúdo

```
prova-individual/
├── gerar_provas.py          # gerador (reexecutável)
├── roster.txt               # lista de alunos (1 nome por linha) — opcional
├── gabarito.csv             # id, nome, senha, chave_xor, arquivos   <- SÓ PROFESSOR
├── src/                     # fontes .c geradas (gabarito) — NÃO distribuir
└── dist/
    ├── windows/prova_aXX.exe   # entregar a alunos de Windows
    └── linux/prova_aXX.elf     # entregar a alunos de Linux
```

## 1. Associar nomes aos binários (recomendado)

Por padrão os binários são `prova_a01 .. prova_a43` (genéricos). Para pôr os nomes reais:

```bash
# edite roster.txt com um nome por linha (na ordem desejada), depois:
python3 gerar_provas.py          # regenera tudo a partir do roster.txt
```

O `gabarito.csv` passa a mapear **nome → senha → arquivo**. Exemplo:

| id | nome | senha | arquivo_windows | arquivo_linux |
|----|------|-------|-----------------|---------------|
| a01 | Maria Silva | UNIRIOS{a01_hu66go} | dist/windows/prova_a01.exe | dist/linux/prova_a01.elf |

> **Reprodutibilidade:** `gerar_provas.py --seed 2026` sempre gera as mesmas senhas.
> Sem `--seed`, cada execução gera senhas novas (útil para outra turma).

## 2. Distribuir

- Entregue a **cada aluno apenas o arquivo dele**, conforme o SO:
  - Windows → `dist/windows/prova_aXX.exe`
  - Linux (ou Kali/WSL) → `dist/linux/prova_aXX.elf`
- Canais sugeridos: pasta individual no Google Drive/Classroom, ou link direto por aluno.
- **Não** distribua `src/`, `gabarito.csv` nem este arquivo.

## 3. Corrigir

O aluno entrega: (a) a senha encontrada, (b) os comandos usados, (c) print do
`[+] Acesso concedido!`. Para conferir:

```bash
# conferência automática de um aluno (roda o binário dele com a senha do gabarito)
id=a07
senha=$(awk -F, -v i=$id '$1==i{print $3}' gabarito.csv)
echo "$senha" | ./dist/linux/prova_$id.elf      # deve dar [+] Acesso concedido!
```

Critério sugerido (100 pts): senha correta **40** · comandos/metodologia **35** ·
print e organização do relatório **25**. Bônus: quem documentar **duas** vias
(ex.: achar a senha por Ghidra **e** por patch/bypass).

## 4. Regenerar / turma nova

```bash
python3 gerar_provas.py --n 43                 # 43 genéricos, senhas novas
python3 gerar_provas.py --roster outra_turma.txt
python3 gerar_provas.py --seed 2026            # mesmas senhas de sempre
```

Requisitos do gerador (já instalados): `x86_64-w64-mingw32-gcc` (.exe) e `zig` (.elf).
