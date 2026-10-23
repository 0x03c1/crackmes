#include <stdio.h>
#include <string.h>

/*
 * crackme1 - Nível 1
 * A senha está hardcoded como string literal.
 * Objetivo didático: análise estática básica (file, strings).
 */

int main(void) {
    char senha[64];

    printf("=== CRACKME 1 ===\n");
    printf("Digite a senha: ");
    scanf("%63s", senha);

    if (strcmp(senha, "Un1r10s_R3v_2026") == 0) {
        puts("[+] Acesso concedido!");
    } else {
        puts("[-] Acesso negado.");
    }

    return 0;
}
