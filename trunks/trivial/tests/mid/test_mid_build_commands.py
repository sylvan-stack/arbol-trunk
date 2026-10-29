"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_build_commands as _support
from test_build_commands import (
    BuildCommands,
    Path,
    ROOT,
    json,
    os,
    read_object,
    shlex,
    subprocess,
    sys,
    tempfile,
    unittest,
)


class BuildCommands(_support.BuildCommands):
# TEST-TIER-BEGIN trunks/trivial/tests/test_build_commands.py::BuildCommands.test_the_contract_shell_command_passes_one_executable_path_with_spaces
    def test_the_contract_shell_command_passes_one_executable_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            folder = base / "Application Support/builds/arbol-trunk/trivial/a"
            python = folder / "runtime/python/bin/python3.14"
            python.parent.mkdir(parents=True)
            python.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} \"$@\"\n")
            python.chmod(0o755)
            entry = folder / "bin/arbol-trunk-trivial"
            entry.parent.mkdir()
            entry.write_text("#!/bin/sh\nexit 0\n")
            entry.chmod(0o755)
            fixture = base / "conformance fixture.py"
            fixture.write_text("import json,shlex,sys\n"
                               "print(json.dumps({'trunk':shlex.split(sys.argv[sys.argv.index('--trunk')+1]),"
                               "'version':sys.argv[sys.argv.index('--root-contract')+1]}))\n")
            checks = read_object(ROOT / "arbol-build.json")["checks"]
            command = next(item["command"] for item in checks if item["name"] == "contract-1")
            external = "~/repos/sylvan-stack/readonly/arbol-root/contract/conformance/bin/rct-conformance.py"
            self.assertIn(external, command)
            command = command.replace(external, shlex.quote(str(fixture)))
            result = subprocess.run(command, shell=True, cwd=base, timeout=10, capture_output=True, text=True,
                                    env={"HOME": str(base), "PATH": "/usr/bin:/bin", "LANG": "C",
                                         "ARBOL_BUILD_DIR": str(folder)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"trunk": [str(entry)], "version": "1"})
            self.assertTrue(os.access(entry, os.X_OK))
# TEST-TIER-END trunks/trivial/tests/test_build_commands.py::BuildCommands.test_the_contract_shell_command_passes_one_executable_path_with_spaces
