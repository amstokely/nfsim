CMAKE_MINIMUM_REQUIRED(VERSION 3.15)

PROJECT(NFsim LANGUAGES CXX C)

SET(CMAKE_CXX_STANDARD 14)

SET(BUILD_PYTHON ON CACHE BOOL "Build SWIG generated Python bindings")

SET(BUILD_DEV ON CACHE BOOL "Build copy of NFsim exe in dev dir for prototyping and testing purposes.")

SET(CMAKE_BUILD_TYPE Release)

# Temporary removed option to build for windows platform because I don't have a Windows PC to test this on.

SET(SUB_DIRS
    ${CMAKE_SOURCE_DIR}/src/nauty24
    ${CMAKE_SOURCE_DIR}/src/NFutil
    ${CMAKE_SOURCE_DIR}/src/NFutil/MTrand
    ${CMAKE_SOURCE_DIR}/src/NFtest/transcription
    ${CMAKE_SOURCE_DIR}/src/NFtest/tlbr
    ${CMAKE_SOURCE_DIR}/src/NFtest/simple_system
    ${CMAKE_SOURCE_DIR}/src/NFtest/agentcell/cell
    ${CMAKE_SOURCE_DIR}/src/NFtest/agentcell
    ${CMAKE_SOURCE_DIR}/src/NFscheduler
    ${CMAKE_SOURCE_DIR}/src/NFreactions/transformations
    ${CMAKE_SOURCE_DIR}/src/NFreactions/reactions
    ${CMAKE_SOURCE_DIR}/src/NFreactions/reactantLists
    ${CMAKE_SOURCE_DIR}/src/NFreactions/mappings
    ${CMAKE_SOURCE_DIR}/src/NFreactions
    ${CMAKE_SOURCE_DIR}/src/NFoutput
    ${CMAKE_SOURCE_DIR}/src/NFinput
    ${CMAKE_SOURCE_DIR}/src/NFinput/TinyXML
    ${CMAKE_SOURCE_DIR}/src/NFinput/json
    ${CMAKE_SOURCE_DIR}/src/NFfunction/muParser
    ${CMAKE_SOURCE_DIR}/src/NFfunction
    ${CMAKE_SOURCE_DIR}/src/NFcore
    ${CMAKE_SOURCE_DIR}/src/NFcore/reactionSelector
    ${CMAKE_SOURCE_DIR}/src/NFcore/moleculeLists
    )
ADD_DEFINITIONS("-Wno-deprecated-declarations")


IF (CMAKE_SYSTEM_NAME MATCHES "Windows")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
ELSE (CMAKE_SYSTEM_NAME MATCHES "Windows")
    SET_SOURCE_FILES_PROPERTIES(src/NFreactions/reactions/DORreaction.cpp PROPERTIES COMPILE_FLAGS -std=c++11)
    SET_SOURCE_FILES_PROPERTIES(src/NFcore/molecule.cpp PROPERTIES COMPILE_FLAGS -std=c++11)
    SET_SOURCE_FILES_PROPERTIES(src/NFcore/templateMolecule.cpp PROPERTIES COMPILE_FLAGS -std=c++11)
    SET_SOURCE_FILES_PROPERTIES(src/NFinput/NFinput.cpp PROPERTIES COMPILE_FLAGS -std=c++11)
ENDIF (CMAKE_SYSTEM_NAME MATCHES "Windows")


INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR} include ${SUB_DIRS})


FILE(GLOB_RECURSE src_files "${CMAKE_CURRENT_SOURCE_DIR}/src/*cpp")
FILE(GLOB_RECURSE c_src_files "${CMAKE_CURRENT_SOURCE_DIR}/src/*c")


SET(SRC_FILES
    ${src_files}
    ${c_src_files}
    )

ADD_LIBRARY(
    NFsimLib SHARED
    ${SRC_FILES}
)

ADD_EXECUTABLE(
    NFsim
    ${SRC_FILES}
)
IF (${BUILD_DEV})
    ADD_EXECUTABLE(
        NFsimDeV
        ${SRC_FILES}
    )
    SET_TARGET_PROPERTIES(
        NFsimDeV
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/dev
    )
ENDIF (${BUILD_DEV})

IF (${BUILD_PYTHON})
    FIND_PACKAGE(SWIG REQUIRED)
    INCLUDE(${SWIG_USE_FILE})

    FIND_PACKAGE(Python3 REQUIRED COMPONENTS Interpreter Development)

    SET(PYNFSIM_LINK_LIBRARIES ${Python3_LIBRARIES} NFsimLib)

    SET(PYNFSIM_INCLUDE_DIRS ${SUB_DIRS} ${CMAKE_SOURCE_DIR}/src ${Python3_INCLUDE_DIRS})

    SET_SOURCE_FILES_PROPERTIES(
        ${CMAKE_SOURCE_DIR}/swig/pynfsim.i
        PROPERTIES
        CPLUSPLUS ON
        SWIG_MODULE_NAME pynfsim
        INCLUDE_DIRECTORIES "${PYNFSIM_INCLUDE_DIRS}"
    )
    LINK_LIBRARIES("${PYNFSIM_LINK_LIBRARIES}")
    SWIG_ADD_LIBRARY(
        pynfsim
        LANGUAGE python
        SOURCES ${CMAKE_SOURCE_DIR}/swig/pynfsim.i
    )
    ADD_DEPENDENCIES(pynfsim NFsimLib)
    SET_TARGET_PROPERTIES(
        pynfsim
        PROPERTIES
        LINK_FLAGS "-flat_namespace -undefined suppress"
        LINK_LIBRARIES "${PYNFSIM_LINK_LIBRARIES}"
        INCLUDE_DIRECTORIES "${PYNFSIM_INCLUDE_DIRS}"
    )
ENDIF (${BUILD_PYTHON})




