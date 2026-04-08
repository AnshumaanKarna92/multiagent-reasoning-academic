# Contributing to Multi-Agent Problem-Solving System

We appreciate your interest in contributing to this research project. This document provides guidelines and instructions for participating in the development.

## Code of Conduct

We are committed to maintaining a respectful and inclusive community. All contributors are expected to treat others with professionalism and courtesy in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`

## Development Workflow

Create a feature branch for your work:

```bash
git checkout -b feature/your-feature-name
```

Make your changes and test thoroughly. Commit with clear, descriptive messages:

```bash
git commit -m "Add feature: Clear description of what was added"
```

Push to your fork and submit a pull request with a detailed description of your changes.

## Code Standards

We follow Python PEP 8 conventions with these guidelines:

Type Hints: Include type hints for function parameters and return values:

```python
def analyze(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    pass
```

Docstrings: All functions and classes require docstrings in the NumPy style:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what function does.
    
    Extended description with more context if needed.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
    """
```

Naming Conventions:
* Classes: PascalCase (TeacherAgent)
* Functions and variables: snake_case (run_simulation)
* Constants: UPPER_SNAKE_CASE (MAX_ROUNDS)

Line Length: Keep lines under 100 characters where practical.

## Testing

While formal unit tests are not yet implemented, ensure your code changes:

1. Run without errors: `python main.py`
2. Maintain backward compatibility with existing test problems
3. Handle edge cases gracefully

If you add new functionality, consider including example usage in EXAMPLES.md.

## Documentation

When contributing code:

1. Update README.md if you add user-facing features
2. Update ARCHITECTURE.md for changes to system design
3. Add examples to EXAMPLES.md for usage patterns
4. Include docstrings in all code

## Research Contributions

This project welcomes research contributions such as:

* Novel agent architectures or communication protocols
* Improved prompt engineering
* Evaluation metrics and benchmarking
* Extensions to new problem domains
* Comparative analysis with alternative approaches

Please include empirical results when proposing research changes.

## Reporting Issues

Use GitHub Issues to report bugs or suggest features. Provide:

1. Clear description of the issue
2. Steps to reproduce (for bugs)
3. Expected behavior
4. Actual behavior
5. System information (Python version, OS, etc.)

## Pull Request Process

1. Update documentation as needed
2. Test your changes with the included problem set
3. Write a clear PR description explaining your changes
4. Reference any related issues
5. Ensure code follows project standards

Pull requests require review before merging. Maintainers or community members may suggest changes.

## Areas for Contribution

We particularly welcome help in:

* Agent design improvements and variations
* Prompt engineering optimization
* Documentation and tutorials
* Example implementations
* Performance optimizations
* Support for additional LLM providers
* Visualization tools
* Test suite development
* Problem benchmark expansion

## Questions or Discussions

For questions about contributing, open a GitHub Discussion or issue. We are happy to provide guidance on where you can best help the project.

## Recognition

Contributors will be recognized in project documentation and release notes. All contributions are valued and help advance the research.

## Future Directions

Some areas where we seek contributions:

* Multi-domain evaluation (not just math)
* Distributed agent systems
* Agent memory and learning mechanisms
* Real-time interaction interfaces
* Comparative studies with single-agent systems

We look forward to your contributions building this research forward.
