from .parser import BorschTranspiler
from .errors import BorschSyntaxError, print_borsch_error

def run_file(file_path: str, show_generated_python: bool = False):
    if not file_path.endswith(".brsh"):
        print_borsch_error("Файл", "BorschScript файли повинні мати розширення .brsh!")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        transpiler = BorschTranspiler()
        py_code = transpiler.transpile(code)
    
        if show_generated_python:
            print("--- Transpiled Python Code ---")
            print(py_code)
            print("------------------------------")

        exec_globals = {"__name__": "__main__"}
        exec(py_code, exec_globals)

    except BorschSyntaxError as e:
        print_borsch_error("Помилка Синтаксису", str(e))
    except Exception as e:
        print_borsch_error("Помилка Виконання", str(e))