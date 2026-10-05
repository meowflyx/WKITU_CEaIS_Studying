import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier

from task2 import (
    CachedStore,
    FileStore,
    MemoryStore,
    SQLiteStore,
    ValidatedCache,
)


class ContractTests(unittest.TestCase):
    factory = staticmethod(lambda path: memory_fixture(path))

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.store, self.other = self.factory(Path(self.folder.name))

    def test_missing(self):
        self.assertIsNone(self.store.get("missing"))
        self.assertFalse(self.store.delete("missing"))
        self.assertFalse(self.store.replace("missing", 1, "new"))
        self.assertEqual(set(self.store.keys()), set())

    def test_save(self):
        version = self.store.save("note", "hello")
        self.assertGreater(version, 0)
        self.assertEqual(self.store.get("note"), ("hello", version))

    def test_overwrite(self):
        first = self.store.save("note", "first")
        second = self.store.save("note", "second")
        self.assertGreater(second, first)
        self.assertEqual(self.store.get("note"), ("second", second))

    def test_same_value_new_version(self):
        first = self.store.save("note", "same")
        self.assertGreater(self.store.save("note", "same"), first)

    def test_empty_value(self):
        version = self.store.save("empty", "")
        self.assertEqual(self.store.get("empty"), ("", version))

    def test_unicode_value(self):
        version = self.store.save("note", "Привет\nвторая строка: ё")
        self.assertEqual(
            self.store.get("note").value, "Привет\nвторая строка: ё"
        )
        self.assertEqual(self.store.get("note").version, version)

    def test_delete(self):
        self.store.save("note", "hello")
        self.assertTrue(self.store.delete("note"))
        self.assertIsNone(self.store.get("note"))
        self.assertFalse(self.store.delete("note"))

    def test_prefix_without_order(self):
        for key in ("ab2", "z", "ab1", "a", "AB", "a_b", "ax"):
            self.store.save(key, key)
        keys = self.store.keys("ab")
        self.assertEqual(set(keys), {"ab1", "ab2"})
        self.assertEqual(len(keys), 2)
        self.assertEqual(set(self.store.keys("a_")), {"a_b"})
        self.assertEqual(set(self.store.keys("AB")), {"AB"})
        self.assertEqual(len(self.store.keys("")), 7)

    def test_invalid_keys(self):
        for key in (
            "", "../x", "a/b", "a\\b", "a b", "CON", "con.txt", "a.",
            "имя", "a" * 65, None, 1,
        ):
            with self.subTest(key=key):
                for action in (
                    lambda: self.store.save(key, "x"),
                    lambda: self.store.get(key),
                    lambda: self.store.delete(key),
                    lambda: self.store.replace(key, 1, "x"),
                ):
                    with self.assertRaises(ValueError):
                        action()
        self.assertEqual(self.store.keys(), [])

    def test_invalid_prefix(self):
        for prefix in ("a/", "%", "имя", "a" * 65, None, 1):
            with self.subTest(prefix=prefix):
                with self.assertRaises(ValueError):
                    self.store.keys(prefix)

    def test_key_limits(self):
        for key in ("a", "a" * 64, "a_b-9.txt"):
            version = self.store.save(key, "ok")
            self.assertEqual(self.store.get(key), ("ok", version))

    def test_replace_success(self):
        version = self.store.save("note", "old")
        self.assertTrue(self.store.replace("note", version, "new"))
        current = self.store.get("note")
        self.assertEqual(current.value, "new")
        self.assertGreater(current.version, version)

    def test_replace_conflict(self):
        version = self.store.save("note", "old")
        latest = self.store.save("note", "changed")
        self.assertFalse(self.store.replace("note", version, "lost"))
        self.assertEqual(self.store.get("note"), ("changed", latest))

    def test_invalid_version(self):
        for version in (0, -1, True, "1", 2**63):
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    self.store.replace("note", version, "new")

    def test_recreate_no_old_version(self):
        version = self.store.save("note", "old")
        self.store.delete("note")
        latest = self.store.save("note", "new")
        self.assertGreater(latest, version)
        self.assertFalse(self.store.replace("note", version, "lost"))

    def test_external_save(self):
        self.store.save("note", "old")
        self.store.get("note")
        version = self.other.save("note", "external")
        self.assertEqual(self.store.get("note"), ("external", version))

    def test_external_delete(self):
        self.store.save("note", "old")
        self.store.get("note")
        self.other.delete("note")
        self.assertIsNone(self.store.get("note"))

    def test_external_create_after_miss(self):
        self.assertIsNone(self.store.get("note"))
        version = self.other.save("note", "created")
        self.assertEqual(self.store.get("note"), ("created", version))

    def test_external_replace(self):
        version = self.store.save("note", "old")
        self.store.get("note")
        self.assertTrue(self.other.replace("note", version, "external"))
        self.assertEqual(self.store.get("note"), self.other.get("note"))

    def test_external_recreate(self):
        first = self.store.save("note", "old")
        self.store.get("note")
        self.other.delete("note")
        latest = self.other.save("note", "new")
        self.assertGreater(latest, first)
        self.assertEqual(self.store.get("note"), ("new", latest))

    def test_invalid_values(self):
        version = self.store.save("note", "unchanged")
        for value in (None, 1, b"bytes", []):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.store.save("note", value)
                with self.assertRaises(TypeError):
                    self.store.replace("note", version, value)
        self.assertEqual(self.store.get("note"), ("unchanged", version))

    def test_document_snapshot(self):
        version = self.store.save("note", "old")
        snapshot = self.store.get("note")
        self.store.save("note", "new")
        self.assertEqual(snapshot, ("old", version))
        with self.assertRaises(AttributeError):
            snapshot.value = "changed"

    def test_keys_snapshot(self):
        self.store.save("note", "old")
        keys = self.store.keys()
        keys.clear()
        self.assertEqual(set(self.store.keys()), {"note"})

    def test_concurrent_replace(self):
        version = self.store.save("note", "old")
        barrier = Barrier(2)

        def change(client_value):
            client, value = client_value
            barrier.wait(timeout=5)
            return client.replace("note", version, value)

        # оба потока используют одну исходную версию
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(change, (
                (self.store, "left"), (self.other, "right")
            )))
        self.assertEqual(sorted(results), [False, True])
        current = self.store.get("note")
        self.assertIn(current.value, ("left", "right"))
        self.assertGreater(current.version, version)


def memory_fixture(path):
    store = MemoryStore()
    return store, store


def file_fixture(path):
    store = FileStore(path / "documents.json")
    return store, store


def sqlite_fixture(path):
    store = SQLiteStore(path / "documents.db")
    return store, store


def cache_fixture(path, cache_type):
    store = MemoryStore()
    return cache_type(store), store


def run_tests(broken=False, all_backends=False):
    factories = {
        "Memory": memory_fixture,
        "File": file_fixture,
        "SQLite": sqlite_fixture,
        "Cache": lambda path: cache_fixture(
            path, CachedStore if broken else ValidatedCache
        ),
    }
    if all_backends:
        for name, backing_factory in (("CacheFile", file_fixture),
                                      ("CacheSQLite", sqlite_fixture)):
            def factory(path, backing_factory=backing_factory):
                store, other = backing_factory(path)
                return ValidatedCache(store), other
            factories[name] = factory
    success = True
    for name, factory in factories.items():
        print(f"\n{name}", flush=True)
        case = type(name, (ContractTests,), {"factory": staticmethod(factory)})
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
        result = unittest.TextTestRunner(
            stream=sys.stdout, verbosity=2
        ).run(suite)
        success = result.wasSuccessful() and success
    return success


if __name__ == "__main__":
    sys.exit(0 if run_tests(
        "--broken-cache" in sys.argv, "--all-cache-backends" in sys.argv
    ) else 1)
