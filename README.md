# Aula de Engenharia Reversa (UNIRIOS)

Material completo para ensinar **engenharia reversa** de forma remota e aplicar uma
**prova individual** para a turma (~43 alunos), em que cada aluno recebe um executável
(`.exe` Windows / `.elf` Linux) e deve **descobrir o conteúdo da senha** embutida.

## Mapa do material

| Arquivo / pasta | Para quem | O que é |
|---|---|---|
| **[GUIA-PROFESSOR-PASSO-A-PASSO.md](GUIA-PROFESSOR-PASSO-A-PASSO.md)** | Professor | **Comece por aqui.** Passo a passo narrado: comando → o que aparece → o que explicar. Cobre os crackmes C e os multi-stack. |
| [aula-engenharia-reversa-kali.md](aula-engenharia-reversa-kali.md) | Professor | Plano de aula: objetivos, cronograma, pré-requisitos, gabarito. |
| [atividade-alunos.md](atividade-alunos.md) | Aluno | Atividade em sala (4 crackmes C) — distribuir **sem** gabarito. |
| [crackmes/](crackmes/) | Professor | Códigos-fonte C (crackme1–4) + Makefile. |
| [crackmes-multistack/](crackmes-multistack/) | Professor | Crackmes equivalentes em **C++, Python, Java, Go**. Veja o [README](crackmes-multistack/README.md). |
| [prova-individual/](prova-individual/) | Professor | Gerador das 43 provas únicas + gabarito. Veja o [LEIAME-PROFESSOR](prova-individual/LEIAME-PROFESSOR.md). |
| [prova-individual/INSTRUCOES-ALUNO.md](prova-individual/INSTRUCOES-ALUNO.md) | Aluno | Como rodar e analisar o binário da prova (Windows/Linux). |

## Fluxo sugerido (aula remota)

1. **Demonstração (professor)** — siga o `GUIA-PROFESSOR-PASSO-A-PASSO.md`, compartilhando a tela.
   Parte A (crackmes C) + Parte B (multi-stack).
2. **Atividade em sala (alunos)** — distribua `atividade-alunos.md` + os binários de `crackmes/`.
3. **Prova individual (avaliação)** — entregue a cada aluno **o binário dele** de
   `prova-individual/dist/` + o `INSTRUCOES-ALUNO.md`. Corrija pelo `gabarito.csv`.

## Gerar os binários (resumo)

```bash
# crackmes C
cd crackmes && make && cd ..

# crackmes multi-stack (veja crackmes-multistack/README.md)
# ... g++, python3, javac/jar, go ...

# 43 provas individuais (Windows + Linux) + gabarito
cd prova-individual && python3 gerar_provas.py --seed 2026
```

> **Regra de ouro:** distribua aos alunos **apenas os binários compilados**.
> Os `.c/.cpp/.py/.java/.go`, o `src/` e o `gabarito.csv` são **gabarito** — não compartilhe.

## Ferramentas usadas na aula

`file`, `strings`, `checksec`, `objdump`, `strace`, `ltrace`, `gdb`, `hexedit`,
`radare2`, **Ghidra**, `c++filt`, `javap`/`jadx`, `python3 -m dis`/`decompyle3`, GoReSym.

## Ética

Todo o material é **didático**. Pratique engenharia reversa apenas em binários próprios
ou com autorização (Brasil: art. 154-A do Código Penal).
