"""Test-runtime compatibility configuration."""

import asyncio
import sys

if sys.platform == "win32":
    # Starlette TestClient uses a background event loop. The Proactor policy
    # hangs in this Windows/PTY environment even for trivial coroutines.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
