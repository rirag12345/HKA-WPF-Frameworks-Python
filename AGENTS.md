# AGENTS.md - Leitfaden für KI-Agenten

Dieses Dokument definiert die strikten Entwicklungsrichtlinien für das FastAPI Book Management-Projekt in diesem Repository. Lies diese Regeln sorgfältig, bevor du Code generierst oder veränderst.

## 1. Projekt-Architektur (Domain-Driven Design)
Das Projekt nutzt ein Source-Layout (`src/book/`) und folgt einer strikten Schichtenarchitektur. Die Zuständigkeiten dürfen **nicht** vermischt werden:
* **`entity/`**: Beinhaltet ausschließlich SQLAlchemy 2.0 Mapped Classes (das Datenmodell). Keine Geschäftslogik.
* **`repository/`**: Isoliert den reinen Datenbankzugriff.
* **`service/`**: Enthält die Geschäftslogik. Holt Daten aus dem Repository und wandelt sie in Pydantic-DTOs um.
* **`router/`**: Die REST-Schnittstelle (`APIRouter`). Nimmt Requests an und ruft den Service via Dependency Injection (`Depends()`) auf.
* **Kapselung (Facade-Pattern)**: Jede Schicht (`entity/`, `repository/`, `service/`, `router/`) MUSS eine `__init__.py` Datei besitzen. Nutze dort zwingend die `__all__ = [...]` Variable, um nur die Klassen nach außen zu exportieren, die Teil der öffentlichen API dieser Schicht sind. Die nächsthöhere Schicht darf nur über die `__init__.py` importieren (z.B. `from book.repository import BookRepository`).

## 2. Tech-Stack & Kernwerkzeuge
* **Python**: `>=3.14` (in `pyproject.toml` unter `requires-python` festgelegt).
* **Paket- und Projektmanager**: `uv` (Nutze ausschließlich `uv run`, `uv sync` oder `uvx` für Skripte. Kein `pip`!).
* **Framework**: FastAPI mit Pydantic V2 + `pydantic-settings` für konfigurationsbasierte Settings-Klassen (z.B. `BaseSettings`).
* **ASGI-Server**: `uvicorn` – Starte die Anwendung lokal mit `uv run book` (Entry-Point: `src/run.py → main()`).
* **Database**: SQLite (3.x+) für persistente Datenspeicherung.
* **ORM**: Pures SQLAlchemy 2.0 (Nutze zwingend `Mapped` und `mapped_column`).
* **Formatierung & Linting**: `ruff` (`uvx ruff format` und `uvx ruff check`). Aktive Regelsets (siehe `pyproject.toml`):
  * `D` (Pydocstyle) – Docstrings werden erzwungen; ignoriert: `D104`, `D203`, `D212`.
  * `FAST` – FastAPI-spezifische Best-Practices.
  * `PT` – Pytest-spezifische Best-Practices.
  * `B` (Bugbear), `SIM` (Simplify), `UP` (Pyupgrade), `E`/`W`/`F`/`I` (Standard-Lint + isort).
  * **Hinweis**: `target-version = "py312"` in Ruff weicht vom `requires-python = ">=3.14"` ab — nicht ändern, bis Ruff offiziell `py314` unterstützt.
* **Typisierung**: Stark typisiert, geprüft durch Type Hints und `ty` (`uvx ty check src tests`).
* **Logging**: Nutze ausschließlich `loguru` (z.B. `logger.debug("...")`) für Konsolenausgaben. Keine `print()`-Statements!

## 3. Code-Qualität & Dokumentation (Priorität!)
**Dokumentation und sauberer Code sind zentral für dieses Projekt.** Beachte diese Regeln strikt:

1. **Dokumentation**:
   - Jede Funktion und Klasse muss einen aussagekräftigen Docstring in **Englisch** haben.
   - Docstrings folgen dem Format: `"""Short description. Details if needed."""`
   - Komplexe Geschäftslogik muss mit Inline-Kommentaren erklärt werden (sparsam, nur wo nötig). **Alle Kommentare müssen auf Englisch verfasst sein.**

2. **Code-Stil**:
   - Nutze sprechende, **englische** Variablennamen. Beispiel: `book_id` statt `buch_id` oder `b_id`.
   - Maximale Zeilenlänge: 80 Zeichen (per Ruff konfiguriert).
   - Immer Type Hints verwenden, nie `Any` außer in absoluten Ausnahmefällen.
   - Imports alphabetisch sortiert (Ruff erledigt das automatisch).
   - Nutze für das Ressourcen-Management (z.B. bei Dependencies mit `yield`) bevorzugt das `with`-Statement (Context Manager) anstelle von `try...finally`.

3. **Fehlerbehandlung**:
   - Nutze aussagekräftige HTTP-Status-Codes und Error-Messages.
   - Alle DB-Fehler sollten saubere Error-Responses sein (kein Stack Trace zum Client).

4. **SQLAlchemy Entities**:
   - Überschreibe in Entity-Klassen zwingend `__eq__`, `__hash__` und `__repr__`.
   - Stelle sicher, dass diese Methoden nur auf primitive Attribute (wie `id` oder `name`) zugreifen und niemals versehentlich Lazy-Loading-Beziehungen (Relationships) auslösen.

## 4. Verhaltensregeln für den Agenten
1. **Analysiere vor dem Schreiben**: Prüfe immer zuerst die `pyproject.toml` auf aktuelle Abhängigkeiten.
2. **Bottom-Up Entwicklung**: Wenn du neue Features baust, beginne immer bei der Entität, gehe dann zum Repository, dann zum Service und baue den Router zuletzt.
3. **Typisierungen**: Nutze konsequent Type Hints in allen Funktionssignaturen.
4. **Keine zirkulären Imports**: Achte auf saubere Trennung.
5. **Dokumentation vor Code**: Schreibe zuerst Docstrings, dann den Code. Das erzwingt klares Denken.
6. **Erklärungen**: Antworte didaktisch leicht verständlich und aussagekräftig. Erkläre das "Warum" hinter Architektur-Entscheidungen, wenn du Code-Vorschläge machst.
7. **Ruff + Linting**: Nach jeder Änderung immer `uvx ruff format` und `uvx ruff check` laufen lassen.
8. **Async/Sync Konsistenz**: Da wir SQLite nutzen, verwende für den Start standardmäßig synchrone Funktionen (`def` statt `async def`) für die Router, Services und Datenbankabfragen, um Blockaden des Event-Loops zu vermeiden. (Alternativ: Nutze explizit `aiosqlite`, falls Asynchronität explizit gefordert ist).

## 5. Testing-Strategie
1. **Test-Driven / Test-Begleitung**: Zu jedem neuen Router oder Service MÜSSEN Tests in einem separaten `tests/`-Verzeichnis geschrieben werden.
2. **Frameworks**: Nutze `pytest` als Test-Runner.
3. **Integrationstests**: Nutze FastAPIs `TestClient` (basierend auf `httpx`), um die REST-Schnittstellen (`router`) zu testen, ohne den echten Server starten zu müssen.
4. **Ausführung**: Tests müssen so geschrieben sein, dass sie reibungslos über `uv run pytest` durchlaufen.