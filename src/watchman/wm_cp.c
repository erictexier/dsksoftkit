#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/stat.h>
#include "wm_publish.h"


#define kCopyCmd            "/bin/cp"

#define kShortTargetChar    't'
#define kLongTargetArg      "--target-directory"


int main(int argc, char *argv[]){
    const char      *ddir;
    int             i;
    
    /* Find the destination argument. cp can have these forms:
       cp [OPTION]... [-T] SOURCE DEST
       cp [OPTION]... SOURCE... DIRECTORY
       cp [OPTION]... -t DIRECTORY SOURCE..
    */
    ddir = argc >= 3 ? argv[argc - 1] : NULL;
    for(i=1; i < argc - 1; i++)
        if( argv[i][0] == '-' && strchr(argv[i], kShortTargetChar) ){
            ddir = argv[i+1];
            break;
        }else if( strncmp(argv[i], kLongTargetArg, strlen(kLongTargetArg)) == 0 ){
            ddir = strchr(argv[i], '=');
            assert(ddir);
            ddir++;
            break;
        }
    
    // Pass all arguments as is, on to cp
    // argv will be null terminated according to the standard: 5.1.2.2.1 Program startup
    umask(0);
    execvp(kCopyCmd, argv);
    return EXIT_FAILURE;                        // should never get here
}
