# Jupyter Server configuration used by the practical exam workspace.
# The exam controller runs on http://127.0.0.1:7000 and embeds Jupyter
# (http://127.0.0.1:7001) in an iframe on the split-screen exam page.

c.ServerApp.allow_origin = "http://127.0.0.1:7000"
c.ServerApp.allow_credentials = True
c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": (
            "frame-ancestors 'self' http://127.0.0.1:7000 http://localhost:7000;"
        )
    }
}
