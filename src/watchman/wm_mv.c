#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define kMvCmd "/bin/mv"

int main(int argc, char *argv[]){
    // Pass all arguments as is
    execvp(kMvCmd, argv);
    return EXIT_FAILURE;                        // should never get here
}
