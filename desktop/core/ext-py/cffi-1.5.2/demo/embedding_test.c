/* Link this program with libembedding_test.so.
   E.g. with gcc:

      gcc -o embedding_test embedding_test.c _embedding_cffi*.so
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
