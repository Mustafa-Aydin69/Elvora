"""
main.py — Application entry point.
Initialises Pygame, starts the CAN thread, runs the main render loop.
"""

import sys
import threading
import logging
import pygame

from can_handler import CANHandler, DEFAULT_STORE
from logic import LogicProcessor
from ui import DashboardUI, W, H, FPS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("main")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class Application:

    def __init__(self):
        # Shared state
        self._data_store = dict(DEFAULT_STORE)
        self._lock = threading.Lock()

        # Subsystems
        self._can = CANHandler(self._data_store, self._lock)
        self._logic = LogicProcessor(self._data_store, self._lock)

        # Pygame
        pygame.init()
        pygame.display.set_caption("EV Dashboard")

        # Try true fullscreen; fall back to windowed on dev machines
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        try:
            self._screen = pygame.display.set_mode((W, H), flags)
            # self._screen = pygame.display.set_mode((W, H), flags | pygame.FULLSCREEN)
        except Exception:
            self._screen = pygame.display.set_mode((W, H), flags)

        pygame.mouse.set_visible(False)
        self._clock = pygame.time.Clock()
        self._ui = DashboardUI(self._screen)
        self._running = False

    def run(self) -> None:
        self._can.start()
        self._running = True
        logger.info("Main loop starting at %d FPS", FPS)

        try:
            while self._running:
                self._handle_events()
                vehicle_state = self._logic.update(self._can.is_alive)
                self._ui.render(vehicle_state, self._clock.get_fps())
                pygame.display.flip()
                self._clock.tick(FPS)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt — shutting down")
        finally:
            self._shutdown()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self._running = False

    def _shutdown(self) -> None:
        logger.info("Stopping CAN thread …")
        self._can.stop()
        pygame.quit()
        logger.info("Goodbye.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    app = Application()
    app.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
