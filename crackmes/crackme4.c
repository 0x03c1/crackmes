#include <stdio.h>
#include <string.h>

/*
 * crackme4 - Nível 4 (bônus)
 * A senha é verificada com XOR: cada caractere da entrada é
 * transformado (XOR 0x42) e comparado com um byte cifrado.
 * Objetivo didático: decompilar no Ghidra, entender o algoritmo
 * e recuperar a senha original.
 */

int main(void) {
    char senha[64];
    int i;
    int tamanho = 16;

    unsigned char cifrado[] = {
        0x24, 0x2e, 0x23, 0x25, 0x39, 0x25, 0x2a, 0x73,
        0x26, 0x30, 0x76, 0x1d, 0x24, 0x36, 0x35, 0x3f
    };

    printf("=== CRACKME 4 ===\n");
    printf("Digite a senha: ");
    scanf("%63s", senha);

    if (strlen(senha) != (size_t)tamanho) {
        puts("[-] Acesso negado.");
        return 1;
    }

    for (i = 0; i < tamanho; i++) {
        if ((senha[i] ^ 0x42) != cifrado[i]) {
            puts("[-] Acesso negado.");
            return 1;
        }
    }

    puts("[+] Acesso concedido!");
    return 0;
}
