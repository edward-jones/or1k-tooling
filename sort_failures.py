#!/usr/bin/env python2


import sys
import re
import subprocess


if len(sys.argv) != 2:
    print >> sys.stderr, "No input log file supplied"
    exit(1)

log_file = sys.argv[1]


# regular expressions of errors which need to be filtered out of the tests
error_regexps = [
    # unknown arguments
    r"""error: unknown argument: '-fabi-version=1'""",
    r"""error: unknown argument: '-falign-labels=8'""",
    r"""error: unknown argument: '-fallow-parameterless-variadic-functions'""",
    r"""error: unknown argument: '-fcheck-data-deps'""",
    r"""error: unknown argument: '-fcompare-debug'""",
    r"""error: unknown argument: '-fcond-mismatch'""",
    r"""error: unknown argument: '-fcrossjumping'""",
    r"""error: unknown argument: '-fcse-follow-jumps'""",
    r"""error: unknown argument: '-fcx-fortran-rules'""",
    r"""error: unknown argument: '-fcx-limited-range'""",
    r"""error: unknown argument: '-fdelete-null-pointer-checks'""",
    r"""error: unknown argument: '-fdirectives-only'""",
    r"""error: unknown argument: '-fdisable-ipa-inline'""",
    r"""error: unknown argument: '-fdisable-tree-cunroll.*'""",
    r"""error: unknown argument: '-fdisable-tree-cunrolli.*'""",
    r"""error: unknown argument: '-fdisable-tree-einline.*'""",
    r"""error: unknown argument: '-fdump-.*'""",
    r"""error: unknown argument: '-feliminate-dwarf2-dups'""",
    r"""error: unknown argument: '-femit-struct-debug-baseonly'""",
    r"""error: unknown argument: '-femit-struct-debug-detailed.*'""",
    r"""error: unknown argument: '-femit-struct-debug-reduced'""",
    r"""error: unknown argument: '-fenable-rtl-loop2_unroll.*'""",
    r"""error: unknown argument: '-ffat-lto-objects'""",
    r"""error: unknown argument: '-fgcse-after-reload'""",
    r"""error: unknown argument: '-fgcse-las'""",
    r"""error: unknown argument: '-fgcse-sm'""",
    r"""error: unknown argument: '-fguess-branch-probability'""",
    r"""error: unknown argument: '-fhoist-adjacent-loads'""",
    r"""error: unknown argument: '-findirect-inlining'""",
    r"""error: unknown argument: '-finline-small-functions'""",
    r"""error: unknown argument: '-finstrument-functions-exclude-file-list=instrument-3'""",
    r"""error: unknown argument: '-finstrument-functions-exclude-function-list=fn'""",
    r"""error: unknown argument: '-fipa-.*'""",
    r"""error: unknown argument: '-fira-algorithm=priority'""",
    r"""error: unknown argument: '-fisolate-erroneous-paths-attribute'""",
    r"""error: unknown argument: '-fleading-underscore'""",
    r"""error: unknown argument: '-flive-range-shrinkage'""",
    r"""error: unknown argument: '-fmodulo-sched'""",
    r"""error: unknown argument: '-fmodulo-sched-allow-regmoves'""",
    r"""error: unknown argument: '-fmove-loop-invariants'""",
    r"""error: unknown argument: '-fno-crossjumping'""",
    r"""error: unknown argument: '-fno-dce'""",
    r"""error: unknown argument: '-fno-delete-null-pointer-checks'""",
    r"""error: unknown argument: '-fno-dse'""",
    r"""error: unknown argument: '-fno-early-inlining'""",
    r"""error: unknown argument: '-fno-foobar'""",
    r"""error: unknown argument: '-fno-forward-propagate'""",
    r"""error: unknown argument: '-fno-guess-branch-probability'""",
    r"""error: unknown argument: '-fno-inline-atomics'""",
    r"""error: unknown argument: '-fno-ipa-cp'""",
    r"""error: unknown argument: '-fno-ipa-pure-const'""",
    r"""error: unknown argument: '-fno-ipa-sra'""",
    r"""error: unknown argument: '-fno-ira-share-save-slots'""",
    r"""error: unknown argument: '-fno-isolate-erroneous-paths-dereference'""",
    r"""error: unknown argument: '-fno-merge-debug-strings'""",
    r"""error: unknown argument: '-fno-move-loop-invariants'""",
    r"""error: unknown argument: '-fno-openmp'""",
    r"""error: unknown argument: '-fno-partial-inlining'""",
    r"""error: unknown argument: '-fno-peel-loops'""",
    r"""error: unknown argument: '-fno-rename-registers'""",
    r"""error: unknown argument: '-fno-strict-volatile-bitfields'""",
    r"""error: unknown argument: '-fno-toplevel-reorder'""",
    r"""error: unknown argument: '-fno-tree-.*'""",
    r"""error: unknown argument: '-fno-vect-cost-model'""",
    r"""error: unknown argument: '-fno-web'""",
    r"""error: unknown argument: '-fopenmp-simd'""",
    r"""error: unknown argument: '-fopt-info'""",
    r"""error: unknown argument: '-fpeel-loops'""",
    r"""error: unknown argument: '-fplan9-extensions'""",
    r"""error: unknown argument: '-fplugin-arg-selfassign-disable'""",
    r"""error: unknown argument: '-fplugin=./finish_unit_plugin.so'""",
    r"""error: unknown argument: '-fplugin=foo'""",
    r"""error: unknown argument: '-fplugin=./ggcplug.so'""",
    r"""error: unknown argument: '-fplugin=./one_time_plugin.so'""",
    r"""error: unknown argument: '-fplugin=./selfassign.so'""",
    r"""error: unknown argument: '-fplugin=./start_unit_plugin.so'""",
    r"""error: unknown argument: '-fpredictive-commoning'""",
    r"""error: unknown argument: '-fpreprocessed'""",
    r"""error: unknown argument: '-free'""",
    r"""error: unknown argument: '-frename-registers'""",
    r"""error: unknown argument: '-frerun-cse-after-loop'""",
    r"""error: unknown argument: '-fsched2-use-superblocks'""",
    r"""error: unknown argument: '-fsched-pressure'""",
    r"""error: unknown argument: '-fsched-stalled-insns=0'""",
    r"""error: unknown argument: '-fschedule-insns2'""",
    r"""error: unknown argument: '-fselective-scheduling'""",
    r"""error: unknown argument: '-fsingle-precision-constant'""",
    r"""error: unknown argument: '-fsplit-wide-types'""",
    r"""error: unknown argument: '-fstack-check=generic'""",
    r"""error: unknown argument: '-fstack-check=specific'""",
    r"""error: unknown argument: '-fstack-limit'""",
    r"""error: unknown argument: '-fstack-usage'""",
    r"""error: unknown argument: '-fstrict-volatile-bitfields'""",
    r"""error: unknown argument: '-ftrack-macro-expansion.*'""",
    r"""error: unknown argument: '-ftree-.*'""",
    r"""error: unknown argument: '-funsafe-loop-optimizations'""",
    r"""error: unknown argument: '-funroll-loops-all'""",
    r"""error: unknown argument: '-fvariable-expansion-in-unroller'""",
    r"""error: unknown argument: '-fvar-tracking'""",
    r"""error: unknown argument: '-fvar-tracking-assignments'""",
    r"""error: unknown argument: '-fvect-cost-model=dynamic'""",
    r"""error: unknown argument: '-fwhole-program'""",
    r"""error: unknown argument: '-gdwarf'""",
    r"""error: unknown argument: '-mno-foobar'""",
    r"""error: unknown argument: '-tfoo'""",
    
    # Unused argument warnings
    """warning: argument unused during compilation: '-dI'""",
    """warning: argument unused during compilation: '-dN'""",
    """warning: argument unused during compilation: '-dU'""",
    """warning: argument unused during compilation: '-dP'""",
    """warning: argument unused during compilation: '-finline-limit=0'""",
    """warning: argument unused during compilation: '-fmax-errors=3'""",
    """warning: argument unused during compilation: '-fprofile-generate'""",
    """warning: argument unused during compilation: '-march=foo'""",
    """warning: argument unused during compilation: '--param allow-store-data-races=0'""",
    """warning: argument unused during compilation: '--param ggc-min-expand=0'""",
    """warning: argument unused during compilation: '--param ggc-min-heapsize=0'""",
    """warning: argument unused during compilation: '--param hot-bb-frequency-fraction=0'""",
    """warning: argument unused during compilation: '--param large-stack-frame=10'""",
    """warning: argument unused during compilation: '--param large-stack-frame-growth=2'""",
    """warning: argument unused during compilation: '--param max-cse-insns=1'""",
    """warning: argument unused during compilation: '--param max-partial-antic-length=0'""",
    """warning: argument unused during compilation: '--param max-predicted-iterations=0'""",
    """warning: argument unused during compilation: '-specs=.*'""",
    """warning: argument unused during compilation: '-Xassembler -dumpmachine'""",
    """warning: -lm: 'linker' input unused""",

    # Unknown warnings
    r"""warning: unknown warning option '.*' \[-Wunknown-warning-option\]""",
    r"""error: unknown warning option '.*' \[-Werror,-Wunknown-warning-option\]""",
    r"""warning: unknown warning option '.*'\; did you mean '.*'\? \[-Wunknown-warning-option\]""",
    r"""error: unknown warning option '.*'\; did you mean '.*'\? \[-Werror,-Wunknown-warning-option\]""",
    r"""error: unknown warning group '-Wunused-local-typedefs', ignored \[-Werror,-Wunknown-pragmas\]""",

    # Unsupported options
    r"""error: unsupported option '-gstabs.*'""",
    r"""error: unsupported option '-gxcoff.*'""",
    r"""error: unsupported option '-gcoff.*'""",
    r"""error: unsupported option '--dump=a'""",

    # tautological
    r"""warning: comparison of unsigned enum expression >= 0 is always true \[-Wtautological-compare\]""",
    r"""warning: self-comparison always evaluates to a constant \[-Wtautological-compare\]""",
    r"""warning: self-comparison always evaluates to false \[-Wtautological-compare\]""",
    r"""warning: comparison of constant .* with expression of type '[\s\S]*' is always true \[-Wtautological-constant-out-of-range-compare\]""",
    r"""warning: comparison of array '.*' equal to a null pointer is always false \[-Wtautological-pointer-compare\]""",
    r"""warning: comparison of address of '.*' not equal to a null pointer is always true \[-Wtautological-pointer-compare\]""",

    # builtin
    r"""warning: declaration of built-in function '.*' requires inclusion of the header .* \[-Wbuiltin-requires-header\]""",
    r"""error: use of unknown builtin '__builtin_shuffle' \[-Wimplicit-function-declaration\]""",
    r"""error: use of unknown builtin '__builtin_puts' \[-Wimplicit-function-declaration\]""",
    r"""error: cannot compile this builtin function yet""",
    r"""error: use of unknown builtin '.*' \[-Wimplicit-function-declaration\]""",
    r"""error: definition of builtin function '.*'""",

    # attributes
    r"""warning: attribute declaration must precede definition \[-Wignored-attributes\]""",
    r"""warning: 'cold' attribute only applies to functions \[-Wignored-attributes\]""",
    r"""warning: 'packed' attribute ignored for field of type 'char' \[-Wignored-attributes\]""",
    r"""warning: alias will always resolve to .* even if weak definition of alias .* is overridden \[-Wignored-attributes\]""",
    r"""warning: 'format' attribute only applies to functions \[-Wignored-attributes\]""",
    r"""warning: '__format__' attribute argument not supported""",
    r"""warning: unknown attribute '.*' ignored \[-Wunknown-attributes\]""",
    r"""warning: unknown attribute 'optimize' ignored \[-Wunknown-attributes\]""",
    r"""warning: ignoring return value of function declared with const attribute \[-Wunused-value\]""",
    r"""error: strftime format attribute requires 3rd parameter to be 0""",
    r"""error: weakref declaration of '.*' must also have an alias attribute""",
    r"""error: '.*' attribute invalid on this declaration, requires typedef or value""",

    # assembly
    r"""error: invalid input constraint 's' in asm""",
    r"""error: invalid operand for inline asm constraint '.*'""",
    r"""error: invalid operand in inline asm:""",
    r"""error: invalid lvalue in asm output""",
    r"""error: invalid lvalue in asm input for constraint '.*'""",
    r"""error: inline asm not supported yet: don't know how to handle tied indirect register inputs""",
    r"""error: expected '\(' after 'asm'""",
    r"""error: invalid use of a cast in a inline asm context requiring an l-value: remove the cast or build with -fheinous-gnu-extensions""",

    # expected
    r"""warning: expected '\;' at end of declaration list""",
    r"""error: expected '\;' after top level declarator""",
    r"""error: expected '\;' after return statement""",
    r"""error: expected '\;' after struct""",
    r"""error: expected '\;' after enum""",
    r"""error: expected identifier or '\('""",
    r"""error: expected '\;' in 'for' statement specifier""",
    r"""error: expected '\)'""",
    r"""error: expected expression""",
    r"""error: expected statement""",
    r"""error: expected end of line in preprocessor expression""",
    r"""error: expected "FILENAME" or <FILENAME>""",
    r"""error: expected comma in macro parameter list""",

    # missing/unsupported extensions
    r"""warning: use of GNU old-style field designator extension \[-Wgnu-designator\]""",
    r"""warning: empty macro arguments are a C99 feature \[-Wc99-extensions\]""",
    r"""warning: anonymous structs are a Microsoft extension \[-Wmicrosoft\]""",
    r"""error: variable length arrays are a C99 feature \[-Werror,-Wvla-extension\]""",
    r"""error: anonymous structs are a C11 extension \[-Werror,-Wc11-extensions\]""",
    r"""error: ordered comparison between pointer and zero \([\s\S]*\) is an extension \[-Werror,-Wpedantic\]""",
    r"""error: fields must have a constant size: 'variable length array in structure' extension will never be supported""",
    r"""error: #line directive with zero argument is a GNU extension""",

    # unused
    r"""warning: unused variable '.*' \[-Wunused-variable\]""",
    r"""warning: unused parameter '.*' \[-Wunused-parameter\]""",
    r"""warning: equality comparison result unused \[-Wunused-comparison\]""",
    r"""warning: inequality comparison result unused \[-Wunused-comparison\]""",
    r"""warning: expression result unused \[-Wunused-value\]""",
    r"""error: unused function '.*' \[-Werror,-Wunused-function\]""",

    # implicit
    r"""warning: implicit conversion from '.*' to '.*' changes value from .* to .*""",
    r"""warning: implicitly declaring library function '.*' with type '[\s\S]*'""",
    r"""warning: implicit truncation from '.*' to bitfield changes value from .* to .* \[-Wbitfield-constant-conversion\]""",
    r"""warning: implicit declaration of function '.*' is invalid in C99 \[-Wimplicit-function-declaration\]""",
    r"""error: implicit declaration of function '.*' is invalid in C99 \[-Werror,-Wimplicit-function-declaration\]""",
    r"""warning: type specifier missing, defaults to 'int' \[-Wimplicit-int\]""",
    r"""error: type specifier missing, defaults to 'int' \[-Werror,-Wimplicit-int\]""",

    # definition
    r"""warning: tentative array definition assumed to have one element""", 
    r"""error: alias definition is part of a cycle""",
    r"""error: redefinition of '.*' as different kind of symbol""",
    r"""error: redefinition of a 'extern inline' function .* is not supported in C99 mode""",
    r"""error: function definition is not allowed here""",
 
    # declaration
    r"""warning: declaration does not declare anything \[-Wmissing-declarations\]""",
    r"""warning: incompatible redeclaration of library function '.*' \[-Wincompatible-library-redeclaration\]""",
    r"""warning: duplicate 'inline' declaration specifier \[-Wduplicate-decl-specifier\]""",
    r"""error: parameter '.*' was not declared, defaulting to type 'int' \[-Werror,-Wpedantic\]""",
    r"""error: weak declaration cannot have internal linkage""",
    r"""error: static declaration of .* follows non-static declaration""",
    r"""error: second parameter of 'main' \(argument array\) must be of type 'char \*\*'""",
    r"""error: use of undeclared identifier .*""",
    r"""error: use of undeclared label .*""",
    r"""error: visibility does not match previous declaration""",

    # initialization
    r"""warning: initializing '[\s\S]*' [\s\S] with an expression of type '[\s\S]*' [\s\S]* converts between pointers to integer types with different sign \[-Wpointer-sign\]""",
    r"""warning: variable '.*' is uninitialized when used within its own initialization \[-Wuninitialized\]""",
    r"""warning: variable '.*' is uninitialized when used here \[-Wuninitialized\]""",
    r"""warning: 'extern' variable has an initializer \[-Wextern-initializer\]""",
    r"""warning: initializer overrides prior initialization of this subobject \[-Winitializer-overrides\]""",
    r"""error: initializer element is not a compile-time constant""",
    r"""error: flexible array requires brace-enclosed initializer""",
    r"""error: array initializer must be an initializer list""",
    r"""error: incompatible pointer types initializing '[\s\S]*' [\s\S]* with an expression of type '[\s\S]*'""",
    r"""error: initialization of flexible array member is not allowed""",
    r"""error: initializing '[\s\S]*' [\s\S] with an expression of type '[\s\S]*' [\s\S]* discards qualifiers \[-Werror,-Wincompatible-pointer-types-discards-qualifiers\]""",

    # general
    r"""warning: adding 'int' to a string does not append to the string \[-Wstring-plus-int\]""",
    r"""error: format argument not an NSString""",
    r"""warning: no case matching constant switch condition '.*'""",
    r"""error: array has incomplete element type '[\s\S]*'""",
    r"""warning: promoted type 'double' of K\&R function parameter is not compatible with the parameter type 'float' declared in a previous prototype""",
    r"""warning: ISO C requires a translation unit to contain at least one declaration""",
    r"""error: ISO C requires a translation unit to contain at least one declaration""",
    r"""error: restrict requires a pointer or reference""",
    r"""warning: plain '_Complex' requires a type specifier\; assuming '_Complex double'""",
    r"""error: exponent has no digits""",
    r"""warning: unknown action for '[\s\S]*' - ignored \[-Wignored-pragmas\]""",
    r"""warning: assigning to '[\s\S]*' [\s\S]* from '[\s\S]*' [\s\S]* converts between pointers to integer types with different sign \[-Wpointer-sign\]""",
    r"""warning: passing '[\s\S]*' [\s\S]* to parameter of type '[\s\S]*' [\s\S]* converts between pointers to integer types with different sign \[-Wpointer-sign\]""",
    r"""warning: using the result of an assignment as a condition without parentheses \[-Wparentheses\]""",
    r"""error: too many parameters \(.*\) for '.*': must be 0, 2, or 3""",
    r"""error: address of vector element requested""",
    r"""warning: null passed to a callee which requires a non-null argument \[-Wnonnull\]""",
    r"""warning: weak identifier '.*' never declared""",
    r"""error: cannot compile this unexpected cast lvalue yet""",
    r"""error: cannot increment value of type '[\s\S]*'""",
    r"""warning: missing terminating '.' character \[-Winvalid-pp-token\]""",
    r"""warning: .* has lower precedence than .*\; .* will be evaluated first \[-Wparentheses\]""",
    r"""warning: expression which evaluates to zero treated as a null pointer constant of type '[\s\S]*' \[-Wnon-literal-null-conversion\]""",
    r"""warning: '\&\&' within '\|\|' \[-Wlogical-op-parentheses\]""",
    r"""error: too few arguments to function call, expected .*, have .*""",
    r"""warning: add explicit braces to avoid dangling else \[-Wdangling-else\]""",
    r"""error: can't convert between vector values of different size""",
    r"""warning: unsequenced modification and access to '.*' \[-Wunsequences\]""",
    r"""error: designator into flexible array member subobject""",
    r"""warning: sizeof on array function parameter will return size of '[\s\S]*' instead of '[\s\S]*' \[-Wsizeof-array-argument\]""",
    r"""warning: qualifier on function type '.*' [\s\S]* has unspecified behavior""",
    r"""error: cannot compile this complex va_arg expression yet""",
    r"""warning: unsequenced modification and access to '.*' \[-Wunsequenced\]""",
    r"""error: controlling expression type '[\s\S]*' not compatible with any generic association type""",
    r"""error: 'main' is not allowed to be declared _Noreturn \[-Werror,-Wmain\]""",
    r"""error: static_assert expression is not an integral constant expression""",
    r"""warning: sizeof on pointer operation will return size of '[\s\S]*' instead of '[\s\S]*' \[-Wsizeof-array-decay\]""",
    r"""warning: format string is not a string literal \(potentially insecure\) \[-Wformat-security\]""",
    r"""warning: 'continue' is bound to current loop, GCC binds it to the enclosing loop \[-Wgcc-compat\]""",
    r"""warning: if statement has empty body \[-Wempty-body\]""",
    r"""warning: incompatible pointer types passing '[\s\S]*' [\s\S]* to parameter of type '[\s\S]*'""",
    r"""error: using extended field designator""",
    r"""warning: more '\%' conversions than data arguments \[-Wformat\]""",
    r"""warning: magnitude of floating-point constant too large for type '.*'\; maximum is .* \[-Wliteral-range\]""",
    r"""error: extraneous '\)' before '\;'""",
    r"""error: invalid suffix '.*' on floating constant""",
    r"""error: ".* not defined\"""",
    r"""undefined reference to `.*'""",
    r"""warning: the clang compiler does not support '.*'""",
    r"""error: the clang compiler does not support '.*'""",
    r"""error: option '-MG' requires '-M' or '-MM'""",
    r"""error: invalid integral value '' in '-ftemplate-depth '""",
    r"""warning: equality comparison with extraneous parentheses \[-Wparentheses-equality\]""",
    r"""warning: division by zero is undefined \[-Wdivision-by-zero\]""",
    r"""error: conflicting types for '.*'""",
    r"""error: '.*' declared as an array with a negative size""",
    r"""warning: stack frame size of .* bytes in function '.*' \[-Wframe-larger-than=\]""",
    r"""warning: overflow in expression\; result is .* with type 'int' \[-Winteger-overflow\]""",
    r"""error: non-void function .* should return a value \[-Wreturn-type\]""",
    r"""error: indirect goto in function with no address-of-label expressions""",
    r"""error: void function .* should not return a value \[-Wreturn-type\]""",
    r"""fatal error: bracket nesting level exceeded maximum of .*""",
    r"""error: clang frontend command failed with exit code 70""",
    r"""warning: incomplete universal character name\; treating as '\\' followed by identifier \[-Wunicode\]""",
    r"""error: second argument to .* is of incomplete type 'void'""",
    r"""error: control reaches end of non-void function \[-Werror,-Wreturn-type\]""",
    r"""warning: control reaches end of non-void function \[-Wreturn-type\]""",
    r"""Return operand #2 has unhandled type i32\nUNREACHABLE executed at .*""",
    r"""error: pasting formed 'socket:', an invalid preprocessing token""",
    r"""warning: backslash and newline separated by space \[-Wbackslash-newline-escape\]""",
    r"""warning: character constant too long for its type""",
    r"""error: macro name must be an identifier""",
    r"""fatal error: 'silly\\"' file not found""",
    r"""error: #line directive requires a positive integer argument""",
    r"""error: _OPENMP not defined""",
    r"""error: _OPENMP defined to wrong value""",
    r"""warning: '/\*' within block comment \[-Wcomment\]""",
    r"""error: '##' cannot appear at end of macro expansion""",
    r"""error: pasting formed '.*', an invalid preprocessing token""",
    r"""error: invalid token at start of a preprocessor expression""",
    r"""error: invalid preprocessing directive""",
    r"""warning: pragma pop_macro could not pop '.*', no matching push_macro \[-Wignored-pragmas\]""",
    r"""warning: universal character names are only valid in C99 or C\+\+\; treating as '\\' followed by identifier \[-Wunicode\]""",
    r"""error: illegal character encoding in string literal""",
    r"""error: invalid universal character""",
    r"""warning: array index .* is past the end of the array \(which contains .* elements?\) \[-Warray-bounds\]""",
    r"""warning: array index .* is before the beginning of the array \[-Warray-bounds\]""",
    r"""error: '.*': unable to pass LLVM bit-code files to linker""",
    r"""warning: control may reach end of non-void function \[-Wreturn-type\]""",
    r"""warning: null character\(s\) preserved in string literal \[-Wnull-character\]""",
    r"""warning: non-constant static local variable in inline function may be different in different files \[-Wstatic-local-in-inline\]""",

    # Missed expected errors, warnings and bogus
    r"""Excess errors:[\s\S]*dg-error""",
    r"""Excess errors:[\s\S]*dg-warning""",
    r"""Excess errors:[\s\S]*dg-bogus""",

    r"""Excess errors:[\s\S]*\[-Wtrigraphs\]""",
    r"""Excess errors:[\s\S]*\[-Winvalid-pp-token\]""",
    r"""Excess errors:[\s\S]*\[-Wmacro-redefined\]""",
    r"""Excess errors:[\s\S]*#error""",
    r"""Excess errors:[\s\S]*string literal""", 
 
    #### Genuine errors?
    
    # Get reent failure
    r"""multiple definition of \`__getreent'""",

    # -Og unsupported
    r"""error: invalid integral value 'g' in '-Og'""",

    # LTO unsupported
    r"""-O2 -flto""",
    
    # Assertion failures
    r"""Assertion `MI->isCall\(\) \|\| MI->isBranch\(\)' failed\.""",
    r"""Assertion `NumParams == params.size\(\) \&\& "function has too many parameters"' failed\.""",
    r"""Assertion `\!isAnnotation\(\) \&\& "getIdentifierInfo\(\) on an annotation token\!"' failed\.""",
    r"""Assertion `Size \!= 0 && "Cannot allocate zero size stack objects!"' failed\.""",
    r"""Assertion `\!VT\.isVector\(\) \&\& "No default SetCC type for vectors\!"' failed\.""",
    r"""Assertion \`isScalar\(\) \&\& "Not a scalar\!"' failed\.""",
    r"""Assertion \`\(ND->isUsed\(false\) \|\| \!isa<VarDecl>\(ND\) \|\| \!E->getLocation\(\)\.isValid\(\)\) \&\& "Should not use decl without marking it used\!"' failed\.""",
    
    # Misc errors
    r"""fatal error:[\s\S]*\^""",
    r"""Call result #2 has unhandled type i32\nUNREACHABLE executed at .*""",
    r"""Unknown type!\nUNREACHABLE executed at .*""",
    r"""Excess errors:[\s\S]*illegal operand""",
    
    # Catch all for errors causing a printed stack trace
    r"""Excess errors:[\s\S]*llvm::sys::PrintStackTrace""",

    # Catch all for every remaining error
    r""".*"""
]


# clear file holding all the filtered tests
#open(log_file + '.' + 'diff', 'w').close()


# remove each set of errors in turn
for i in range(0, len(error_regexps)):
    if i == 0:
        in_file = open(log_file, 'r')
    else:
        in_file = open(log_file + '.' + str(i - 1), 'r')

    #diff_file = open(log_file + '.' + 'diff', 'a')
    out_file  = open(log_file + '.' + str(i), 'w')

    # write out the regular expression to the diff file
    sys.stdout.write('\n')
    print '# Error regexp: ' + error_regexps[i]
    sys.stdout.write('\n')
    sys.stdout.flush()

    subprocess.call(['./filter_tests.py', error_regexps[i]],
          stdin=in_file, stdout=out_file)
    
    in_file.seek(0)
    subprocess.call(['./filter_tests.py', '-match', error_regexps[i]],
          stdin=in_file)

    out_file.close()
    #diff_file.close()
    in_file.close()

