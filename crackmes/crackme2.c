#include <stdio.h>
#include <string.h>

/*
 * crackme2 - Nível 2
 * A senha é montada caractere a caractere em tempo de execução,
 * portanto NÃO aparece na saída do `strings`.
 * Objetivo didático: análise dinâmica com ltrace (intercepta o strcmp).
 */

int main(void) {
    char senha[64];
    char correta[9];

    correta[0] = 'k';
    correta[1] = '4';
    correta[2] = 'l';
    correta[3] = '1';
    correta[4] = '_';
    correta[5] = 'r';
    correta[6] = '3';
    correta[7] = 'v';
    correta[8] = '\0';

    printf("=== CRACKME 2 ===\n");
    printf("Digite a senha: ");
    scanf("%63s", senha);

    if (strcmp(senha, correta) == 0) {
        puts("[+] Acesso concedido!");
    } else {
        puts("[-] Acesso negado.");
    }

    return 0;
}
