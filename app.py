"""Application entrypoint for running the Flask development server."""
from __future__ import annotations

from __init__ import create_app

app = create_app()

if __name__ == "__main__":  # pragma: no cover - manual execution
    app.run(host="0.0.0.0", port=8200, debug=True)
