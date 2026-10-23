#include <stdio.h>

/*
 * crackme3 - Nível 3
 * Comparação feita byte a byte em loop (sem strcmp),
 * então o ltrace não revela nada. O serial correto também
 * é montado em tempo de execução (não aparece em `strings`).
 * Objetivo didático: usar GDB para inspecionar o fluxo do programa
 * e/ou aplicar patch no binário.
 */

int validar(const char *serial) {
    char alvo[9];
    int i;

    alvo[0] = 'R';
    alvo[1] = '3';
    alvo[2] = 'V';
    alvo[3] = '3';
    alvo[4] = 'R';
    alvo[5] = 'S';
    alvo[6] = '0';
    alvo[7] = '!';
    alvo[8] = '\0';

    for (i = 0; i < 8; i++) {
        if (serial[i] != alvo[i])
            return 0;
    }
    return 1;
}

int main(void) {
    char serial[64];

    printf("=== CRACKME 3 ===\n");
    printf("Digite o serial: ");
    scanf("%63s", serial);

    if (validar(serial)) {
        puts("[+] Serial válido! Acesso concedido.");
    } else {
        puts("[-] Serial inválido.");
    }

    return 0;
}
