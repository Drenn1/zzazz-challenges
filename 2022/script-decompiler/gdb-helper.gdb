# Breakpoint on a script opcode
define sb
    # RunScriptCommand function, SCRIPT_MODE_BYTECODE
    break *0x8098d56 if *($r4 + 8) == $arg0
end
