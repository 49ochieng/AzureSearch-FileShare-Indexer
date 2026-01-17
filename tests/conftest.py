"""
Pytest configuration and fixtures

Author: Edgar McOchieng
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file"""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("This is a sample text document for testing.")
    return file_path


@pytest.fixture
def sample_files(temp_dir):
    """Create multiple sample files"""
    files = []
    for i in range(5):
        file_path = os.path.join(temp_dir, f"file{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Sample content {i}")
        files.append(file_path)
    return files


@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration for tests"""
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://test.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_KEY", "test-key")
    monkeypatch.setenv("AZURE_SEARCH_INDEX_NAME", "test-index")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_KEY", "test-key")
    monkeypatch.setenv("FILE_SHARE_PATH", "/test/path")