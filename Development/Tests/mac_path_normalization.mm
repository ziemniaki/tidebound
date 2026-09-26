// Compiled against the header used by the patched runtime, not a Python model.
#include "portablePathApple.h"
#include <iostream>
#include <stdexcept>
#include <unistd.h>

static void check(const std::string &input, const std::string &expected, bool absolute = false) {
    std::string actual = portableGamePath(input.c_str(), absolute);
    if (actual != expected) throw std::runtime_error(input + " -> " + actual + "; expected " + expected);
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 2 || chdir(argv[1]) != 0) return 2;
        check("Data/Scripts.rxdata", "Data/Scripts.rxdata");
        check("Data\\Scripts.rxdata", "Data/Scripts.rxdata");
        check("./Data/../Data/Scripts.rxdata", "Data/Scripts.rxdata");
        check("Audio/BGM/Rout\xc3\xa9 1.mid", "Audio/BGM/Route\xcc\x81 1.mid");
        auto cwd = ghc::filesystem::current_path();
        check((cwd / "Data/Scripts.rxdata").string(), "Data/Scripts.rxdata");
        auto alias = cwd.string();
        if (alias.find("/private/var/") == 0) {
            alias.erase(0, 8);
            check(alias + "/Data/Scripts.rxdata", "Data/Scripts.rxdata");
        }
        auto abs = portableGamePath("Data/Scripts.rxdata", true);
        if (!ghc::filesystem::path(abs).is_absolute() || !ghc::filesystem::exists(abs))
            throw std::runtime_error("absolute path lost its target: " + abs);
        auto outside = cwd.parent_path() / "different-game/Data/Scripts.rxdata";
        if (!ghc::filesystem::path(portableGamePath(outside.c_str(), false)).is_absolute())
            throw std::runtime_error("stripped an unrelated directory prefix");
        std::cout << "PASS: native path resolution in " << argv[1] << std::endl;
    }
}
