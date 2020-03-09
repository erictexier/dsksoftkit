#*****************************************************************************
# 
# watchman command line utilities CMakeLists.txt build script.
#
# Copyright (c) 2019
# Eclectic Studio Net
# 
# Usage: Run this in a shell:
#
# cmake28 -g "Unix Makefiles" .
# make
#
#*****************************************************************************


# Set minimum cmake version that can process this file.
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

PROJECT(watchman)

# Define build version here.
SET(WATCHMAN_VERSION_MAJOR 1)
SET(WATCHMAN_VERSION_MINOR 0)
SET(WATCHMAN_VERSION_PATCH 0)

INCLUDE_DIRECTORIES("${PROJECT_BINARY_DIR}")

ADD_EXECUTABLE(wm_cp wm_publish.c wm_cp.c)
ADD_EXECUTABLE(wm_ln wm_publish.c wm_ln.c)
ADD_EXECUTABLE(wm_mkdir wm_publish.c wm_mkdir.c) 
ADD_EXECUTABLE(wm_rm wm_publish.c wm_rm.c)
ADD_EXECUTABLE(wm_rmdir wm_publish.c wm_rmdir.c) 
ADD_EXECUTABLE(wm_mv wm_mv.c) 
ADD_EXECUTABLE(wm_chmod wm_chmod.c) 

INSTALL(TARGETS wm_cp wm_ln wm_mkdir wm_rm wm_rmdir wm_mv wm_chmod DESTINATION bin) 
