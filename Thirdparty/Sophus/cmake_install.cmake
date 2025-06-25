# Install script for directory: /home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/sophus/cmake/SophusTargets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/sophus/cmake/SophusTargets.cmake"
         "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/CMakeFiles/Export/4110a4f8b3c48cc11f058d9be1acc9d2/SophusTargets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/sophus/cmake/SophusTargets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/sophus/cmake/SophusTargets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/sophus/cmake" TYPE FILE FILES "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/CMakeFiles/Export/4110a4f8b3c48cc11f058d9be1acc9d2/SophusTargets.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/sophus/cmake" TYPE FILE FILES
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/SophusConfig.cmake"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/SophusConfigVersion.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/sophus" TYPE FILE FILES
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/average.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/common.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/geometry.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/interpolate.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/interpolate_details.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/num_diff.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/rotation_matrix.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/rxso2.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/rxso3.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/se2.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/se3.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/sim2.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/sim3.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/sim_details.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/so2.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/so3.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/types.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/velocities.hpp"
    "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/sophus/formatstring.hpp"
    )
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/test/cmake_install.cmake")
  include("/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/examples/cmake_install.cmake")

endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
if(CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_COMPONENT MATCHES "^[a-zA-Z0-9_.+-]+$")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
  else()
    string(MD5 CMAKE_INST_COMP_HASH "${CMAKE_INSTALL_COMPONENT}")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INST_COMP_HASH}.txt")
    unset(CMAKE_INST_COMP_HASH)
  endif()
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/home/pzt/Documents/Research/SLAM/ORB_SLAM3/Thirdparty/Sophus/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
