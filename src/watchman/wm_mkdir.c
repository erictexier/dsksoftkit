#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define kDirCmd "/bin/mkdir"

int main(int argc, char *argv[]){
    // Pass all arguments as is, on to mkdir
    // argv will be null terminated according to the standard: 5.1.2.2.1 Program startup
    execvp(kDirCmd, argv);
    return EXIT_FAILURE;                        // should never get here
}
