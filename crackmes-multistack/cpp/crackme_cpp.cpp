// crackme_cpp - Stack C++
//
// Objetivo didático: mostrar o "name mangling" do C++ e como a senha,
// montada em runtime, não aparece em texto puro no `strings`. O aluno
// precisa demanglar os símbolos (c++filt) e/ou decompilar no Ghidra.
//
// Senha correta: Cpp_M4ngl3d!
//
// Compilar (Linux/ELF):   g++ -O0 -g -no-pie -o crackme_cpp crackme_cpp.cpp
// Compilar (Windows/exe): x86_64-w64-mingw32-g++ -O0 -g -static -o crackme_cpp.exe crackme_cpp.cpp
#include <iostream>
#include <string>

// Nome de função propositalmente "feio": no binário vira algo como
// _Z14montarSegredov -> c++filt revela "montarSegredo()".
static std::string montarSegredo() {
    // Senha cifrada com XOR 0x37: NÃO aparece em `strings` (nem como array).
    // O aluno precisa demanglar os símbolos e/ou decompilar no Ghidra para
    // entender que esta função reconstrói a senha em runtime.
    const unsigned char cif[] = {
        0x74, 0x47, 0x47, 0x68, 0x7a, 0x03, 0x59, 0x50, 0x5b, 0x04, 0x53, 0x16
    };
    const unsigned char chave = 0x37;
    std::string s;
    for (unsigned char b : cif) s.push_back((char)(b ^ chave));
    return s;
}

int main() {
    std::string entrada;
    std::cout << "=== CRACKME C++ ===\n";
    std::cout << "Digite a senha: ";
    std::getline(std::cin, entrada);

    if (entrada == montarSegredo()) {
        std::cout << "[+] Acesso concedido!\n";
    } else {
        std::cout << "[-] Acesso negado.\n";
    }
    return 0;
}
