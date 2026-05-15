import os
import sys
import webbrowser
import time
import io
import threading
import socket

# ✅ Evita loop infinito do executável (ESSENCIAL)
if os.environ.get("STREAMLIT_RUNNING") == "1":
    pass
else:
    os.environ["STREAMLIT_RUNNING"] = "1"

# ✅ Corrige erro quando roda sem console (--noconsole)
if sys.stdout is not None:
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def wait_for_server(host="localhost", port=8501, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except:
            time.sleep(0.5)
    return False


def open_browser():
    if wait_for_server():
        webbrowser.open("http://localhost:8501")


def pause():
    try:
        input()
    except:
        time.sleep(5)


def main():
    # ✅ bloqueio extra contra reexecução
    if os.environ.get("STREAMLIT_RUNNING") != "1":
        return

    base_path = get_base_path()
    app_path = os.path.join(base_path, "app.py")

    if not os.path.exists(app_path):
        print(f"[ERRO] app.py não encontrado: {app_path}")
        pause()
        sys.exit(1)

    print("=" * 60)
    print("LIMPEZA DE DUPLICADOS - BASE_PEDIDOS")
    print("=" * 60)
    print("[OK] Iniciando aplicação...")
    print(f"Caminho base: {base_path}")
    print(f"Aplicacao: {app_path}")
    print("=" * 60)

    try:
        threading.Thread(target=open_browser, daemon=True).start()

        sys.argv = ["streamlit", "run", app_path]
        sys.argv += [
            "--server.port=8501",
            "--server.headless=true",
            "--server.runOnSave=false",
            "--logger.level=error",
        ]

        from streamlit.web import cli as stcli
        stcli.main()

    except Exception as e:
        print(f"[ERRO] Falha ao iniciar: {str(e)}")
        pause()
        sys.exit(1)


if __name__ == "__main__":
    main()