// CrackMe.java - Stack Java (bytecode / .jar)
//
// Objetivo didático: mostrar que bytecode Java decompila de forma quase
// perfeita. O aluno recebe apenas o CrackMe.jar e deve decompilar com
// jadx (GUI) / CFR / procyon, ou inspecionar com `javap -c -p CrackMe`.
// Mesmo ofuscada (XOR), a lógica fica legível no decompilado.
//
// Senha correta: J4v4_D3c0mp1l3d
//
// Compilar e empacotar:
//   javac CrackMe.java
//   jar cfe CrackMe.jar CrackMe CrackMe.class
// Executar:
//   java -jar CrackMe.jar
import java.util.Scanner;

public class CrackMe {

    // Bytes cifrados (senha XOR 0x55). Em `strings` saem só os bytes,
    // não a senha; o decompilador revela o algoritmo.
    private static final int[] CIFRADO = {
        0x1f, 0x61, 0x23, 0x61, 0x0a, 0x11, 0x66, 0x36,
        0x65, 0x38, 0x25, 0x64, 0x39, 0x66, 0x31
    };
    private static final int CHAVE = 0x55;

    private static boolean verifica(String entrada) {
        if (entrada.length() != CIFRADO.length) return false;
        for (int i = 0; i < CIFRADO.length; i++) {
            if ((entrada.charAt(i) ^ CHAVE) != CIFRADO[i]) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println("=== CRACKME JAVA ===");
        System.out.print("Digite a senha: ");
        Scanner sc = new Scanner(System.in);
        String entrada = sc.hasNextLine() ? sc.nextLine().trim() : "";
        if (verifica(entrada)) {
            System.out.println("[+] Acesso concedido!");
        } else {
            System.out.println("[-] Acesso negado.");
        }
    }
}
