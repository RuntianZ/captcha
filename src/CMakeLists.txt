cmake_minimum_required(VERSION 3.8)
project(src)

set(CMAKE_C_STANDARD 99)

set(SOURCE_FILES captcha.h main.c captcha.c)
add_executable(src ${SOURCE_FILES})