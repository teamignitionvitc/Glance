<div align="center">

<img src="docs/public/Glance.png" alt="Glance Logo" width="300"/>

# Contributing to Glance

<p><strong>Professional Real-Time Telemetry Visualization Platform</strong></p>

<p><em>Thank you for your interest in contributing to Glance!</em></p>

<p>
  <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat" alt="Contributions Welcome"/>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" alt="PRs Welcome"/>
</p>

<hr/>
<img src="docs/public/ign_logo_wht.png" alt="Team Ignition Logo" width="150"/>
<p><strong>Developed by Team Ignition Software Department</strong><br/>
<em>Vellore Institute of Technology, Chennai</em></p>

</div>

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)
- [Recognition](#recognition)

---

## Code of Conduct

<table>
<tr>
<td width="60%">

By participating in this project, you agree to maintain a welcoming, inclusive, and respectful environment for all contributors.

**Our Pledge**

We are committed to providing a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

</td>
<td width="40%">

**Expected Behavior**

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

**Unacceptable Behavior**

- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Unethical or unprofessional conduct

</td>
</tr>
</table>

**Enforcement**

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the Team Ignition Software Department through our [website](https://teamignition.space). All complaints will be reviewed and investigated.

---

## How Can I Contribute?

<table>
<tr>
<td width="33%">

### Reporting Bugs

Found a bug? Help us fix it!

- Use GitHub Issues
- Search existing issues first
- Include detailed information
- Provide reproduction steps
- Attach screenshots/logs

[Report a Bug →](https://github.com/teamignitionvitc/Glance/issues/new?template=bug_report.md)

</td>
<td width="33%">

### Suggesting Features

Have an idea for improvement?

- Open a feature request
- Describe the use case
- Explain expected behavior
- Consider implementation
- Discuss in issues first

[Request Feature →](https://github.com/teamignitionvitc/Glance/issues/new?template=feature_request.md)

</td>
<td width="34%">

### Writing Code

Ready to contribute code?

- Fix bugs
- Add new features
- Improve performance
- Refactor existing code
- Add tests

[Start Contributing →](#getting-started)

</td>
</tr>
<tr>
<td colspan="3">

### Other Ways to Help

<table>
<tr>
<th>Contribution Type</th>
<th>How to Help</th>
<th>Skills Needed</th>
</tr>
<tr>
<td><strong>Documentation</strong></td>
<td>Improve README, add tutorials, fix typos</td>
<td>Technical writing</td>
</tr>
<tr>
<td><strong>Testing</strong></td>
<td>Test on different platforms, report issues</td>
<td>QA mindset</td>
</tr>
<tr>
<td><strong>Design</strong></td>
<td>Improve UI/UX, create icons, mockups</td>
<td>UI/UX design</td>
</tr>
<tr>
<td><strong>Translation</strong></td>
<td>Translate documentation and UI</td>
<td>Multilingual skills</td>
</tr>
<tr>
<td><strong>Community</strong></td>
<td>Answer questions, help newcomers</td>
<td>Communication</td>
</tr>
</table>

</td>
</tr>
</table>

---

## Getting Started

### Prerequisites

<table>
<tr>
<th width="30%">Requirement</th>
<th width="70%">Details</th>
</tr>
<tr>
<td><strong>Python</strong></td>
<td>3.8 or higher (3.10+ recommended)</td>
</tr>
<tr>
<td><strong>Git</strong></td>
<td>For version control and collaboration</td>
</tr>
<tr>
<td><strong>GitHub Account</strong></td>
<td>Required to submit pull requests</td>
</tr>
<tr>
<td><strong>Code Editor</strong></td>
<td>VS Code, PyCharm, or similar (with Python support)</td>
</tr>
<tr>
<td><strong>Virtual Environment</strong></td>
<td>Recommended for dependency isolation</td>
</tr>
</table>

### Development Setup

<details open>
<summary><h4>Step 1: Fork the Repository</h4></summary>

1. Visit the [Glance repository](https://github.com/teamignitionvitc/Glance)
2. Click the "Fork" button in the top-right corner
3. Select your GitHub account as the destination

</details>

<details open>
<summary><h4>Step 2: Clone Your Fork</h4></summary>

```bash
# Clone your forked repository
git clone https://github.com/YOUR_USERNAME/Glance.git

# Navigate to the project directory
cd Glance

# Add upstream remote (original repository)
git remote add upstream https://github.com/teamignitionvitc/Glance.git

# Verify remotes
git remote -v
```

**Expected output:**
```
origin    https://github.com/YOUR_USERNAME/Glance.git (fetch)
origin    https://github.com/YOUR_USERNAME/Glance.git (push)
upstream  https://github.com/teamignitionvitc/Glance.git (fetch)
upstream  https://github.com/teamignitionvitc/Glance.git (push)
```

</details>

<details open>
<summary><h4>Step 3: Set Up Development Environment</h4></summary>

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies (recommended)
pip install PySide6-WebEngine

# Install development dependencies (if you're adding tests)
pip install pytest pytest-qt pytest-cov
```

</details>

<details open>
<summary><h4>Step 4: Verify Installation</h4></summary>

```bash
# Run the application
python main.py

# Expected: Application launches successfully
```

If you encounter issues, check the [Troubleshooting](#troubleshooting) section.

</details>

---

## Development Workflow

### Creating a Feature Branch

<table>
<tr>
<td width="50%">

**Branch Naming Convention**

<table>
<tr><th>Type</th><th>Format</th><th>Example</th></tr>
<tr><td>Feature</td><td><code>feature/description</code></td><td><code>feature/kalman-filter</code></td></tr>
<tr><td>Bug Fix</td><td><code>fix/description</code></td><td><code>fix/serial-connection</code></td></tr>
<tr><td>Documentation</td><td><code>docs/description</code></td><td><code>docs/api-reference</code></td></tr>
<tr><td>Refactor</td><td><code>refactor/description</code></td><td><code>refactor/widget-system</code></td></tr>
<tr><td>Test</td><td><code>test/description</code></td><td><code>test/filter-manager</code></td></tr>
</table>

</td>
<td width="50%">

**Create and Switch to Branch**

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Verify you're on the correct branch
git branch
```

**Expected output:**
```
  main
* feature/your-feature-name
```

</td>
</tr>
</table>

### Making Changes

<table>
<tr>
<td width="50%">

**Best Practices**

- Make small, focused commits
- Test changes thoroughly
- Follow coding standards
- Update documentation
- Add tests for new features
- Keep commits atomic

</td>
<td width="50%">

**Development Cycle**

1. Write code
2. Test manually
3. Run automated tests (if available)
4. Update documentation
5. Commit changes
6. Push to your fork
7. Create pull request

</td>
</tr>
</table>

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your local main
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main

# Rebase your feature branch (if needed)
git checkout feature/your-feature-name
git rebase main
```

---

## Coding Standards

<div align="center">
<h3>We follow PEP 8 with some project-specific conventions</h3>
</div>

### Python Style Guide

<table>
<tr>
<td width="50%">

**General Rules**

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 120 characters
- **Encoding**: UTF-8
- **Imports**: Grouped and sorted
  1. Standard library
  2. Third-party packages
  3. Local modules
- **Naming**:
  - `snake_case` for functions, variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

</td>
<td width="50%">

**Example**

```python
"""Module docstring."""

import sys
import time
from typing import List, Optional

from PySide6.QtWidgets import QWidget
import numpy as np

from app.widgets import ValueCard


class CustomWidget(QWidget):
    """Class docstring.
    
    Args:
        param_config: Parameter configuration dict
    """
    
    MAX_BUFFER_SIZE = 1000  # Constant
    
    def __init__(self, param_config: dict):
        """Initialize widget."""
        super().__init__()
        self.param_config = param_config
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize user interface."""
        # Implementation
        pass
```

</td>
</tr>
</table>

### Code Quality Checklist

<table>
<tr>
<th width="30%">Category</th>
<th width="70%">Requirements</th>
</tr>
<tr>
<td><strong>Documentation</strong></td>
<td>
- Module docstrings<br/>
- Class docstrings<br/>
- Function/method docstrings<br/>
- Complex logic comments<br/>
- Type hints for parameters and returns
</td>
</tr>
<tr>
<td><strong>Error Handling</strong></td>
<td>
- Try-except blocks for risky operations<br/>
- Specific exception types<br/>
- Proper error messages<br/>
- Resource cleanup (files, connections)<br/>
- Logging for debugging
</td>
</tr>
<tr>
<td><strong>Performance</strong></td>
<td>
- Efficient algorithms<br/>
- Avoid unnecessary loops<br/>
- Use generators for large datasets<br/>
- Profile critical sections<br/>
- Minimize memory usage
</td>
</tr>
<tr>
<td><strong>Security</strong></td>
<td>
- Validate user inputs<br/>
- Sanitize file paths<br/>
- Check array bounds<br/>
- Handle null/None values<br/>
- Avoid injection vulnerabilities
</td>
</tr>
</table>

### Type Hints

**Required for:**
- Public function parameters
- Public function return types
- Class attributes (when not obvious)

**Example:**

```python
from typing import List, Dict, Optional, Tuple

def process_data(
    data: List[float], 
    threshold: float, 
    config: Optional[Dict[str, any]] = None
) -> Tuple[List[float], int]:
    """Process data with threshold filtering.
    
    Args:
        data: Input data values
        threshold: Filtering threshold
        config: Optional configuration dictionary
        
    Returns:
        Tuple of (filtered_data, filtered_count)
    """
    filtered = [x for x in data if x > threshold]
    return filtered, len(filtered)
```

### Docstring Format

**Google Style (Preferred):**

```python
def calculate_average(values: List[float], window_size: int = 5) -> float:
    """Calculate moving average of values.
    
    This function computes a simple moving average over the specified
    window size. If fewer values than window_size are available, it
    uses all available values.
    
    Args:
        values: List of numeric values to average
        window_size: Number of values to include in average (default: 5)
        
    Returns:
        The calculated average as a float
        
    Raises:
        ValueError: If values list is empty
        TypeError: If values contains non-numeric types
        
    Examples:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
        >>> calculate_average([1, 2, 3], window_size=2)
        2.5
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    window = values[-window_size:]
    return sum(window) / len(window)
```

---

## Testing Guidelines

### Manual Testing

<table>
<tr>
<td width="50%">

**Before Submitting PR**

Test your changes with:

1. **Dummy Data Mode**
   - Verify basic functionality
   - Check all widgets update
   - Test configuration changes

2. **Multiple Platforms**
   - Windows
   - Linux (if possible)
   - macOS (if possible)

3. **Edge Cases**
   - Empty data
   - Invalid inputs
   - Extreme values
   - Connection failures

</td>
<td width="50%">

**Testing Checklist**

- [ ] Application launches successfully
- [ ] No console errors or warnings
- [ ] All menu items functional
- [ ] Widgets display correctly
- [ ] Data updates in real-time
- [ ] Filters work as expected
- [ ] Data logging functions
- [ ] Project save/load works
- [ ] No memory leaks (long runs)
- [ ] Responsive UI (no freezing)

</td>
</tr>
</table>

### Automated Testing (Future)

We're working on adding automated tests. If you'd like to contribute test infrastructure:

```python
# Example test structure (pytest)
import pytest
from app.filters import MovingAverageFilter

def test_moving_average_basic():
    """Test basic moving average calculation."""
    filter_obj = MovingAverageFilter("test_filter", window_size=3)
    
    # Test data
    assert filter_obj.apply(1.0) == 1.0  # First value
    assert filter_obj.apply(2.0) == 1.5  # Average of [1, 2]
    assert filter_obj.apply(3.0) == 2.0  # Average of [1, 2, 3]
    assert filter_obj.apply(4.0) == 3.0  # Average of [2, 3, 4]

def test_moving_average_reset():
    """Test filter reset functionality."""
    filter_obj = MovingAverageFilter("test_filter", window_size=3)
    
    filter_obj.apply(1.0)
    filter_obj.apply(2.0)
    filter_obj.reset()
    
    assert filter_obj.apply(5.0) == 5.0  # Should start fresh
```

---

## Documentation Standards

### README Updates

When adding features, update:

<table>
<tr>
<th>Section</th>
<th>Update Needed</th>
</tr>
<tr>
<td><strong>Features</strong></td>
<td>Add new feature to relevant section</td>
</tr>
<tr>
<td><strong>Screenshots</strong></td>
<td>Update if UI changed significantly</td>
</tr>
<tr>
<td><strong>User Guide</strong></td>
<td>Add usage instructions</td>
</tr>
<tr>
<td><strong>Configuration</strong></td>
<td>Document new settings</td>
</tr>
<tr>
<td><strong>Troubleshooting</strong></td>
<td>Add common issues and solutions</td>
</tr>
<tr>
<td><strong>Version History</strong></td>
<td>List in next version's changes</td>
</tr>
</table>

### Code Comments

**Good Comments:**

```python
# Calculate Kalman gain using covariance matrices
kalman_gain = predicted_error / (predicted_error + measurement_variance)

# Apply exponential smoothing with user-configured alpha
filtered_value = self.alpha * raw_value + (1 - self.alpha) * self.last_value

# Prevent division by zero in edge case where window is empty
if len(self.buffer) == 0:
    return None
```

**Bad Comments:**

```python
# Increment i
i += 1

# Set value
self.value = 5

# Call function
result = process_data(data)
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

<table>
<tr><th>Type</th><th>Description</th><th>Example</th></tr>
<tr><td><code>feat</code></td><td>New feature</td><td><code>feat(filters): add median filter implementation</code></td></tr>
<tr><td><code>fix</code></td><td>Bug fix</td><td><code>fix(serial): resolve port detection on Linux</code></td></tr>
<tr><td><code>docs</code></td><td>Documentation</td><td><code>docs(readme): update installation instructions</code></td></tr>
<tr><td><code>style</code></td><td>Code style</td><td><code>style(widgets): format according to PEP 8</code></td></tr>
<tr><td><code>refactor</code></td><td>Code refactoring</td><td><code>refactor(backend): simplify data parsing logic</code></td></tr>
<tr><td><code>test</code></td><td>Add tests</td><td><code>test(filters): add unit tests for Kalman filter</code></td></tr>
<tr><td><code>chore</code></td><td>Maintenance</td><td><code>chore(deps): update PySide6 to 6.5.0</code></td></tr>
</table>

**Examples:**

```bash
# Good commit messages
git commit -m "feat(widgets): add LED indicator widget with color states"
git commit -m "fix(logging): prevent buffer overflow in high-rate scenarios"
git commit -m "docs(filters): add Kalman filter tuning guide"

# Bad commit messages
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Detailed Commit Example:**

```
feat(filters): implement Kalman filter for signal processing

Add Kalman filter implementation with configurable process and
measurement variance parameters. Includes:

- KalmanFilter class with optimal estimation algorithm
- Filter state reset functionality
- Serialization to/from JSON
- Integration with FilterManager

Closes #42
```

---

## Pull Request Process

### Before Submitting

<table>
<tr>
<td width="50%">

**Code Checklist**

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests (if applicable)
- [ ] Documentation updated
- [ ] No merge conflicts with main
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

</td>
<td width="50%">

**Review Checklist**

- [ ] Self-review completed
- [ ] Code is commented where needed
- [ ] No debug/console.log statements
- [ ] No unnecessary files included
- [ ] Screenshots added (for UI changes)
- [ ] Performance implications considered

</td>
</tr>
</table>

### Creating a Pull Request

<details open>
<summary><h4>Step 1: Push Your Changes</h4></summary>

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat(scope): description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

</details>

<details open>
<summary><h4>Step 2: Open Pull Request</h4></summary>

1. Visit your fork on GitHub
2. Click "Compare & pull request" button
3. Fill out the PR template:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
Describe how you tested these changes.

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] All tests pass

## Related Issues
Closes #(issue number)
```

</details>

<details open>
<summary><h4>Step 3: Address Review Feedback</h4></summary>

```bash
# Make requested changes
# Edit files as needed

# Commit changes
git add .
git commit -m "fix: address review feedback"

# Push updates
git push origin feature/your-feature-name
```

PR will automatically update with new commits.

</details>

### PR Review Criteria

<table>
<tr>
<th width="30%">Category</th>
<th width="70%">What We Look For</th>
</tr>
<tr>
<td><strong>Code Quality</strong></td>
<td>Clean, readable, follows standards, well-documented</td>
</tr>
<tr>
<td><strong>Functionality</strong></td>
<td>Works as intended, no regressions, handles edge cases</td>
</tr>
<tr>
<td><strong>Testing</strong></td>
<td>Adequately tested, includes test cases if applicable</td>
</tr>
<tr>
<td><strong>Documentation</strong></td>
<td>README updated, code commented, clear commit messages</td>
</tr>
<tr>
<td><strong>Performance</strong></td>
<td>No unnecessary overhead, efficient algorithms</td>
</tr>
<tr>
<td><strong>Security</strong></td>
<td>Input validation, no vulnerabilities introduced</td>
</tr>
</table>

### After Merging

Once your PR is merged:

1. **Delete your feature branch** (both local and remote)
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your main branch**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

3. **Celebrate!** You've contributed to Glance!

---

## Community Guidelines

### Communication

<table>
<tr>
<td width="50%">

**Where to Discuss**

- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code reviews, implementation details
- **GitHub Discussions**: General questions, ideas
- **Team Website**: Official announcements

</td>
<td width="50%">

**Best Practices**

- Be respectful and professional
- Stay on topic
- Provide context and details
- Use clear, concise language
- Search before asking
- Thank people for their help

</td>
</tr>
</table>

### Getting Help

<table>
<tr>
<th>Question Type</th>
<th>Where to Ask</th>
</tr>
<tr>
<td>Bug or issue</td>
<td>Open GitHub Issue</td>
</tr>
<tr>
<td>Feature idea</td>
<td>Open GitHub Discussion</td>
</tr>
<tr>
<td>How to use</td>
<td>Check README, then ask in Discussions</td>
</tr>
<tr>
<td>Development question</td>
<td>Comment on related PR/Issue</td>
</tr>
<tr>
<td>Security concern</td>
<td>Email Team Ignition privately</td>
</tr>
</table>

---

## Recognition

### Contributors

All contributors will be recognized in:

- **README.md**: Contributors section (coming soon)
- **CONTRIBUTORS.md**: Detailed list of contributions
- **Release Notes**: Mentioned in version announcements
- **GitHub**: Visible in repository contributors

### Types of Recognition

<table>
<tr>
<th>Contribution Level</th>
<th>Recognition</th>
</tr>
<tr>
<td><strong>First-time Contributors</strong></td>
<td>Welcome message, guidance for future contributions</td>
</tr>
<tr>
<td><strong>Regular Contributors</strong></td>
<td>Listed in CONTRIBUTORS.md, mentioned in releases</td>
</tr>
<tr>
<td><strong>Major Contributors</strong></td>
<td>Special mention in README, project acknowledgments</td>
</tr>
<tr>
<td><strong>Core Team</strong></td>
<td>Elevated permissions, design decision involvement</td>
</tr>
</table>

---

## Troubleshooting

### Common Setup Issues

<details>
<summary><h4>Import Errors</h4></summary>

**Problem**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

</details>

<details>
<summary><h4>Git Issues</h4></summary>

**Problem**: Merge conflicts

**Solution**:
```bash
# Update your branch with latest main
git fetch upstream
git checkout feature/your-branch
git rebase upstream/main

# Resolve conflicts in affected files
# Then:
git add .
git rebase --continue
```

**Problem**: Accidentally committed to main

**Solution**:
```bash
# Move commit to new branch
git branch feature/new-branch
git reset --hard origin/main
git checkout feature/new-branch
```

</details>

<details>
<summary><h4>Application Won't Run</h4></summary>

**Problem**: Application crashes on startup

**Checklist**:
- Python 3.8+ installed?
- All dependencies installed?
- Virtual environment activated?
- No syntax errors in modified code?
- Try with original code first

</details>

### Getting Additional Help

If you're stuck:

1. Search existing issues on GitHub
2. Check the main README.md
3. Ask in GitHub Discussions
4. Contact Team Ignition through our website

---

<div align="center">

<h2>Thank You for Contributing!</h2>

<p><strong>Your contributions help make Glance better for everyone.</strong></p>

<p><em>Whether you're fixing a typo or adding a major feature,<br/>every contribution is valued and appreciated.</em></p>

<hr/>

<p>
  <a href="https://github.com/teamignitionvitc/Glance">View Project</a> •
  <a href="https://github.com/teamignitionvitc/Glance/issues">Report Issues</a> •
  <a href="https://glance.teamignition.space/">Documentation</a>
</p>

<p><sub>Made with ❤️ by Team Ignition Software Department</sub></p>

<img src="docs/public/ign_logo_wht.png" alt="Team Ignition" width="120"/>

</div>