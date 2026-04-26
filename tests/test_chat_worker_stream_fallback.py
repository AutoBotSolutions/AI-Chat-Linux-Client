"""Tests for ChatWorker stream->nonstream fallback behavior."""

from PyQt6.QtTest import QSignalSpy
from ui.main_window import ChatWorker


class FakeRouterEmptyStreamThenText:
    async def route_request(self, messages, model=None, stream=False, **kwargs):
        if stream:
            if False:
                yield ""  # pragma: no cover
            return
        yield "fallback response"


class FakeRouterNormalStream:
    async def route_request(self, messages, model=None, stream=False, **kwargs):
        if stream:
            yield "hello"
            yield " world"
            return
        yield "should-not-be-used"


def test_chat_worker_falls_back_to_nonstream_when_stream_empty(qtbot):
    worker = ChatWorker(
        router=FakeRouterEmptyStreamThenText(),
        messages=[{"role": "user", "content": "test"}],
        model="ollama/some-model",
        stream=True,
    )

    spy_response = QSignalSpy(worker.response_received)

    with qtbot.waitSignal(worker.finished, timeout=5000):
        worker.start()

    assert len(spy_response) == 1
    assert spy_response[0][0] == "fallback response"


def test_chat_worker_keeps_stream_response_when_present(qtbot):
    worker = ChatWorker(
        router=FakeRouterNormalStream(),
        messages=[{"role": "user", "content": "test"}],
        model="ollama/some-model",
        stream=True,
    )

    spy_response = QSignalSpy(worker.response_received)

    with qtbot.waitSignal(worker.finished, timeout=5000):
        worker.start()

    assert len(spy_response) == 1
    assert spy_response[0][0] == "hello world"
