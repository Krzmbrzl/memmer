#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import threading
import unittest

from memmer.utils import DatabaseThread


class TestDatabaseThread(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseThread()

    def tearDown(self):
        self.db.shutdown()

    def test_returns_result(self):
        future = self.db.submit(lambda session: 21 * 2)
        self.assertEqual(future.result(timeout=5), 42)

    def test_captures_exception(self):
        def boom(session):
            raise ValueError("nope")

        future = self.db.submit(boom)
        with self.assertRaises(ValueError):
            future.result(timeout=5)

    def test_runs_on_single_dedicated_thread(self):
        caller_thread = threading.get_ident()

        thread_ids = [
            self.db.submit(lambda session: threading.get_ident()).result(timeout=5)
            for _ in range(20)
        ]

        # Everything ran on one and the same thread ...
        self.assertEqual(len(set(thread_ids)), 1)
        # ... and that thread is not the caller's.
        self.assertNotEqual(thread_ids[0], caller_thread)

    def test_tasks_run_serially_in_submission_order(self):
        order = []
        running = []
        lock = threading.Lock()

        def make_task(i):
            def task(session):
                with lock:
                    running.append(i)
                    # If anything ran concurrently, more than one task would be
                    # "running" at the same time.
                    self.assertEqual(running, [i])
                order.append(i)
                with lock:
                    running.remove(i)

            return task

        futures = [self.db.submit(make_task(i)) for i in range(50)]
        for future in futures:
            future.result(timeout=5)

        self.assertEqual(order, list(range(50)))

    def test_session_argument_is_none_before_establish(self):
        seen = self.db.submit(lambda session: session).result(timeout=5)
        self.assertIsNone(seen)

    def test_establish_adopts_session_for_later_tasks(self):
        sentinel = object()

        self.db.establish(lambda: (sentinel, None)).result(timeout=5)

        seen = self.db.submit(lambda session: session).result(timeout=5)
        self.assertIs(seen, sentinel)


if __name__ == "__main__":
    unittest.main()
