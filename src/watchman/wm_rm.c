#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include "wm_publish.h"


#define kRmCmd        "/bin/rm"

int main(int argc, char *argv[]){
    const char      *ddir;
    int             i;
    
    // For security reasons, this program will only rm from the publish tree
    for(i=1; i < argc; i++)
        if( argv[i][0] == '-' && argv[i][1] != '-'){
            // If it's not a long option, then don't check next argument
            i++;
        }else if( argv[i][0] != '-' && argv[i][0] != 0 && !path_in_publish(argv[i])){
            fprintf(stderr, "%s: path is not under publish: %s\n", argv[0], argv[i]);
            return ENOTSUP;
        }
    
    // Pass all arguments as is, on to rm
    // argv will be null terminated according to the standard: 5.1.2.2.1 Program startup
    execvp(kRmCmd, argv);
    return EXIT_FAILURE;                        // should never get here
}
