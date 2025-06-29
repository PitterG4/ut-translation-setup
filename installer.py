import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import sys
import shutil
import threading
from pathlib import Path

from constants import *
from etc import steam_game_path
from ui import setup_styles, create_widgets


class TranslationSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Instalador da Tradução de Until Then [PT-BR]")
        self.root.geometry("650x580")
        self.root.resizable(False, False)

        if getattr(sys, 'frozen', False):
            self.application_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
        else:
            self.application_path = Path(__file__).resolve().parent

        self.game_folder_var = tk.StringVar()
        self.game_folder_var.trace_add("write", self._on_path_changed)
        self.keep_backup_var = tk.BooleanVar(value=False)

        self.pck_explorer_path = self._find_pck_explorer()
        self.base_translation_path = self.application_path / BASE_TRANSLATION_PATH
        self.game_pck_filepath = None
        self.selected_translation_assets = None
        self.translation_type = None
        self.last_validated_path = None
        self.patch_applied_to_path = None
        self._initial_autodetect_failed = False
        self.patch_thread_running = False

        self.pck_explorer_ready = False
        self.translation_folder_ready = False

        setup_styles(self)
        create_widgets(self)

        self._initial_checks()
        self._auto_detect_game_folder()

    def _auto_detect_game_folder(self):
        detected_path = steam_game_path()
        if detected_path:
            self.game_folder_var.set(detected_path)
        else:
            self.log("Pasta do jogo não encontrada automaticamente. Por favor, selecione manualmente.")
            self._initial_autodetect_failed = True

    def _initial_checks(self):
        pck_explorer_dir = Path(self.pck_explorer_path).parent if self.pck_explorer_path else self.application_path
        mbedtls_dir = pck_explorer_dir / MBEDTLS_FOLDER_NAME

        if not self.pck_explorer_path or not os.access(self.pck_explorer_path, os.X_OK):
            self.log(f"ERRO CRÍTICO: \"{GODOT_PCK_EXPLORER}\" não foi encontrado ou não é executável.", error=True,
                     show_popup=True, popup_title="Componente Essencial Faltando")
            self.pck_explorer_ready = False
        elif not mbedtls_dir.is_dir():
            self.log(
                f"ERRO: Pasta \"{MBEDTLS_FOLDER_NAME}\" não encontrada. Ela é uma dependência de {GODOT_PCK_EXPLORER}.",
                error=True, show_popup=True, popup_title="Dependência Faltando")
            self.pck_explorer_ready = False
        else:
            self.pck_explorer_ready = True

        if not self.base_translation_path.is_dir():
            self.log(f"ERRO: Pasta de tradução \"{BASE_TRANSLATION_PATH}\" não encontrada!", error=True,
                     show_popup=True, popup_title="Erro Crítico de Arquivos")
            self.translation_folder_ready = False
        else:
            self.translation_folder_ready = True

        if not self.pck_explorer_ready or not self.translation_folder_ready:
            if hasattr(self, 'apply_button'): self.apply_button.config(state=tk.DISABLED)

    def log(self, message, error=False, show_popup=False, popup_title="Aviso"):
        self.status_text.config(state=tk.NORMAL)
        if self.status_text.get("1.0", tk.END).strip():
            self.status_text.insert(tk.END, "\n")

        tag = "error_tag" if error else "info_tag"
        self.status_text.insert(tk.END, message, tag)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

        if show_popup:
            if error:
                messagebox.showerror(popup_title, message)
            else:
                messagebox.showwarning(popup_title, message)

    def _clear_log(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete('1.0', tk.END)
        self.status_text.config(state=tk.DISABLED)

    def _find_pck_explorer(self):
        candidate = self.application_path / GODOT_PCK_EXPLORER
        if candidate.is_file():
            return str(candidate)
        if not getattr(sys, 'frozen', False):
            if shutil.which(GODOT_PCK_EXPLORER):
                return GODOT_PCK_EXPLORER
        return None

    def browse_game_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de instalação do jogo")
        if folder:
            self.game_folder_var.set(folder)

    def _on_path_changed(self, *args):
        if self._initial_autodetect_failed:
            self._clear_log()
            self._initial_autodetect_failed = False
        self._validate_game_path()

    def _validate_game_path(self):
        current_path = self.game_folder_var.get()
        if self.patch_applied_to_path == current_path:
            return

        self.apply_button.config(state=tk.DISABLED)
        self.game_pck_filepath = None
        self.selected_translation_assets = None
        self.translation_type = None

        if not self.pck_explorer_ready or not self.translation_folder_ready:
            return

        if not current_path or not Path(current_path).is_dir():
            return

        pck_path = self._check_pck_file(current_path)
        if not pck_path:
            return

        if current_path != self.last_validated_path:
            self.log(f"Pasta do jogo selecionada: \"{current_path}\".")

        self.game_pck_filepath = pck_path
        self.log(f"Arquivo \"{PCK_FILENAME}\" encontrado com sucesso.")

        version_type = self._get_game_version()
        if not version_type:
            return

        sub_dir = DEMO_TRANSLATION_SUBDIR if version_type == "Demo" else FULL_TRANSLATION_SUBDIR
        self.selected_translation_assets = str(self.base_translation_path / sub_dir / MAIN_SUBDIR_NAME)

        self.log(f"Versão do jogo: {self.translation_type}.")
        self.last_validated_path = current_path

        if self._is_ready_to_patch():
            self.apply_button.config(state=tk.NORMAL)
            self.log("\nO instalador agora está com tudo pronto. Clique em \"Aplicar\" para continuar.\n")

    def _check_pck_file(self, game_folder):
        pck_candidate = Path(game_folder) / PCK_FILENAME
        if not pck_candidate.is_file():
            self.log(f"ERRO: Arquivo \"{PCK_FILENAME}\" não encontrado em \"{game_folder}\".", error=True)
            self.last_validated_path = None
            return None
        return str(pck_candidate)

    def _get_game_version(self):
        try:
            pck_size_mb = Path(self.game_pck_filepath).stat().st_size / (1024 * 1024)
            is_demo = pck_size_mb < DEMO_PCK_SIZE
            self.translation_type = "Demo" if is_demo else "Completa"
            return self.translation_type
        except Exception as e:
            self.log(f"ERRO inesperado ao ler o arquivo PCK: {e}", error=True, show_popup=True)
            self.last_validated_path = None
            return None

    def _is_ready_to_patch(self):
        return all([
            self.pck_explorer_ready,
            self.translation_folder_ready,
            self.game_pck_filepath,
            self.selected_translation_assets,
            self.translation_type
        ])

    def _ensure_ready_to_patch(self):
        if not self._is_ready_to_patch():
            self.log("ERRO: Configuração incompleta. Verifique as mensagens de erro anteriores.", error=True,
                     show_popup=True)
            return False
        return True

    def _split_pck_filename(self):
        p = Path(PCK_FILENAME)
        return p.stem, p.suffix

    def _get_temp_pck_filepath(self):
        if not self.game_pck_filepath: return None
        game_folder = Path(self.game_pck_filepath).parent
        base, ext = self._split_pck_filename()
        return str(game_folder / f"{base}_Translated_PTBR_TEMP{ext}")

    def _get_backup_filepath(self):
        if not self.game_pck_filepath: return None
        game_dir = Path(self.game_pck_filepath).parent
        base, ext = self._split_pck_filename()
        return str(game_dir / f"{base}OLD{ext}")

    def _show_progress_bar(self):
        self.progress_bar_frame.pack(pady=(10, 5), fill=tk.X, padx=5)
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.progress_bar['value'] = 0
        self.patch_thread_running = True
        self._update_progress_bar_animation()

    def _hide_progress_bar(self):
        self.patch_thread_running = False
        self.root.after(300, self.progress_bar_frame.pack_forget)

    def _update_progress_bar_animation(self):
        if self.patch_thread_running:
            if self.progress_bar['value'] < 95:
                self.progress_bar['value'] += 1
            self.root.after(75, self._update_progress_bar_animation)

    def start_patch_thread(self):
        if not self._ensure_ready_to_patch():
            return

        backup_path = self._get_backup_filepath()
        if self.keep_backup_var.get() and backup_path and not Path(backup_path).exists():
            try:
                pck_size_gb = Path(self.game_pck_filepath).stat().st_size / (1024 * 1024 * 1024)
                msg = f"Tem certeza que deseja manter uma cópia de segurança do arquivo original?\nEla ocupará aproximadamente {pck_size_gb:.2f} GB de espaço adicional."
                if not messagebox.askyesno("Confirmar Cópia", msg):
                    self.log("Aplicação cancelada pelo usuário.")
                    return
            except Exception:
                pass

        self.apply_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.path_entry.config(state=tk.DISABLED)

        self._show_progress_bar()
        threading.Thread(target=self._execute_patch, daemon=True).start()

    def _execute_patch(self):
        temp_pck_file = self._get_temp_pck_filepath()
        command = [
            self.pck_explorer_path, "-pc", self.game_pck_filepath,
            self.selected_translation_assets, temp_pck_file,
            GODOT_VERSION_STR, PATH_PREFIX_STRING
        ]

        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, startupinfo=startupinfo, encoding='utf-8', errors='replace'
            )
            stdout, stderr = process.communicate(timeout=1800)

            if process.returncode == 0:
                self.root.after(0, self.log, "Tradução aplicada com sucesso ao arquivo temporário.")
                self._finalize_patch(temp_pck_file)
            else:
                error_output = f"\"{Path(self.pck_explorer_path).name}\" falhou (código: {process.returncode}).\n\nDetalhes:\n{stderr.strip()}"
                self.root.after(0, self._process_patch_result, False, "Erro na Aplicação", error_output)
                if Path(temp_pck_file).exists(): Path(temp_pck_file).unlink()

        except subprocess.TimeoutExpired:
            self.root.after(0, self._process_patch_result, False, "Erro de Timeout",
                            "A operação demorou mais de 30 minutos.")
        except Exception as e:
            self.root.after(0, self._process_patch_result, False, "Erro Inesperado",
                            f"Aconteceu algum erro durante a aplicação: {e}")

    def _finalize_patch(self, temp_pck_file):
        try:
            final_pck_path = self.game_pck_filepath
            backup_path_str = self._get_backup_filepath()
            backup_path = Path(backup_path_str) if backup_path_str else None
            backup_filename = backup_path.name if backup_path else "UntilThenOLD.pck"

            result_details_backup_line = ""

            if self.keep_backup_var.get():
                if backup_path and not backup_path.exists():
                    self.log(f"Criando cópia do arquivo original como \"{backup_filename}\"...")
                    shutil.move(self.game_pck_filepath, backup_path_str)
                    self.log(f"Cópia \"{backup_filename}\" criado.")
                    result_details_backup_line = f"▪ Cópia do arquivo original: \"{backup_filename}\"\n"
                else:
                    self.log(f"Removendo \"{PCK_FILENAME}\" atual...")
                    game_pck_path = Path(self.game_pck_filepath)
                    if game_pck_path.exists(): game_pck_path.unlink()
                    result_details_backup_line = f"▪ Cópia anterior preservada: \"{backup_filename}\"\n"
            else:
                self.log(f"Substituindo arquivo original \"{PCK_FILENAME}\"...")
                game_pck_path = Path(self.game_pck_filepath)
                if game_pck_path.exists(): game_pck_path.unlink()
                result_details_backup_line = "▪ Arquivo original substituído.\n"

            shutil.move(temp_pck_file, final_pck_path)
            self.log(f"\n\"{PCK_FILENAME}\" traduzido instalado.")

            result_details = (f"Tradução instalada com sucesso!\n\n"
                              f"{result_details_backup_line}"
                              f"▪ Arquivo com tradução ativa: \"{PCK_FILENAME}\"")
            self.root.after(0, self._process_patch_result, True, "Instalação Concluída!", result_details)

        except Exception as e:
            details = (f"A tradução foi processada, mas houve algum problema ao finalizar os arquivos:\n{e}\n\n"
                       f"Por gentileza, ajuste manualmente:\n"
                       f"▪ Renomeie \"{temp_pck_file}\" para \"{PCK_FILENAME}\" na pasta do jogo.")
            self.root.after(0, self._process_patch_result, False, "Erro na Finalização", details)

    def _process_patch_result(self, success, title, details):
        self.progress_bar['value'] = 100
        self.root.update_idletasks()
        self._hide_progress_bar()

        if success:
            self.patch_applied_to_path = self.last_validated_path
            self.log("Processo concluído com êxito. Parabéns!\n")
            messagebox.showinfo(title, details)
        else:
            self.log(f"ERRO: {title} - {details.splitlines()[0]}", error=True)
            messagebox.showerror(title, details)
            self.browse_button.config(state=tk.NORMAL)
            self.path_entry.config(state=tk.NORMAL)
            if self._is_ready_to_patch():
                self.apply_button.config(state=tk.NORMAL)