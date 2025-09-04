# Document Knowledge Converter (DKC)

A beginner-friendly, offline agent that converts a folder of PDFs/TXTs into structured knowledge cards and chunks. Perfect for researchers, students, and developers who want to extract and organize information from documents without relying on external APIs or cloud services.

## 🚀 Quick Start

### 1. Get the Code

```bash
# Clone the repository
git clone https://github.com/Jori-Health/OpenCompute.git
cd firstAgent

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Run Your First Example

```bash
# Process the included sample documents
python -m dkc.cli build --in data/sample_docs --out output

# Inspect a single document
python -m dkc.cli inspect --file data/sample_docs/quickstart1.txt
```

### 3. Check Your Results

```bash
# View the generated files
ls output/
# You should see: cards.jsonl, chunks.jsonl, manifest.json

# Look at a knowledge card
head -1 output/cards.jsonl | python -m json.tool
```

## 📋 What This Project Does

DKC transforms unstructured documents into structured knowledge that's easy to search, analyze, and work with programmatically. Think of it as a smart document processor that:

- **Extracts key information** from PDFs and text files
- **Creates searchable chunks** with overlapping windows
- **Generates knowledge cards** with facts, entities, and citations
- **Maintains full provenance** - you can always trace back to the source
- **Works completely offline** - no internet required

## 🏗️ Project Structure

```
firstAgent/
├── src/dkc/                    # Main source code
│   ├── __init__.py
│   ├── schema.py              # Data models (KnowledgeCard, Chunk, Citation)
│   ├── utils.py               # Utility functions (hashing, file I/O)
│   ├── loader.py              # Document loading (PDF/TXT)
│   ├── chunker.py             # Text chunking with overlap
│   ├── cards.py               # Knowledge card generation
│   ├── writer.py              # Output file writing
│   ├── cli.py                 # Command-line interface
│   └── eval.py                # Evaluation metrics
├── tests/                     # Test suite
│   └── test_smoke.py          # End-to-end smoke test
├── data/sample_docs/          # Sample documents for testing
│   ├── quickstart1.txt        # Python programming guide
│   ├── quickstart2.txt        # Machine learning overview
│   ├── sample1.txt            # Machine learning concepts
│   └── sample2.txt            # Python best practices
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🎯 Core Concepts

### Knowledge Cards
Each document becomes a knowledge card containing:
- **Facts**: Key information extracted from the document (≤5 facts)
- **Acronyms**: Technical terms like "API", "ML", "CPU"
- **Entities**: Named entities like "Python", "Google", "Machine Learning"
- **Citations**: References back to the source document

### Chunks
Long documents are split into overlapping chunks for better processing:
- **Size**: Default 800 words per chunk
- **Overlap**: 120 words between chunks (configurable)
- **Stable IDs**: Deterministic chunk IDs for reproducibility

### Manifest
A summary file containing:
- **Counts**: Total documents, cards, and chunks processed
- **Skipped files**: Any files that couldn't be processed
- **Metadata**: Processing timestamp and file information

## 📚 Tutorial: Processing Your Own Documents

### Step 1: Prepare Your Documents

Create a folder with your documents:

```bash
mkdir my_documents
# Add your PDF and TXT files here
cp /path/to/your/document.pdf my_documents/
cp /path/to/your/notes.txt my_documents/
```

### Step 2: Process the Documents

```bash
# Basic processing
python -m dkc.cli build --in my_documents --out results

# Custom chunk size (for longer documents)
python -m dkc.cli build --in my_documents --out results --chunk 1000 --overlap 150
```

### Step 3: Explore the Results

```bash
# Count your results
echo "Cards: $(wc -l < results/cards.jsonl)"
echo "Chunks: $(wc -l < results/chunks.jsonl)"

# View a knowledge card
python -c "
import json
with open('results/cards.jsonl', 'r') as f:
    card = json.loads(f.readline())
    print(f'Title: {card[\"title\"]}')
    print(f'Facts: {len(card[\"facts\"])} facts')
    print(f'Acronyms: {card[\"acronyms\"]}')
    print(f'Entities: {card[\"entities\"][:5]}...')  # First 5 entities
"

# View a chunk
python -c "
import json
with open('results/chunks.jsonl', 'r') as f:
    chunk = json.loads(f.readline())
    print(f'Chunk {chunk[\"ordinal\"]}: {chunk[\"text\"][:100]}...')
"
```

### Step 4: Evaluate Quality

```bash
# Check completeness and citation coverage
python -c "
from dkc.eval import eval_cards
result = eval_cards('results/cards.jsonl')
print(f'Completeness: {result[\"completeness\"]:.1%}')
print(f'Citation Coverage: {result[\"citation_coverage\"]:.1%}')
"
```

## 🔧 Advanced Usage

### Custom Chunking

```bash
# Smaller chunks for detailed analysis
python -m dkc.cli build --in documents --out results --chunk 400 --overlap 60

# Larger chunks for broader context
python -m dkc.cli build --in documents --out results --chunk 1200 --overlap 200
```

### Inspecting Individual Documents

```bash
# Inspect a PDF
python -m dkc.cli inspect --file document.pdf

# Inspect a text file
python -m dkc.cli inspect --file notes.txt
```

### Processing Large Document Collections

```bash
# Process a large folder (DKC handles errors gracefully)
python -m dkc.cli build --in /path/to/large/collection --out results

# Check what was skipped
python -c "
import json
with open('results/manifest.json', 'r') as f:
    manifest = json.load(f)
    print(f'Processed: {manifest[\"total_documents\"]} documents')
    print(f'Skipped: {len(manifest[\"skipped_files\"])} files')
    if manifest['skipped_files']:
        print('Skipped files:', manifest['skipped_files'])
"
```

## 🧪 Development & Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_smoke.py -v
```

### Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest

# Run linting (if configured)
# flake8 src/
# mypy src/
```

## 📊 Output Format Details

### Knowledge Cards (`cards.jsonl`)
```json
{
  "id": "unique-document-id",
  "title": "Document Title",
  "date": "2024-01-15",
  "source_path": "/path/to/source/file.pdf",
  "facts": [
    "Key fact 1 from the document",
    "Key fact 2 from the document"
  ],
  "acronyms": ["API", "ML", "CPU"],
  "entities": ["Python", "Google", "Machine Learning"],
  "citations": [
    {
      "doc_id": "unique-document-id",
      "source_path": "/path/to/source/file.pdf",
      "text_excerpt": "Excerpt from the document...",
      "page": 1,
      "line": 10
    }
  ]
}
```

### Chunks (`chunks.jsonl`)
```json
{
  "id": "unique-chunk-id",
  "doc_id": "unique-document-id",
  "ordinal": 1,
  "text": "This is the actual text content of the chunk...",
  "source_path": "/path/to/source/file.pdf",
  "page": 1,
  "line_start": 1,
  "line_end": 50
}
```

### Manifest (`manifest.json`)
```json
{
  "total_documents": 10,
  "total_cards": 10,
  "total_chunks": 25,
  "skipped_files": ["corrupted.pdf"],
  "created_at": "2024-01-15T10:30:00"
}
```

## 🛠️ Requirements

- **Python 3.11+**
- **Dependencies**:
  - `click>=8.1` - Command-line interface
  - `loguru>=0.7` - Logging
  - `pydantic>=2.6` - Data validation
  - `pypdf>=4.2` - PDF processing
  - `pytest>=8.0` - Testing

## 🎨 Design Principles

- **Offline First**: No external dependencies or network calls
- **Deterministic**: Same input always produces same output
- **Pure Functions**: Minimal side effects for better testing
- **Beginner Friendly**: Clear code and comprehensive documentation
- **Fast & Lightweight**: Optimized for speed and minimal resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Troubleshooting

### Common Issues

**"No module named 'dkc'"**
```bash
# Make sure you're in the project directory and have activated the virtual environment
source venv/bin/activate
pip install -e .
```

**"Permission denied" errors**
```bash
# Make sure output directory is writable
chmod 755 output/
```

**PDF files not processing**
```bash
# Check if the PDF is corrupted or password-protected
python -m dkc.cli inspect --file problematic.pdf
```

**Empty output files**
```bash
# Check the manifest for skipped files
cat results/manifest.json | python -m json.tool
```

### Getting Help

- Check the [Issues](link-to-issues) page for known problems
- Create a new issue with:
  - Your Python version
  - Operating system
  - Error message
  - Steps to reproduce

## 🎉 Success Stories

*"DKC helped me process 500 research papers into searchable knowledge cards. The offline processing was crucial for my privacy requirements."* - Research Student

*"Perfect for my documentation project. The overlapping chunks ensure I don't lose context between sections."* - Technical Writer

---

**Ready to get started?** Jump to the [Quick Start](#-quick-start) section above!
