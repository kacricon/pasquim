#include <stdio.h>
#include <stdlib.h>

#define FIXNUM_MASK     3
#define FIXNUM_TAG      0
#define FIXNUM_SHIFT    2

#define CHAR_MASK       0xff
#define CHAR_SHIFT      8
#define CHAR_TAG        7

#define BOOL_MASK       0xff
#define BOOL_SHIFT      8
#define BOOL_TAG        15

void show(int x) {
    if((x & FIXNUM_MASK) == FIXNUM_TAG) {
        // integer
        printf("%d", x >> FIXNUM_SHIFT);
    } else if((x & CHAR_MASK) == CHAR_TAG) {
        // character
        printf("#\\%c", (char)(x >> CHAR_SHIFT));
    } else if((x & BOOL_MASK) == BOOL_TAG) {
        // boolean
        if((x >> BOOL_SHIFT) != 0) {
            printf("#t");
        } else {
            printf("#f");
        }
    }
}

__attribute__((__cdecl__))
extern int scheme_entry() asm ("scheme_entry");

int main(int argc, const char **argv) {
    int val = scheme_entry();
    show(val);
    printf("\n");
    return 0;
}
