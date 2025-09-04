# hi5 - Your First AI Agent 🚀

Welcome to **hi5**, a tiny AI agent that automatically finds the most important lines in any text file! This is a perfect project for learning how AI agents work.

## What is an AI Agent? 🤖

An **AI agent** is a program that can:
- **Perceive** its environment (read files, analyze data)
- **Think** about what it sees (score and rank information)
- **Act** on its analysis (generate reports, make decisions)

Think of it like a smart assistant that never gets tired and can process information super fast!

### How hi5 Works
1. **Input**: You give it a text file (like notes, articles, or documents)
2. **Analysis**: It reads every line and scores them based on importance
3. **Output**: It gives you the top 5 most important lines with explanations

## Why This Agent is Special ✨

- **Offline**: Works without internet - your data stays private
- **Deterministic**: Same input always gives same output (no randomness)
- **Transparent**: Shows you exactly why each line was chosen
- **Fast**: Processes files in milliseconds
- **Simple**: Easy to understand and modify

## Complete Beginner Tutorial 📚

### Step 1: What You'll Need
- A computer with Python 3.7+ installed
- Basic familiarity with command line (don't worry, we'll guide you!)

### Step 2: Understanding the Project Structure
```
hi5/
├── src/hi5/           # The main agent code
│   ├── score.py       # How it analyzes text
│   ├── select.py      # How it picks highlights
│   └── cli.py         # Command-line interface
├── data/              # Sample files to test with
├── tests/             # Tests to make sure everything works
└── requirements.txt   # Dependencies (like ingredients for a recipe)
```

### Step 3: Setting Up Your Environment

**What's a virtual environment?** Think of it as a clean workspace for your project. It keeps your project's dependencies separate from other Python projects on your computer.

1. **Open your terminal/command prompt** and navigate to the project folder:
```bash
cd /path/to/your/hi5/project
```

2. **Create a virtual environment** (like setting up a new workspace):
```bash
python -m venv venv
```

3. **Activate the virtual environment** (enter your workspace):
```bash
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You'll know it worked when you see `(venv)` at the beginning of your command prompt!

4. **Install the required packages** (get the tools your agent needs):
```bash
pip install -r requirements.txt
```

### Step 4: Your First Agent Run! 🎉

Let's run the agent on a sample file:

```bash
PYTHONPATH=/path/to/your/hi5/project/src python -m hi5.cli pick --path data/sample_notes.txt
```

**What just happened?**
- The agent read `data/sample_notes.txt`
- It analyzed each line and gave it a score
- It picked the 5 most important lines
- It created two output files with the results

### Step 5: Understanding the Output

The agent creates two files:

**1. `highlights.json`** - Machine-readable format:
```json
[
  {
    "rank": 1,
    "line_no": 7,
    "text": "- The algorithm works well for structured content.",
    "reason": "period; bullet; len=50"
  }
]
```

**2. `highlights.md`** - Human-readable checklist:
```markdown
# Highlights
- [ ] (1) L7: - The algorithm works well for structured content.
      reason: period; bullet; len=50
```

### Step 6: How the Agent Thinks 🧠

The agent scores lines based on these rules:
- **+1 point**: Line ends with a period (complete thoughts)
- **+1 point**: Contains important keywords (summary, key, result, finding, todo)
- **+1 point**: Starts with a bullet point (organized information)
- **+1 point**: Good length (40-160 characters - not too short, not too long)
- **-1 point**: ALL CAPS (hard to read)

### Step 7: Try It With Your Own Files!

1. **Create a test file**:
```bash
echo "This is a test document.

## Summary
Here are the key findings from our research.

## Results
- The new system works 50% faster.
- Users report higher satisfaction.
- Implementation was completed on time.

## TODO
- Deploy to production
- Train the support team

This concludes our project report." > my_test.txt
```

2. **Run the agent on your file**:
```bash
PYTHONPATH=/path/to/your/hi5/project/src python -m hi5.cli pick --path my_test.txt
```

3. **Check the results**:
```bash
cat highlights.json
cat highlights.md
```

### Step 8: Understanding the Code (Optional but Recommended!)

**Want to see how the magic happens?** Let's look at the key files:

**`src/hi5/score.py`** - The "brain" of the agent:
```python
def score_line(line: str) -> Tuple[int, List[str]]:
    score = 0
    reasons = []
    
    # +1 if line ends with period
    if line.endswith('.'):
        score += 1
        reasons.append("period")
    
    # +1 if contains keyword
    for keyword in ["summary", "key", "result", "finding", "todo"]:
        if keyword in line.lower():
            score += 1
            reasons.append(f"keyword={keyword}")
            break
    
    return score, reasons
```

**`src/hi5/select.py`** - How it picks the best lines:
```python
def pick_highlights(lines: List[str], k: int = 5) -> List[Dict]:
    # Score each line
    candidates = []
    for i, line in enumerate(lines, 1):
        score, reasons = score_line(line)
        if score > 0:  # Only keep good lines
            candidates.append({
                'score': score,
                'line_no': i,
                'text': line,
                'reasons': reasons
            })
    
    # Sort by score (highest first), then by line number
    candidates.sort(key=lambda x: (-x['score'], x['line_no']))
    
    # Take the top k
    return candidates[:k]
```

## Running Tests 🧪

**What are tests?** Tests are like quality checks that make sure your agent works correctly. They're like having a robot that checks your homework!

```bash
pytest -q
```

This runs all the tests and tells you if everything is working properly.

## Customizing Your Agent 🛠️

Want to make the agent smarter? Here are some ideas:

1. **Add new keywords** in `src/hi5/score.py`:
```python
KEYWORDS = {"summary", "key", "result", "finding", "todo", "important", "critical"}
```

2. **Change the scoring rules** - maybe give more points to longer lines:
```python
# In score_line function
if MIN_LENGTH <= line_len <= MAX_LENGTH * 2:  # Allow longer lines
    score += 1
    reasons.append(f"len={line_len}")
```

3. **Pick more highlights**:
```bash
python -m hi5.cli pick --path my_file.txt --k 10  # Get top 10 instead of 5
```

## Troubleshooting 🔧

**Problem**: "Module not found" error
**Solution**: Make sure you're using the full PYTHONPATH:
```bash
PYTHONPATH=/full/path/to/your/project/src python -m hi5.cli pick --path data/sample_notes.txt
```

**Problem**: Virtual environment not working
**Solution**: Make sure you activated it (you should see `(venv)` in your prompt)

**Problem**: Tests failing
**Solution**: Make sure you installed all dependencies:
```bash
pip install -r requirements.txt
```

## What's Next? 🚀

Congratulations! You've just built and run your first AI agent. Here are some ideas for what to do next:

1. **Try it on different types of files** (emails, articles, code comments)
2. **Modify the scoring rules** to match your preferences
3. **Add new features** (like highlighting different types of content)
4. **Learn about other types of agents** (web scrapers, chatbots, recommendation systems)

## Key Concepts You've Learned 🎓

- **AI Agent**: A program that perceives, thinks, and acts
- **Virtual Environment**: A clean workspace for Python projects
- **Scoring Algorithm**: Rules for ranking information
- **Deterministic**: Same input always gives same output
- **CLI**: Command Line Interface - how you talk to your agent
- **Testing**: Automated quality checks for your code

You're now ready to build more complex agents! 🎉
