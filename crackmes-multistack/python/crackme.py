#!/usr/bin/env python3
# crackme Python - Stack Python (bytecode)
#
# Objetivo didático: o aluno recebe apenas o .pyc (bytecode compilado),
# NÃO o .py. A senha não aparece em texto puro porque está ofuscada
# (string invertida + deslocamento). Ele precisa:
#   - desmontar o bytecode:  python3 -m dis crackme.pyc   (ou módulo dis)
#   - ou decompilar:         pip install decompyle3 / uncompyle6
#   - e então reverter o algoritmo.
#
# Senha correta: Pyth0n_R3v3rs3
#
# Gerar o .pyc para distribuir (sem entregar o .py):
#   python3 -c "import py_compile; py_compile.compile('crackme.py', cfile='crackme.pyc')"

def _verifica(entrada: str) -> bool:
    # A senha fica guardada INVERTIDA no código; em runtime desfazemos a
    # inversão para comparar. Resultado: a senha nunca aparece "inteira"
    # em texto puro, mas o bytecode (dis) revela a string invertida.
    alvo = "3sr3v3R_n0htyP"[::-1]          # inverte -> Pyth0n_R3v3rs3
    return entrada == alvo


def main() -> None:
    print("=== CRACKME PYTHON ===")
    entrada = input("Digite a senha: ").strip()
    if _verifica(entrada):
        print("[+] Acesso concedido!")
    else:
        print("[-] Acesso negado.")


if __name__ == "__main__":
    main()
