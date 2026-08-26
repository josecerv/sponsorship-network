"""Launch a DETACHED Codex run (gpt-5.6-sol, reasoning high) on this Windows machine.

    python pilots/scripts/codex_exec_detached.py <workdir> [--sandbox danger-full-access]

<workdir>/prompt.txt holds the full brief. Codex is pointed at that file (argv stays short: cmd.exe caps the command
line at ~8k; stdin '-' and bash $VAR expansion both arrived EMPTY under the Claude Code Bash tool). Write the brief so
that Codex WRITES its outputs to files under <workdir>/out/ (stdout is lost when detached) and lists the structure
markers it must keep byte-identical. Then wait for the output files (Monitor / until-loop on <workdir>/pid.txt) and
run md_fidelity_check.py <workdir>. Pattern proven 2026-08-21 (three passes, 2-4 minutes each).
RUN IT FROM AN UNSANDBOXED SHELL (Claude Code Bash tool with dangerouslyDisableSandbox=true, or the PowerShell tool):
under the Bash tool's sandbox Codex exits in about a minute with "CreateProcessAsUserW failed: 5 (Access is denied)" and
writes nothing (2026-08-21 late). pid.txt holds the cmd wrapper's pid; check ~/.codex/sessions/<date>/rollout-*.jsonl
for task_complete instead.
Why not the codex-companion plugin: its background `task` stalled at 600s with no tool calls; `task --help` launches a
real task named "--help".
"""
import subprocess, os, sys

D = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
# --sandbox <mode>: workspace-write (default) | danger-full-access. 2026-08-21 late: on this machine Codex's own Windows
# sandbox intermittently cannot spawn a shell ("CreateProcessAsUserW failed: 5"); with danger-full-access it runs directly.
SANDBOX = sys.argv[sys.argv.index("--sandbox") + 1] if "--sandbox" in sys.argv else "workspace-write"
D = os.path.abspath(D)
prompt = open(os.path.join(D, "prompt.txt"), encoding="utf-8").read()
assert len(prompt) > 200, "prompt.txt looks empty"
os.makedirs(os.path.join(D, "out"), exist_ok=True)
out = open(os.path.join(D, "codex_stdout.txt"), "w", encoding="utf-8")
err = open(os.path.join(D, "codex_stderr.txt"), "w", encoding="utf-8")
short = ("Your full task brief is in the file " + os.path.join(D, "prompt.txt") +
         " . Read that file first (all of it), then do exactly what it says: read the input files, write the output files "
         "to the out folder next to it, re-check the constraints it lists, and reply with the short summary it asks for.")
cmd = ["codex", "exec", "-m", "gpt-5.6-sol", "-c", "model_reasoning_effort=high", "-s", SANDBOX,
       "-C", r"C:\Users\jcerv\Jose\sponsorship-network", short]
p = subprocess.Popen(cmd, stdout=out, stderr=err, shell=True,
                     creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
open(os.path.join(D, "pid.txt"), "w").write(str(p.pid))
print("launched codex pid", p.pid, "| sandbox", SANDBOX, "| brief chars", len(prompt), "| outputs expected in", os.path.join(D, "out"))
