cmake_minimum_required(VERSION 3.20)
project(jarvis-audio-engine VERSION 1.9.0 LANGUAGES CXX)

# C++20 standard for modern features
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ============================================================================
# Compilation Flags
# ============================================================================

# Optimization for sub-millisecond latency
if (MSVC)
    add_compile_options(/O2 /arch:AVX2 /fp:fast)
else()
    add_compile_options(-O3 -march=native -ffast-math)
endif()

# ============================================================================
# Source Files
# ============================================================================

set(SOURCES
    src/audio_engine.cpp
)

set(HEADERS
    include/audio_engine.h
)

# ============================================================================
# Library Targets
# ============================================================================

# Shared library for Rust FFI binding
add_library(audio_engine_shared SHARED ${SOURCES} ${HEADERS})

target_include_directories(audio_engine_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Set output directory
set_target_properties(audio_engine_shared PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# ============================================================================
# External Dependencies
# ============================================================================

# Find FFmpeg libraries
find_package(PkgConfig REQUIRED)
pkg_check_modules(FFMPEG REQUIRED
    libavformat
    libavcodec
    libavutil
    libswresample
)

# Find PortAudio
pkg_check_modules(PORTAUDIO REQUIRED portaudio-2.0)

# Find libsamplerate (optional but recommended)
pkg_check_modules(SAMPLERATE libsamplerate)

# Include directories
target_include_directories(audio_engine_shared PRIVATE
    ${FFMPEG_INCLUDE_DIRS}
    ${PORTAUDIO_INCLUDE_DIRS}
    $<$<BOOL:${SAMPLERATE_FOUND}>:${SAMPLERATE_INCLUDE_DIRS}>
)

# Link libraries
target_link_libraries(audio_engine_shared PRIVATE
    ${FFMPEG_LIBRARIES}
    ${PORTAUDIO_LIBRARIES}
    $<$<BOOL:${SAMPLERATE_FOUND}>:${SAMPLERATE_LIBRARIES}>
)

# Compiler definitions
if(SAMPLERATE_FOUND)
    target_compile_definitions(audio_engine_shared PRIVATE HAVE_SAMPLERATE)
endif()

# ============================================================================
# Testing
# ============================================================================

enable_testing()

# Add test executable
add_executable(audio_test
    tests/test_audio_engine.cpp
)

target_link_libraries(audio_test PRIVATE
    audio_engine_shared
)

add_test(NAME AudioEngineTest COMMAND audio_test)

# ============================================================================
# Installation
# ============================================================================

install(TARGETS audio_engine_shared
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES include/audio_engine.h
    DESTINATION include
)

# ============================================================================
# Docker Build Support
# ============================================================================

# Build command:
# cmake -B build && cmake --build build --config Release
#
# Docker:
# docker build -t jarvis-audio-engine:1.9.0 .
