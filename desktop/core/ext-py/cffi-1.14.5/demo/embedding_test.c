/* There are two options:

   =====1=====

   Link this program with _embedding_test.so.
   E.g. with gcc:

      gcc -o embedding_test embedding_test.c _embedding_cffi*.so

   You must then run the executable with the right command
   (LD_LIBRARY_PATH on Linux), otherwise it won't find the
   _embedding_cffi*.so:

      LD_LIBRARY_PATH=. ./embedding_test

   There are platform-specific options to gcc to avoid needing
   that, too.  Linux:

      gcc -o embedding_test embedding_test.c _embedding_cffi*.so  \
          -Wl,-rpath=\$ORIGIN/

   =====2=====

   Compile and link the _embedding_test.c source code together with
   this example (e.g. with PyPy):

      gcc -o embedding_test embedding_test.c _embedding_cffi.c  \
          -I/opt/pypy/include -pthread -lpypy-c
*/

#include <stdio.h>

extern int add(int x, int y);


int main(void)
{
    int res = add(40, 2);
    printf("result: %d\n", res);
    res = add(100, -5);
    printf("result: %d\n", res);
    return 0;
}
