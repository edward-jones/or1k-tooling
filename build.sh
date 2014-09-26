#!/bin/bash

# Current shortcoming is that this can only set up the environment correctly
# when one of the commands is run. So things run outside the environment wont be
# set up right at all. Will be a major issue if doing incremental builds
#
# Hopefully will always run tests using this script, but at the very least
# PATH will need install/bin and or1ksim-install/bin in

BASEDIR=`pwd`

BINUTILS_BUILD=${BASEDIR}/build/binutils
BINUTILS_SRC=${BASEDIR}/or1k-src

LLVM_BUILD=${BASEDIR}/build/llvm
LLVM_SRC=${BASEDIR}/llvm-or1k
CLANG_SRC=${BASEDIR}/clang-or1k

COMPILER_RT_BUILD=${BASEDIR}/build/compiler-rt
COMPILER_RT_SRC=${BASEDIR}/compiler-rt-or1k

NEWLIB_BUILD=${BASEDIR}/build/newlib
NEWLIB_SRC=${BASEDIR}/or1k-src

GCC_BUILD=${BASEDIR}/build/gcc
GCC_SRC=${BASEDIR}/or1k-gcc

OR1KSIM_BUILD=${BASEDIR}/build/or1ksim
OR1KSIM_SRC=${BASEDIR}/or1ksim
OR1KSIM_INSTALL=${BASEDIR}/or1ksim-install

CRUNTIME_BUILD=${BASEDIR}/build/cruntime
CRUNTIME_SRC=${BASEDIR}/cruntime-or1k

DEJAGNU_BUILD=${BASEDIR}/build/dejagnu
DEJAGNU_SRC=${BASEDIR}/or1k-dejagnu

OR1K_TOOLING=${BASEDIR}/or1k-tooling

INSTALL=${BASEDIR}/install
PARALLEL="-j12"


# Set terminal title                                                            
# @param string $1  Tab/window title                                            
# @param string $2  (optional) Separate window title                            
# The latest version of this software can be obtained here:                     
# http://fvue.nl/wiki/NameTerminal                                              
# (Modified to avoid breakage with -e in this script by Simon Cook)             
nameTerminal() {                                                                
    echo " * $1"                                                                
    [ "${TERM:0:5}" = "xterm" ]   && local ansiNrTab=0                          
    [ "$TERM"       = "rxvt" ]    && local ansiNrTab=61                         
    [ "$TERM"       = "konsole" ] && local ansiNrTab=30 ansiNrWindow=0          
        # Change tab title                                                      
    [ $ansiNrTab ] && echo -n $'\e'"]$ansiNrTab;$0 - $1"$'\a'                   
} # nameTerminal()                                                              
                                                                                
mkcd() {                                                                        
  mkdir -p "${1}" && cd "${1}"                                                  
} 


binutilsConfig() {
    rm -rf ${BINUTILS_BUILD}
    mkcd ${BINUTILS_BUILD}
    ${BINUTILS_SRC}/configure --prefix=${INSTALL} --target=or1k-elf \
      --enable-shared --disable-itcl --disable-tk --disable-tcl \
      --disable-winsup --disable-libgui --disable-rda --disable-sid \
      --disable-sim --disable-gdb --with-sysroot --disable-newlib \
      --disable-libgloss --disable-werror > config.log 2>&1
}

llvmConfig() {
    rm -rf ${LLVM_BUILD}

    # ensure theres a symlink to clang in the tools directory
    ln -sf ${CLANG_SRC} ${LLVM_SRC}/tools/clang

    mkcd ${LLVM_BUILD}
    cmake ${LLVM_SRC} -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_INSTALL_PREFIX=${INSTALL} > config.log 2>&1
}

or1ksimConfig() {
    rm -rf ${OR1KSIM_BUILD}
    mkcd ${OR1KSIM_BUILD}
    ${OR1KSIM_SRC}/configure --prefix=${OR1KSIM_INSTALL} > config.log 2>&1
}

# should be built after binutils and llvm/clang
compilerrtConfig() {
    # ensure clang/binutils in the PATH
    export PATH=${INSTALL}/bin:$PATH

    rm -rf ${COMPILER_RT_BUILD}

    # hardcoded LLVM_CONFIG_PATH but it should be in path anyway
    mkcd ${COMPILER_RT_BUILD}
    cmake ${COMPILER_RT_SRC} \
      -DCMAKE_INSTALL_PREFIX=${INSTALL} \
      -DLLVM_CONFIG_PATH=${INSTALL}/bin/llvm-config \
      -DCMAKE_C_COMPILER=${INSTALL}/bin/clang \
      -DCMAKE_CXX_COMPILER=${INSTALL}/bin/clang++ \
      -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug > config.log 2>&1
}

# should be built after clang, binutils and or1ksim
newlibConfig() {
    rm -rf ${NEWLIB_BUILD}

    # ensure clang/binutils in the path
    export PATH=${INSTALL}/bin:${PATH}

    # add symlink to find clang when looking for or1k-elf cross compiler
    ln -sf ${INSTALL}/bin/clang ${INSTALL}/bin/or1k-elf-cc

    mkcd ${NEWLIB_BUILD}
    ${NEWLIB_SRC}/configure CC=${INSTALL}/bin/clang --prefix=${INSTALL} \
      --target=or1k-elf --enable-shared --disable-itcl --disable-tk \
      --disable-tcl --disable-winsup --disable-libgui --disable-rda \
      --disable-sid --enable-sim --enable-gdb --with-sysroot --enable-newlib \
      --enable-libgloss --disable-werror --with-or1ksim=${OR1KSIM_INSTALL} \
      > config.log 2>&1
}

# should be built after clang and binutils
cruntimeConfig() {
    rm -rf ${CRUNTIME_BUILD}

    # ensure clang/binutils in the path
    export PATH=${INSTALL}/bin:${PATH}

    # no gcc cross compiler atm, use clang
    mkcd ${CRUNTIME_BUILD}
    cmake ${CRUNTIME_SRC} -DCMAKE_INSTALL_PREFIX=${INSTALL} \
      -DCMAKE_C_COMPILER=${INSTALL}/bin/clang \
      -DCMAKE_CXX_COMPILER=${INSTALL}/bin/clang++ > config.log 2>&1
}

# build gcc cross-compiler for or1k tests, may need to be done after newlib
# built.
gccConfig() {
    rm -rf ${GCC_BUILD}
    mkcd ${GCC_BUILD}
    ${GCC_SRC}/configure --prefix=${INSTALL} --target=or1k-elf \
      --enable-languages=c,c++ --disable-shared --disable-libssp --with-newlib \
      > config.log 2>&1
}

# don't think this has any dependencies
dejagnuConfig() {
    rm -rf ${DEJAGNU_BUILD}
    mkcd ${DEJAGNU_BUILD}
    ${DEJAGNU_SRC}/configure --prefix=${INSTALL} > config.log 2>&1
}

makeInstall() {
    make V=1 VERBOSE=1 ${PARALLEL} > build.log 2>&1
    make V=1 VERBOSE=1 ${PARALLEL} install > install.log 2>&1
}

bootstrapAll() {
    nameTerminal "Deleting previous installations"
    rm -rf ${INSTALL}
    rm -rf ${OR1kSIM_INSTALL}

    nameTerminal "Configuring binutils"
    binutilsConfig
    nameTerminal "Building/Installing binutils"
    cd ${BINUTILS_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error binutils"
        exit
    fi

    # add new binutils to the path
    export PATH=${INSTALL}/bin:${PATH}

    nameTerminal "Configuring LLVM/Clang"
    llvmConfig
    nameTerminal "Building/Installing llvm/clang"
    cd ${LLVM_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: LLVM/Clang"
        exit
    fi

    nameTerminal "Configuring Compiler-RT"
    compilerrtConfig
    nameTerminal "Building/Installing compiler-rt"
    cd ${COMPILER_RT_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: Compiler-RT"
        exit
    fi

    nameTerminal "Configuring or1ksim"
    or1ksimConfig
    nameTerminal "Building/Installing or1ksim"
    cd ${OR1KSIM_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: or1ksim"
        exit
    fi

    # add symlink to find clang when looking for or1k-elf cross compiler
    ln -sf ${INSTALL}/bin/clang ${INSTALL}/bin/or1k-elf-cc

    nameTerminal "Configuring newlib"
    newlibConfig
    nameTerminal "Building/Installing newlib"
    cd ${NEWLIB_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: newlib"
        exit
    fi

    nameTerminal "Configuring c-runtime"
    cruntimeConfig
    nameTerminal "Building/Installing cruntime"
    cd ${CRUNTIME_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: c-runtime"
        exit
    fi

    nameTerminal "Configuring gcc"
    gccConfig
    nameTerminal "Building/Installing gcc"
    cd ${GCC_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: gcc"
        exit
    fi
    # don't actually need to install, but may be useful anyway

    nameTerminal "Configuring DejaGNU"
    dejagnuConfig
    nameTerminal "Building/Installing DejaGNU"
    cd ${DEJAGNU_BUILD}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: DejaGNU"
        exit
    fi
}

runTests() {
    # set up path to find utilites and the simulator
    export PATH=${INSTALL}/bin:${PATH}
    export PATH=${OR1KSIM_INSTALL}/bin:${PATH}

    # set up environment to find the test tools
    export DEJAGNU=${OR1K_TOOLING}/site-sim.exp
    export DEJAGNULIBS=${INSTALL}/share/dejagnu
    export LD_LIBRARY_PATH=${OR1KSIM_INSTALL}/lib:${LD_LIBRARY_PATH}

    # ensure there's a symlink to clang so it cross compiles when testing
    ln -sf ${INSTALL}/bin/clang ${INSTALL}/bin/or1k-elf-clang

    # run gcc tests using clang, the above symlink probably isn't necessary
    cd ${GCC_BUILD}/gcc
    make check-gcc CC_UNDER_TEST=${INSTALL}/bin/or1k-elf-clang

    # run tests using clang, output to gcc.log in testsuite/gcc
    # believe the temporaries are placed in cwd
    # also believe it searches for site.exp in cwd
    # ${INSTALL}/bin/runtest --tool gcc \
    #  --tool_exec ${INSTALL}/bin/or1k-elf-clang \
    #  --srcdir ${GCC_SRC}/gcc/testsuite --outdir ${LLVM_BUILD} \
    #  --target=or1k-elf
}

if [ "$1" = "bootstrap" ]; then
    bootstrapAll
fi
if [ "$1" = "test" ]; then
    runTests
fi
if [ "$1" = "config" ]; then
    if [ "$2" = "binutils" ]; then
        binutilsConfig
    fi
    if [ "$2" = "llvm" ]; then
        llvmConfig
    fi
    if [ "$2" = "or1ksim" ]; then
        or1ksimConfig
    fi
    if [ "$2" = "compiler_rt" ]; then
        compilerrtConfig
    fi
    if [ "$2" = "newlib" ]; then
        newlibConfig
    fi
    if [ "$2" = "cruntime" ]; then
        cruntimeConfig
    fi
    if [ "$2" = "gcc" ]; then
        gccConfig
    fi
    if [ "$2" = "dejagnu" ]; then
        dejagnuConfig
    fi
fi

