cmake_minimum_required(VERSION 3.20)
project(jarvis-audio-engine VERSION 1.3.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffast-math")

# Dependencies
find_package(ALSA REQUIRED)
find_package(PkgConfig REQUIRED)

pkg_check_modules(PIPEWIRE libpipewire-0.3)
pkg_check_modules(SPA libspa-0.2)

# Whisper.cpp (STT)
add_subdirectory(third_party/whisper.cpp)

# Piper TTS
add_subdirectory(third_party/piper)

# Jarvis Audio Engine Library
add_library(jarvis_audio_engine
    src/audio_engine.cpp
    src/dsp_pipeline.cpp
    src/stт_processor.cpp
    src/tts_processor.cpp
    src/audio_io.cpp
    src/audio_buffer.cpp
)

target_include_directories(jarvis_audio_engine PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${ALSA_INCLUDE_DIRS}
    ${PIPEWIRE_INCLUDE_DIRS}
    ${SPA_INCLUDE_DIRS}
)

target_link_libraries(jarvis_audio_engine PUBLIC
    ${ALSA_LIBRARIES}
    ${PIPEWIRE_LIBRARIES}
    ${SPA_LIBRARIES}
    whisper
    piper
)

# HTTP API Server (CPR + nlohmann/json)
find_package(nlohmann_json REQUIRED)
find_package(httplib REQUIRED)

add_executable(jarvis-audio-api
    src/http_server.cpp
    src/api_handlers.cpp
)

target_link_libraries(jarvis-audio-api PUBLIC
    jarvis_audio_engine
    nlohmann_json::nlohmann_json
    httplib::httplib
)

# Tests
enable_testing()
add_executable(audio_tests
    tests/test_dsp.cpp
    tests/test_stт.cpp
    tests/test_tts.cpp
)
target_link_libraries(audio_tests PUBLIC jarvis_audio_engine)
add_test(NAME AudioTests COMMAND audio_tests)

# Installation
install(TARGETS jarvis_audio_engine jarvis-audio-api
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
)
install(DIRECTORY include/ DESTINATION include)