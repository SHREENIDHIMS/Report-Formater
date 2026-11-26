"""Run one rendering job inside the isolated worker container."""

import json
import shutil
import sys
from pathlib import Path

from app.rendering import convert_docx_to_pdf


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: entrypoint.py INPUT.docx RESULT_DIR", file=sys.stderr)
        return 2
    result_dir = Path(sys.argv[2])
    try:
        result = convert_docx_to_pdf(sys.argv[1], temp_dir=str(result_dir))
        print(json.dumps(result.model_dump(mode="json")))
        return 0 if result.status.value == "succeeded" else 1
    finally:
        # The PDF is the retained job artifact. Remove the copied source and
        # LibreOffice profile so the writable mount contains no intermediates.
        (result_dir / "input.docx").unlink(missing_ok=True)
        shutil.rmtree(result_dir / "lo-profile", ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
