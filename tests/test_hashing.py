"""Tests for the hashing module."""

from pathlib import Path

from loadout._hashing import hash_bytes, hash_content, hash_directory, hash_file


class TestHashContent:
    def test_deterministic(self):
        assert hash_content("hello") == hash_content("hello")

    def test_different_content(self):
        assert hash_content("hello") != hash_content("world")

    def test_returns_hex_string(self):
        result = hash_content("test")
        assert len(result) == 64  # SHA-256 hex digest
        assert all(c in "0123456789abcdef" for c in result)


class TestHashBytes:
    def test_deterministic(self):
        assert hash_bytes(b"hello") == hash_bytes(b"hello")

    def test_different_data(self):
        assert hash_bytes(b"hello") != hash_bytes(b"world")


class TestHashFile:
    def test_text_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = hash_file(f)
        assert result == hash_content("hello world")

    def test_binary_file(self, tmp_path: Path):
        f = tmp_path / "test.bin"
        data = bytes(range(256))
        f.write_bytes(data)
        result = hash_file(f)
        assert result == hash_bytes(data)


class TestHashDirectory:
    def test_empty_directory(self, tmp_path: Path):
        d = tmp_path / "empty"
        d.mkdir()
        result = hash_directory(d)
        assert len(result) == 64

    def test_deterministic(self, tmp_path: Path):
        d = tmp_path / "dir"
        d.mkdir()
        (d / "a.txt").write_text("aaa")
        (d / "b.txt").write_text("bbb")
        assert hash_directory(d) == hash_directory(d)

    def test_content_change_changes_hash(self, tmp_path: Path):
        d = tmp_path / "dir"
        d.mkdir()
        (d / "a.txt").write_text("aaa")
        h1 = hash_directory(d)
        (d / "a.txt").write_text("bbb")
        h2 = hash_directory(d)
        assert h1 != h2

    def test_new_file_changes_hash(self, tmp_path: Path):
        d = tmp_path / "dir"
        d.mkdir()
        (d / "a.txt").write_text("aaa")
        h1 = hash_directory(d)
        (d / "b.txt").write_text("bbb")
        h2 = hash_directory(d)
        assert h1 != h2

    def test_nested_files(self, tmp_path: Path):
        d = tmp_path / "dir"
        d.mkdir()
        sub = d / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("nested")
        result = hash_directory(d)
        assert len(result) == 64
