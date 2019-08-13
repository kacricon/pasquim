#include <stdio.h>
#include <stdlib.h>

__attribute__((__cdecl__))
extern int scheme_entry() asm ("scheme_entry");

int main(int argc, const char **argv) {
    int val = scheme_entry();
    printf("%d\n", val);
    return 0;
}
