import tkinter as tk
from tkinter import ttk

def setup_styles(app):

    style = ttk.Style()
    if 'vista' in style.theme_names():
        style.theme_use('vista')
    
    app.font_normal = ("Segoe UI", 9)
    app.font_bold = ("Segoe UI", 9, "bold")
    app.font_header_title = ("Segoe UI", 12, "bold")
    app.font_header_subtitle = ("Segoe UI", 9)

    style.configure("TButton", font=app.font_normal, padding=5)
    style.configure("TLabel", font=app.font_normal, padding=2)
    style.configure("TEntry", font=app.font_normal, padding=(5, 3))
    style.configure("TLabelframe", font=app.font_normal, padding=10)
    style.configure("TLabelframe.Label", font=app.font_bold, padding=(0, 5))
    style.configure("TCheckbutton", font=app.font_normal, padding=5)
    style.configure("TProgressbar", thickness=20)

def create_widgets(app):
    header_frame = ttk.Frame(app.root, padding=(10, 10, 10, 0))
    header_frame.pack(fill=tk.X)
    ttk.Label(header_frame, text="Instalador da Tradução de Until Then [PT-BR]", font=app.font_header_title).pack(anchor=tk.W)
    ttk.Label(header_frame, text="Olá, bem-vindo! Qualquer dúvida ou erro, por favor, me avise pelo Discord: \"PitterG4\".\nTradução referente aos capítulos 1, 2 e 3.", font=app.font_header_subtitle).pack(anchor=tk.W, pady=(0, 5))
    ttk.Separator(header_frame, orient='horizontal').pack(fill='x', pady=(5, 0))

    content_frame = ttk.Frame(app.root, padding=10)
    content_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(content_frame, text="O instalador aplicará a tradução na seguinte pasta:").pack(anchor=tk.W, pady=(5, 2))
    path_frame = ttk.Frame(content_frame)
    path_frame.pack(fill=tk.X, pady=(0, 10))
    app.path_entry = ttk.Entry(path_frame, textvariable=app.game_folder_var, width=70)
    app.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    app.browse_button = ttk.Button(path_frame, text="Procurar...", command=app.browse_game_folder)
    app.browse_button.pack(side=tk.LEFT)

    status_frame = ttk.LabelFrame(content_frame, text=" Mensagens ")
    status_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    app.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD, relief=tk.FLAT, borderwidth=0, font=app.font_normal, state=tk.DISABLED, bg=app.root.cget('bg'))

    app.status_text.tag_configure("error_tag", foreground="red", font=app.font_normal)
    app.status_text.tag_configure("info_tag", foreground="black", font=app.font_normal)

    scrollbar = ttk.Scrollbar(status_frame, command=app.status_text.yview)
    app.status_text.configure(yscrollcommand=scrollbar.set)
    app.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    backup_frame = ttk.Frame(content_frame)
    backup_frame.pack(fill=tk.X, pady=(5, 0))
    ttk.Checkbutton(backup_frame, text=f"Manter cópia do arquivo original (UntilThen.pck)", variable=app.keep_backup_var).pack(anchor=tk.W)
    
    app.progress_bar_frame = ttk.Frame(content_frame)
    app.progress_bar = ttk.Progressbar(app.progress_bar_frame, orient='horizontal', mode='determinate', length=300, maximum=100)

    footer_frame = ttk.Frame(app.root, padding=10)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
    ttk.Separator(footer_frame, orient='horizontal').pack(fill='x', pady=(0, 10))
    app.apply_button = ttk.Button(footer_frame, text="Aplicar", state=tk.DISABLED, command=app.start_patch_thread)
    app.apply_button.pack(side=tk.RIGHT, padx=(5, 0))
