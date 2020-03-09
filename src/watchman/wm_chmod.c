#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define kChmodCmd "/bin/chmod"

int main(int argc, char *argv[]){
    // Pass all arguments as is
    execvp(kChmodCmd, argv);
    return EXIT_FAILURE;                        // should never get here
}
