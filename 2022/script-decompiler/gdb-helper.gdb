# Breakpoint on a script opcode.
# It doesn't really work, maybe it's just too slow. Just use read breakpoints.
define scbreak
    # RunScriptCommand function, SCRIPT_MODE_BYTECODE
    break *0x8098d56 if *($r4 + 8) == $arg0
end

# Change the current script address
define scjump
    set *(int*)($r4 + 8) = $arg0
end
