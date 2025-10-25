cmake_minimum_required(VERSION 3.20)
project(jarvis-audio-engine VERSION 1.9.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimisations pour mode release
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffast-math")
endif()

# Dependencies optionnelles (pour développement futur)
# find_package(ALSA QUIET)
# find_package(PkgConfig QUIET)

# Jarvis Audio Engine Library (placeholder)
add_library(jarvis_audio_engine
    src/audio_engine.cpp
)

target_include_directories(jarvis_audio_engine PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# HTTP API Server
find_package(nlohmann_json 3.2.0 QUIET)
find_package(httplib QUIET)

add_executable(jarvis-audio-api
    src/http_server.cpp
)

target_include_directories(jarvis-audio-api PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(jarvis-audio-api PUBLIC
    jarvis_audio_engine
)

if(nlohmann_json_FOUND)
    target_link_libraries(jarvis-audio-api PUBLIC nlohmann_json::nlohmann_json)
endif()

if(httplib_FOUND)
    target_link_libraries(jarvis-audio-api PUBLIC httplib::httplib)
endif()

# Installation
install(TARGETS jarvis_audio_engine jarvis-audio-api
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
)
install(DIRECTORY include/ DESTINATION include)

# Notes de développement pour futures phases
# - Intégrer Whisper.cpp pour STT
# - Intégrer Piper pour TTS
# - Ajouter support ALSA/PipeWire pour audio I/O
# - Implémenter DSP pipeline (HPF, AGC, normalisation)
# - Ajouter tests unitaires