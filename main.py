import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import ctypes

from etc import is_admin
from installer import TranslationSetup 

def main():
    if os.name == 'nt' and not is_admin():
        try:
            params = " ".join(f'"{arg}"' for arg in sys.argv)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as e:
            messagebox.showerror(
                "Erro de Permissão",
                f"Não foi possível obter privilégios de administrador.\n\n"
                f"Por favor, execute o instalador como administrador.\n\n"
                f"Erro: {e}"
            )
        sys.exit(0) 

    root = tk.Tk()
    app = TranslationSetup(root)
    root.mainloop()

if __name__ == "__main__":
    main()