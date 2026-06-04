"""
Tests for SystemCheckWorker — the QThread that runs async system checks
without blocking the UI thread.

These tests verify:
- The worker emits report_ready on success
- The worker emits error_occurred when the checker raises
- The worker's event loop is always closed (finally branch)
- The ChatWindow lifecycle: duplicate-run guard and on_finished cleanup
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QSignalSpy


# ---------------------------------------------------------------------------
# Isolated SystemCheckWorker unit tests
# ---------------------------------------------------------------------------

class TestSystemCheckWorkerSignals:
    """Test the worker in isolation — no ChatWindow needed."""

    def _make_fake_results(self):
        return {
            "system_info": {
                "platform": "Linux",
                "platform_release": "6.x",
                "python_version": "3.13.0",
            },
            "python_checks": {
                "python_version_ok": True,
                "missing_packages": [],
            },
            "network_checks": {"internet_available": True},
            "provider_checks": {},
            "file_system_checks": {
                "config_dir_accessible": True,
                "data_dir_accessible": True,
            },
        }

    def test_report_ready_emitted_on_success(self, qtbot):
        """Worker must emit report_ready with a non-empty string on success."""
        from ui.main_window import SystemCheckWorker

        fake_results = self._make_fake_results()
        fake_checker = MagicMock()
        fake_checker.get_recommendations = MagicMock(return_value=[])

        worker = SystemCheckWorker()
        spy = QSignalSpy(worker.report_ready)

        with patch("ui.main_window.SystemChecker", return_value=fake_checker), \
             patch.object(
                 fake_checker,
                 "check_all_systems",
                 new=AsyncMock(return_value=fake_results),
             ):
            with qtbot.waitSignal(worker.report_ready, timeout=5000):
                worker.start()

        worker.wait()
        assert len(spy) == 1
        report_text = spy[0][0]
        assert isinstance(report_text, str)
        assert len(report_text) > 0
        assert "SYSTEM CHECK REPORT" in report_text

    def test_error_occurred_emitted_on_failure(self, qtbot):
        """Worker must emit error_occurred when the checker raises an exception."""
        from ui.main_window import SystemCheckWorker

        worker = SystemCheckWorker()
        spy = QSignalSpy(worker.error_occurred)

        with patch(
            "ui.main_window.SystemChecker",
            side_effect=RuntimeError("simulated failure"),
        ):
            with qtbot.waitSignal(worker.error_occurred, timeout=5000):
                worker.start()

        worker.wait()
        assert len(spy) == 1
        assert "simulated failure" in spy[0][0]

    def test_finished_emitted_after_success(self, qtbot):
        """The built-in QThread.finished signal must fire after a successful run."""
        from ui.main_window import SystemCheckWorker

        fake_results = self._make_fake_results()
        fake_checker = MagicMock()
        fake_checker.get_recommendations = MagicMock(return_value=[])

        worker = SystemCheckWorker()

        with patch("ui.main_window.SystemChecker", return_value=fake_checker), \
             patch.object(
                 fake_checker,
                 "check_all_systems",
                 new=AsyncMock(return_value=fake_results),
             ):
            with qtbot.waitSignal(worker.finished, timeout=5000):
                worker.start()

        worker.wait()

    def test_finished_emitted_after_error(self, qtbot):
        """QThread.finished must fire even when an error occurs."""
        from ui.main_window import SystemCheckWorker

        worker = SystemCheckWorker()

        with patch(
            "ui.main_window.SystemChecker",
            side_effect=RuntimeError("boom"),
        ):
            with qtbot.waitSignal(worker.finished, timeout=5000):
                worker.start()

        worker.wait()


# ---------------------------------------------------------------------------
# Event-loop hygiene
# ---------------------------------------------------------------------------

class TestEventLoopHygiene:
    """Verify the worker always closes its event loop."""

    def test_event_loop_closed_on_success(self, qtbot):
        from ui.main_window import SystemCheckWorker

        closed_loops = []
        original_new_event_loop = asyncio.new_event_loop

        def tracking_new_event_loop():
            loop = original_new_event_loop()
            original_close = loop.close
            def patched_close():
                closed_loops.append(True)
                original_close()
            loop.close = patched_close
            return loop

        fake_results = {
            "system_info": {"platform": "test", "platform_release": "0", "python_version": "3.13"},
            "python_checks": {"python_version_ok": True, "missing_packages": []},
            "network_checks": {"internet_available": True},
            "provider_checks": {},
            "file_system_checks": {"config_dir_accessible": True, "data_dir_accessible": True},
        }
        fake_checker = MagicMock()
        fake_checker.get_recommendations = MagicMock(return_value=[])

        worker = SystemCheckWorker()

        with patch("asyncio.new_event_loop", side_effect=tracking_new_event_loop), \
             patch("ui.main_window.SystemChecker", return_value=fake_checker), \
             patch.object(
                 fake_checker,
                 "check_all_systems",
                 new=AsyncMock(return_value=fake_results),
             ):
            with qtbot.waitSignal(worker.finished, timeout=5000):
                worker.start()

        worker.wait()
        assert closed_loops, "Event loop was never closed after successful run"

    def test_event_loop_closed_on_error(self, qtbot):
        from ui.main_window import SystemCheckWorker

        closed_loops = []
        original_new_event_loop = asyncio.new_event_loop

        def tracking_new_event_loop():
            loop = original_new_event_loop()
            original_close = loop.close
            def patched_close():
                closed_loops.append(True)
                original_close()
            loop.close = patched_close
            return loop

        worker = SystemCheckWorker()

        with patch("asyncio.new_event_loop", side_effect=tracking_new_event_loop), \
             patch("ui.main_window.SystemChecker", side_effect=RuntimeError("forced")):
            with qtbot.waitSignal(worker.finished, timeout=5000):
                worker.start()

        worker.wait()
        assert closed_loops, "Event loop was not closed after error"


# ---------------------------------------------------------------------------
# ChatWindow integration — duplicate-run guard and cleanup
# ---------------------------------------------------------------------------

class TestChatWindowSystemCheckIntegration:
    def test_duplicate_run_guard(self, chat_window, qtbot):
        """Starting a second system check while one is running must be a no-op."""
        # Inject a fake running worker
        fake_running = MagicMock()
        fake_running.isRunning.return_value = True
        chat_window.system_check_worker = fake_running

        chat_window.run_system_check()

        # The existing fake worker must NOT have been replaced
        assert chat_window.system_check_worker is fake_running

    def test_on_finished_clears_worker(self, chat_window):
        """on_system_check_finished() must set system_check_worker to None."""
        chat_window.system_check_worker = MagicMock()
        chat_window.on_system_check_finished()
        assert chat_window.system_check_worker is None

    def test_on_error_does_not_crash(self, chat_window):
        """on_system_check_error() must log and show a dialog without raising."""
        with patch("ui.main_window.QMessageBox.warning"):
            # Must not raise regardless of message content
            chat_window.on_system_check_error("oops")
