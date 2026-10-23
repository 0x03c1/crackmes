#!/usr/bin/env python3
"""
gerar_provas.py — Gera uma prova individual por aluno para a atividade de
Engenharia Reversa (UNIRIOS). Cada aluno recebe um executável (.exe para Windows
e .elf para Linux) com uma SENHA ÚNICA embutida de forma ofuscada (XOR), de modo
que `strings` não a revele — o aluno precisa aplicar as técnicas da aula
(Ghidra/GDB/objdump) para recuperá-la e informar o conteúdo.

Saídas:
  dist/windows/prova_<id>.exe
  dist/linux/prova_<id>.elf
  gabarito.csv            (id, nome, senha, chave_xor, arquivos)  <- SÓ PROFESSOR

Uso:
  python3 gerar_provas.py                      # usa roster.txt (ou gera aluno-01..43)
  python3 gerar_provas.py --n 43               # ignora roster, cria 43 genéricos
  python3 gerar_provas.py --roster alunos.txt  # um nome por linha

Requisitos (já instalados nesta máquina):
  - x86_64-w64-mingw32-gcc  (gera .exe Windows)
  - zig                     (gera .elf Linux via 'zig cc -target x86_64-linux-gnu')
"""
import argparse, csv, os, random, re, shutil, string, subprocess, sys
from pathlib import Path

RAIZ      = Path(__file__).resolve().parent
SRC_DIR   = RAIZ / "src"
WIN_DIR   = RAIZ / "dist" / "windows"
LIN_DIR   = RAIZ / "dist" / "linux"
GABARITO  = RAIZ / "gabarito.csv"

MINGW = shutil.which("x86_64-w64-mingw32-gcc")
ZIG   = shutil.which("zig")

TEMPLATE = r"""/* Prova individual — Engenharia Reversa (UNIRIOS)
 * Gerado automaticamente. A senha está ofuscada por XOR: NAO aparece no
 * `strings`. Recupere-a com as tecnicas da aula (Ghidra / GDB / objdump).
 */
#include <stdio.h>
#include <string.h>

static const unsigned char cifrado[] = { %(BYTES)s };
static const int tamanho = %(TAM)d;
static const unsigned char chave = 0x%(CHAVE)02x;

int main(void) {
    char entrada[128];
    printf("=== PROVA DE ENGENHARIA REVERSA — UNIRIOS ===\n");
    printf("Aluno(a): %(NOME)s\n");
    printf("Descubra a senha embutida e informe no relatorio.\n");
    printf("Senha: ");
    if (scanf("%%127s", entrada) != 1) return 1;

    if ((int)strlen(entrada) != tamanho) {
        printf("[-] Acesso negado.\n");
        return 1;
    }
    for (int i = 0; i < tamanho; i++) {
        if (((unsigned char)entrada[i] ^ chave) != cifrado[i]) {
            printf("[-] Acesso negado.\n");
            return 1;
        }
    }
    printf("[+] Acesso concedido! Senha correta.\n");
    return 0;
}
"""


def gerar_senha(idx: int) -> str:
    """Senha única e legível: UNIRIOS{<id>_<6 aleatorios>}"""
    sufixo = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"UNIRIOS{{a{idx:02d}_{sufixo}}}"


def escrever_fonte(nome_aluno: str, senha: str) -> tuple[str, int, int]:
    chave = random.randint(0x11, 0xFE)
    cifrado = [ord(c) ^ chave for c in senha]
    bytes_str = ", ".join(f"0x{b:02x}" for b in cifrado)
    # nome seguro para exibir dentro de string C (sem aspas/quebras)
    nome_c = re.sub(r'[^\w .\-]', '', nome_aluno)[:40]
    return TEMPLATE % {
        "BYTES": bytes_str, "TAM": len(senha),
        "CHAVE": chave, "NOME": nome_c,
    }, chave, len(senha)


def compilar(c_path: Path, exe_out: Path, elf_out: Path) -> list[str]:
    erros = []
    # Windows .exe (estático p/ nao depender de DLLs no PC do aluno)
    r = subprocess.run([MINGW, "-O0", "-s", "-static", "-o", str(exe_out), str(c_path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        erros.append(f"mingw: {r.stderr.strip()[:200]}")
    # Linux .elf via zig (-s remove simbolos p/ dar mais trabalho que o strings)
    r = subprocess.run([ZIG, "cc", "-target", "x86_64-linux-gnu", "-O0", "-s",
                        "-o", str(elf_out), str(c_path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        erros.append(f"zig: {r.stderr.strip()[:200]}")
    return erros


def carregar_roster(args) -> list[str]:
    if args.n:
        return [f"aluno-{i:02d}" for i in range(1, args.n + 1)]
    rp = Path(args.roster)
    if rp.exists():
        nomes = [l.strip() for l in rp.read_text(encoding="utf-8").splitlines() if l.strip()]
        if nomes:
            return nomes
    return [f"aluno-{i:02d}" for i in range(1, 44)]  # default: 43 alunos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, help="gerar N provas genericas (aluno-01..N)")
    ap.add_argument("--roster", default=str(RAIZ / "roster.txt"), help="arquivo com 1 nome por linha")
    ap.add_argument("--seed", type=int, default=None, help="semente p/ reproduzir as mesmas senhas")
    args = ap.parse_args()

    if not MINGW:
        sys.exit("ERRO: x86_64-w64-mingw32-gcc nao encontrado (brew install mingw-w64)")
    if not ZIG:
        sys.exit("ERRO: zig nao encontrado (brew install zig)")
    if args.seed is not None:
        random.seed(args.seed)

    for d in (SRC_DIR, WIN_DIR, LIN_DIR):
        d.mkdir(parents=True, exist_ok=True)

    nomes = carregar_roster(args)
    print(f"Gerando {len(nomes)} provas (Windows + Linux)...\n")

    linhas = []
    for idx, nome in enumerate(nomes, start=1):
        slug = f"a{idx:02d}"
        senha = gerar_senha(idx)
        fonte, chave, tam = escrever_fonte(nome, senha)
        c_path  = SRC_DIR / f"prova_{slug}.c"
        c_path.write_text(fonte, encoding="utf-8")
        exe_out = WIN_DIR / f"prova_{slug}.exe"
        elf_out = LIN_DIR / f"prova_{slug}.elf"
        erros = compilar(c_path, exe_out, elf_out)
        status = "OK" if not erros else "FALHA: " + " | ".join(erros)
        print(f"  [{idx:02d}/{len(nomes)}] {nome:<22} senha={senha:<22} {status}")
        linhas.append({
            "id": slug, "nome": nome, "senha": senha,
            "chave_xor": f"0x{chave:02x}", "tamanho": tam,
            "arquivo_windows": f"dist/windows/prova_{slug}.exe",
            "arquivo_linux":   f"dist/linux/prova_{slug}.elf",
        })

    with GABARITO.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)

    print(f"\nGabarito salvo em: {GABARITO}")
    print(f".exe em: {WIN_DIR}")
    print(f".elf em: {LIN_DIR}")


if __name__ == "__main__":
    main()
