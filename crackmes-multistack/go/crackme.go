// crackme.go - Stack Go
//
// Objetivo didático: binários Go são grandes e estáticos. Mesmo com os
// símbolos removidos (-s -w), muita coisa "vaza" em `strings`, e a
// estrutura exige ferramentas específicas (GoReSym, Ghidra com plugin Go).
// Aqui a senha é verificada por XOR, então não aparece inteira no strings;
// o aluno precisa achar os bytes cifrados e a chave no decompilado.
//
// Senha correta: G0_r3v3rs1ng!!
//
// Compilar (Linux/ELF):   GOOS=linux   GOARCH=amd64 go build -ldflags "-s -w" -o crackme     crackme.go
// Compilar (Windows/exe): GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o crackme.exe crackme.go
package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// Senha cifrada com XOR 0x33.
var cifrado = []byte{
	0x74, 0x03, 0x6c, 0x41, 0x00, 0x45, 0x00, 0x41, 0x40, 0x02, 0x5d, 0x54, 0x12, 0x12,
}

const chave = 0x33

func verifica(entrada string) bool {
	if len(entrada) != len(cifrado) {
		return false
	}
	for i := 0; i < len(cifrado); i++ {
		if entrada[i]^chave != cifrado[i] {
			return false
		}
	}
	return true
}

func main() {
	fmt.Println("=== CRACKME GO ===")
	fmt.Print("Digite a senha: ")
	leitor := bufio.NewReader(os.Stdin)
	linha, _ := leitor.ReadString('\n')
	entrada := strings.TrimSpace(linha)
	if verifica(entrada) {
		fmt.Println("[+] Acesso concedido!")
	} else {
		fmt.Println("[-] Acesso negado.")
	}
}
