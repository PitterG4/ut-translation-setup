import ctypes
import winreg
import re
from pathlib import Path


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def steam_install_path():
    keys_to_try = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
    ]
    for hkey, key_path in keys_to_try:
        try:
            with winreg.OpenKey(hkey, key_path) as key:
                steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                return steam_path
        except FileNotFoundError:
            continue
    return None


def steam_game_path():
    steam_path_str = steam_install_path()
    if not steam_path_str:
        return None

    library_paths = []
    main_library_path = Path(steam_path_str) / "steamapps"
    library_paths.append(main_library_path)

    library_vdf_path = main_library_path / "libraryfolders.vdf"
    if library_vdf_path.exists():
        try:
            with open(library_vdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.finditer(r'"path"\s+"([^"]+)"', content)
                for match in matches:
                    lib_path_str = match.group(1).replace("\\\\", "\\")
                    library_paths.append(Path(lib_path_str) / "steamapps")
        except Exception:
            pass

    for lib_path in library_paths:
        game_path = lib_path / "common" / "Until Then"
        if game_path.is_dir():
            return str(game_path)

    for lib_path in library_paths:
        game_path = lib_path / "common" / "Until Then Demo"
        if game_path.is_dir():
            return str(game_path)

    return None