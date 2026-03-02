# Contributing to Government Knowledge Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:
- Be respectful and professional
- Welcome diverse perspectives
- Focus on constructive feedback
- Report unacceptable behavior responsibly

## Getting Started

### 1. Fork the Repository
```bash
git clone https://github.com/richardogundele/rag_knowledge_assistant.git
cd rag_knowledge_assistant
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest black flake8 mypy  # Development tools
```

### 4. Make Your Changes
- Keep commits focused and atomic
- Write clear, descriptive commit messages
- Follow the code style guidelines below

### 5. Test Your Changes
```bash
pytest tests/
black .
flake8
mypy
```

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## Code Style Guidelines

### Python Code
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for auto-formatting
- Use [type hints](https://docs.python.org/3/library/typing.html) for functions
- Maximum line length: 100 characters

### Example Function
```python
from typing import List, Dict, Optional

def retrieve_documents(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.3
) -> List[Dict[str, str]]:
    """
    Retrieve documents matching the query.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of document chunks with metadata
    """
    # Implementation
    pass
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add support for DOCX files
fix: Correct confidence score calculation
docs: Update API documentation
refactor: Simplify retriever logic
test: Add tests for guardrails
style: Format code with black
chore: Update dependencies
```

## Pull Request Process

1. **Update Documentation**: Update README.md and relevant docs
2. **Add Tests**: Include tests for new features
3. **Write Description**: Clear description of changes and motivation
4. **Link Issues**: Reference related issues with "Closes #123"
5. **Request Review**: Ask maintainers for review

### PR Template
```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Areas for Contribution

### High Priority
- [ ] Document format support (DOCX, Excel, HTML)
- [ ] Performance optimization for large datasets
- [ ] Production deployment guides
- [ ] Test coverage expansion

### Medium Priority
- [ ] Multi-language support
- [ ] Additional LLM integrations
- [ ] UI/UX improvements
- [ ] Analytics dashboard

### Good for First Contributors
- [ ] Documentation improvements
- [ ] Bug fixes
- [ ] Code comments and docstrings
- [ ] Test additions

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_retriever.py

# Run with coverage
pytest --cov=services tests/

# Run with verbose output
pytest -v
```

## Code Review Process

1. Maintainers will review your PR
2. Provide feedback and request changes if needed
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged in release notes

## Documentation Updates

When submitting changes that affect documentation:

1. Update relevant README sections
2. Update docstrings in code
3. Update API documentation if endpoints change
4. Add changelog entry in CHANGELOG.md

## Reporting Bugs

Submit bugs through [GitHub Issues](https://github.com/richardogundele/rag_knowledge_assistant/issues):

**Title**: Brief description of the bug

**Description**:
```
## Bug Description
Clear description of what's not working.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: (Windows/Mac/Linux)
- Python: 3.10/3.11/etc
- Ollama: (installed/version)
- Documents: (number and type)

## Additional Context
Any additional information.
```

## Feature Requests

Submit feature requests through [GitHub Discussions](https://github.com/richardogundele/rag_knowledge_assistant/discussions):

**Title**: Brief feature description

**Description**:
```
## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches considered.

## Additional Context
Any additional information.
```

## Development Tips

### Debugging
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Query: {query}")
logger.info("Documents retrieved")
logger.warning("Low confidence score")
logger.error("Failed to process document")
```

### Performance Testing
```bash
# Profile your code
python -m cProfile -s cumulative main.py

# Memory profiling
pip install memory_profiler
python -m memory_profiler main.py
```

### Vector Store Testing
```python
# Test FAISS operations in isolation
from services.vector_store import FAISSVectorStore

store = FAISSVectorStore()
store.add_embeddings(embeddings)
results = store.search(query_embedding, top_k=5)
```

## Documentation Standards

### Docstrings
```python
def function_name(param1: str, param2: int) -> Dict:
    """
    Brief one-line description.
    
    Longer description if needed. Explain what the function does,
    why it exists, and how to use it.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input provided
        TimeoutError: When document processing exceeds timeout
        
    Example:
        >>> result = function_name("test", 42)
        >>> result['status']
        'success'
    """
    pass
```

## Release Process

1. Update version in `config.py`
2. Update `CHANGELOG.md`
3. Create GitHub release with tag
4. Publish to PyPI (if applicable)
5. Announce in discussions

## Questions?

- 📖 Read the [README](README.md)
- 💬 Start a [Discussion](https://github.com/richardogundele/rag_knowledge_assistant/discussions)
- 🐛 File an [Issue](https://github.com/richardogundele/rag_knowledge_assistant/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Government Knowledge Assistant! 🎉**
