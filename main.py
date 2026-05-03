"""Entry point — start the Flask development server."""

from app import create_app


def main() -> None:
    app = create_app()
    print("PGDBA Schedule App running at http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
