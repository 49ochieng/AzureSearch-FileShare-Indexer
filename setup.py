"""
Setup configuration for AzureSearch FileShare Indexer
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # Skip platform-specific markers
            if ';' in line:
                pkg = line.split(';')[0].strip()
            else:
                pkg = line
            requirements.append(pkg)

setup(
    name="azuresearch-fileshare-indexer",
    version="1.0.0",
    author="Edgar McOchieng",
    author_email="edgar@example.com",
    description="Enterprise-grade document indexing for Azure AI Search with vector embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edgarochieng/AzureSearch-FileShare-Indexer",
    packages=find_packages(include=['src', 'src.*', 'config', 'config.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Azure :: AI",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=24.1.1',
            'isort>=5.13.2',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
            'pylint>=3.0.0',
            'bandit>=1.7.6',
            'pre-commit>=3.6.0',
        ],
        'enhanced': [
            'pdfplumber>=0.10.0',
            'Pillow>=10.0.0',
            'markdown>=3.5.1',
            'pytesseract>=0.3.10',
        ],
    },
    entry_points={
        'console_scripts': [
            'azs-index=scripts.index_files:main',
            'azs-index-vector=scripts.index_files_vector:main',
            'azs-create-index=scripts.create_standard_index:main',
            'azs-create-vector-index=scripts.create_vector_index:main',
            'azs-manage-indexes=scripts.manage_indexes:main',
            'azs-search=scripts.search_demo:main',
        ],
    },
    keywords='azure search indexing vector-embeddings semantic-search openai documents',
    project_urls={
        'Bug Reports': 'https://github.com/edgarochieng/AzureSearch-FileShare-Indexer/issues',
        'Source': 'https://github.com/edgarochieng/AzureSearch-FileShare-Indexer',
        'Documentation': 'https://github.com/edgarochieng/AzureSearch-FileShare-Indexer/tree/main/docs',
    },
)
