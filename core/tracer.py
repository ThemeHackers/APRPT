import sys
import os
import inspect
from rich.console import Console
from rich.text import Text

console = Console()

class ExecutionTracer:
    def __init__(self, project_root=None):
        self.project_root = project_root or os.getcwd()
        self.active = False

    def trace_calls(self, frame, event, arg):
        if event != 'call':
            return
        
        code = frame.f_code
        func_name = code.co_name
        line_no = frame.f_lineno
        filename = code.co_filename

        if not filename.startswith(self.project_root):
            return

        rel_path = os.path.relpath(filename, self.project_root)

        module = inspect.getmodule(frame)
        module_name = module.__name__ if module else "Unknown"

        caller_frame = frame.f_back
        if caller_frame:
            caller_code = caller_frame.f_code
            caller_file = os.path.relpath(caller_code.co_filename, self.project_root)
            caller_line = caller_frame.f_lineno
            caller_info = f"{caller_file}:{caller_line}"
        else:
            caller_info = "Unknown"

        console.print(f"[dim]TRACE:[/dim] [white]{caller_info}[/white] -> [cyan]{rel_path}[/cyan]:{line_no} [green]{module_name}.{func_name}()[/green]")

        return self.trace_calls

    def start(self):
        self.active = True
        sys.settrace(self.trace_calls)
        console.print("[bold yellow][*] Verbose Execution Tracer Started[/bold yellow]")

    def stop(self):
        self.active = False
        sys.settrace(None)
        console.print("[bold yellow][*] Verbose Execution Tracer Stopped[/bold yellow]")

_tracer = None

def enable_tracing(root_dir=None):
    global _tracer
    if _tracer is None:
        _tracer = ExecutionTracer(root_dir)
    _tracer.start()

def disable_tracing():
    global _tracer
    if _tracer:
        _tracer.stop()
