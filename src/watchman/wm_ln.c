#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#include "wm_publish.h"


#define kLinkCmd                "/bin/ln"

#define kShortTargetChar        't'
#define kLongTargetArg          "--target-directory"

#define kNoShortHardLinkChars   "dFPL"
#define kNoLongHardLinkArgs     {"--directory", "--logical", "--physical"}


int main(int argc, char *argv[]){
    const char      *ddir;
    char            **lnargs;
    int             i;

    /* Find the destination argument. ln can have these forms:
       ln [OPTION]... [-T] TARGET LINK_NAME   (1st form)
       ln [OPTION]... TARGET                  (2nd form)
       ln [OPTION]... TARGET... DIRECTORY     (3rd form)
       ln [OPTION]... -t DIRECTORY TARGET...  (4th form)
    */
    ddir = argc >= 2 ? argv[1] : NULL;
    for(i=1; i < argc; i++)
        if( i < argc - 1 && argv[i][0] == '-' && strchr(argv[i], kShortTargetChar) ){
            ddir = argv[i+1];
            break;
        }else if( i < argc - 1 && strncmp(argv[i], kLongTargetArg, strlen(kLongTargetArg)) == 0 ){
            ddir = strchr(argv[i], '=');
            assert(ddir);
            ddir++;
            break;
        }else if( argv[i][0] == '-' && strpbrk(argv[i], kNoShortHardLinkChars )){
            // Do not allow any short hard link options
            fprintf(stderr, "%s: cannot use any hard link options: %s\n", argv[0], argv[i]);
            return ENOTSUP;
        }else if( argv[i][0] == '-' ){
            // Do not allow any long hard link options
            const char      *restricted[] = kNoLongHardLinkArgs;
            int             r = 0;

            for( ; r < sizeof(restricted)/sizeof(char *); r++)
                if( strncmp(argv[i], restricted[r], strlen(restricted[r])) == 0 ){
                    fprintf(stderr, "%s: cannot use any hard link options: %s\n", argv[0], argv[i]);
                    return ENOTSUP;
                }
        }else if( argv[i][0] != '-' ){
            ddir = argv[i];
        }

    // Pass arguments to ln, always with -s, and without any hard link options
    lnargs = calloc(sizeof(char *), argc+2);
    assert(lnargs);
    lnargs[0] = argv[0];
    lnargs[1] = "-s";
    for(i=1; i <= argc; i++)    // argv[argc] always == NULL
        lnargs[i+1] = argv[i];

    execvp(kLinkCmd, lnargs);
    free(lnargs);                       // should never get here
    return EXIT_FAILURE;
}
