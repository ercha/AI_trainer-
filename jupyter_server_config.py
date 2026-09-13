# Jupyter Server configuration used by the practical exam workspace.
# The exam controller runs on http://127.0.0.1:7000 and embeds Jupyter
# (http://127.0.0.1:7001) in an iframe on the split-screen exam page.

from pathlib import Path

ROOT = Path(__file__).resolve().parent
USER_SETTINGS_DIR = str(ROOT / "jupyter_settings")

c.ServerApp.allow_origin = "http://127.0.0.1:7000"
c.ServerApp.allow_credentials = True
c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": (
            "frame-ancestors 'self' http://127.0.0.1:7000 http://localhost:7000;"
        )
    }
}

# Notebook 7 is built on JupyterLab. Point both LabServerApp and LabApp
# at this project's settings directory so autosave settings are actually loaded.
c.LabServerApp.user_settings_dir = USER_SETTINGS_DIR
c.LabApp.user_settings_dir = USER_SETTINGS_DIR
