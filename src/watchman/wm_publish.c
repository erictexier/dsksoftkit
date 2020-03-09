#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <limits.h>
#include <unistd.h>
#include "wm_publish.h"


static const char *get_publish_path(){
    static char     *sPubPath = NULL;
    
    
    if( !sPubPath ){
        size_t          sz;
        const char      *show_path = getenv("NCO_PROJECT_PATH");
        struct stat     info = {};

        if( !show_path ){
            fprintf(stderr, "project path is not set\n");
            return "";
        }
        sz = strlen(show_path) + strlen(kPublishSubdir) + 1;
        sPubPath = malloc(sz);
        assert(sPubPath);
        strncpy(sPubPath, show_path, sz);
        sPubPath[sz-1] = 0;
        strcat(sPubPath, kPublishSubdir);
        
        stat(sPubPath, &info);
        if( !S_ISDIR(info.st_mode)){
            fprintf(stderr, "publish path does not exist: %s%s\n", show_path, kPublishSubdir);
            free(sPubPath);
            sPubPath = "";
        }
    }
    return sPubPath;
}

static char *get_absolute_path(const char *path){
    size_t          sz;
    char            *abspath;
    static char     sCwdPath[PATH_MAX] = {0};
    
    
    if( sCwdPath[0] == 0 ){
        if( !getcwd(sCwdPath, PATH_MAX)) return NULL;
    }
    sz = strlen(sCwdPath) + 1 + strlen(path) + 1;
    abspath = malloc(sz);
    assert(abspath);
    strncpy(abspath, sCwdPath, sz);
    abspath[sz-1] = 0;
    strcat(abspath, "/");
    strcat(abspath, path);
    return abspath;
}

int path_in_publish(const char *origpath){
    char    *path, *abspath, *pub_prefix, *pos;
    int     x;


    pub_prefix = realpath(get_publish_path(), NULL);
    if( !pub_prefix ) return 0;

    // Make origpath absolute
    assert(origpath);
    if( origpath[0] != '/' )
        path = get_absolute_path(origpath);
    else
        path = strdup(origpath);
    assert(path);

    // Find parent directory of path, so that realpath will resolve correctly if it exists
    // path should be absolute at this point.
    // Strip trailing slashes
    do{
        pos = strrchr(path, '/');
        if( pos && pos > path ) *pos = 0;
    }while( pos && pos > path && *(pos+1) == 0 );

    abspath = realpath(path, NULL);         // malloc's
    //printf("prefix: %s\n", pub_prefix);
    //printf("check : %s\n", abspath ? abspath : path);
    pos = strstr(abspath ? abspath : path, pub_prefix);
    x = pos ? 1 : 0;

    if( abspath ) free(abspath);
    free(path);
    free(pub_prefix);
    return x;
}
