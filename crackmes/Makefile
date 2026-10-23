# Makefile dos crackmes - Aula de Engenharia Reversa (Kali Linux)
# Flags: -O0 (sem otimização), -g (símbolos p/ GDB), -no-pie (endereços fixos)

CC      = gcc
CFLAGS  = -O0 -g -no-pie -fno-stack-protector

all: crackme1 crackme2 crackme3 crackme4

crackme1: crackme1.c
	$(CC) $(CFLAGS) -o $@ $<

crackme2: crackme2.c
	$(CC) $(CFLAGS) -o $@ $<

crackme3: crackme3.c
	$(CC) $(CFLAGS) -o $@ $<

crackme4: crackme4.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f crackme1 crackme2 crackme3 crackme4
