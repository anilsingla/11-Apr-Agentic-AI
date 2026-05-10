# GitHub Copilot Guide for Writing Code

A practical guide to using GitHub Copilot effectively as your AI pair programmer.

## What is GitHub Copilot?

GitHub Copilot is an AI-powered code completion tool that suggests whole lines or blocks of code as you type. It works inside your editor (VS Code, JetBrains IDEs, Neovim, Visual Studio, and others) and uses the context of your file, related files, and comments to generate suggestions.

There are three main interaction modes:

- **Inline completions** — ghost-text suggestions while you type. Press `Tab` to accept.
- **Copilot Chat** — a conversational sidebar for questions, refactors, explanations, and multi-file edits.
- **Copilot in the CLI / agent mode** — runs commands, edits files across a project, and executes longer tasks.

## Setup Essentials

1. Install the Copilot extension for your editor.
2. Sign in with a GitHub account that has an active Copilot subscription (Free, Pro, Business, or Enterprise).
3. Verify it works: open a new file, type a comment like `// function that reverses a string`, and check that a suggestion appears.
4. Learn the keybindings — they're the difference between Copilot feeling magical and feeling clunky.

### Core keybindings (VS Code defaults)

| Action | Mac | Windows / Linux |
|---|---|---|
| Accept suggestion | `Tab` | `Tab` |
| Dismiss suggestion | `Esc` | `Esc` |
| Next suggestion | `Option + ]` | `Alt + ]` |
| Previous suggestion | `Option + [` | `Alt + [` |
| Open Copilot panel | `Ctrl + Enter` | `Ctrl + Enter` |
| Trigger inline chat | `Cmd + I` | `Ctrl + I` |
| Open Copilot Chat | `Ctrl + Cmd + I` | `Ctrl + Alt + I` |

## How to Get Better Suggestions

Copilot's quality depends almost entirely on the context you give it. Treat it like a smart collaborator who only sees what's on your screen.

### 1. Write descriptive comments

Vague comments produce vague code. Specific comments produce specific code.

```python
# Bad: too vague
# function to handle data

# Good: specific behavior, inputs, outputs
# Parse a CSV string into a list of dicts.
# First row is the header. Skip empty lines. Trim whitespace from values.
def parse_csv(text: str) -> list[dict]:
```

### 2. Use meaningful names

Function and variable names are signals. `calculateMonthlyRecurringRevenue` gives Copilot far more to work with than `calc`.

### 3. Provide examples in comments

When the shape of input or output matters, show it.

```javascript
// Convert "2024-03-15T10:30:00Z" to "March 15, 2024 at 10:30 AM"
function formatTimestamp(iso) {
```

### 4. Open related files in tabs

Copilot looks at your other open editor tabs to build context. If you're writing tests, keep the file under test open. If you're implementing an interface, keep the interface file open.

### 5. Define types and signatures first

Type annotations and function signatures act like a spec. Write them before the body and Copilot will fill in implementations that respect them.

```typescript
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

function findActiveUsers(users: User[], sinceDays: number): User[] {
  // Copilot now knows exactly what to return
}
```

### 6. Stay consistent with your codebase

If your project uses snake_case, async/await, or a particular logging library, use it once near where you're working. Copilot will mirror the style in subsequent suggestions.

## Common Workflows

### Generating a function from a comment

Write the comment, press Enter, and start the signature. Copilot usually completes the rest.

```python
# Return the n-th Fibonacci number using memoization.
def fib(n: int) -> int:
```

### Writing tests

Open the source file alongside the test file. Then prompt with the test name:

```javascript
// In user.test.js, with user.js open in another tab
describe('createUser', () => {
  it('rejects invalid email addresses', () => {
```

### Refactoring with Copilot Chat

Select code and ask. Effective prompts are specific:

- "Extract the validation logic into a separate function."
- "Convert this Promise chain to async/await."
- "Replace the for loop with a more idiomatic map/filter chain."

Avoid: "Make this better." Better by what measure?

### Explaining unfamiliar code

Select a block and use `/explain` in Copilot Chat. Useful when reading a new codebase, debugging legacy code, or reviewing a PR.

### Generating boilerplate

Copilot shines at the tedious parts: regex, SQL queries, config files, API client wrappers, data transformations, mock data, and one-off scripts.

## Prompting Patterns That Work

**Pattern: state the goal, then the constraints.**

```
Write a Python function that:
- accepts a list of dicts representing orders
- groups them by customer_id
- returns total spend per customer, sorted descending
- uses only the standard library
```

**Pattern: provide a small example pair.**

Show one input and the desired output. This is more reliable than describing transformations in prose.

**Pattern: ask for alternatives.**

In chat: "Show me three ways to implement this — one with recursion, one iterative, one functional. Note tradeoffs."

**Pattern: iterate, don't restart.**

If a suggestion is 80% right, keep it and ask for the specific fix: "Now handle the case where the input list is empty." Don't throw it out and rephrase from scratch.

## Things to Watch Out For

### It can be confidently wrong

Copilot generates plausible code, not necessarily correct code. It can invent function names, misremember API signatures, hallucinate library features, and mix up versions. Always verify against documentation for anything non-trivial.

### Security and licensing

- Don't paste secrets, API keys, or proprietary data into prompts. They become part of the request context.
- Review generated code for vulnerabilities — SQL injection, path traversal, weak crypto, unvalidated input. Copilot reproduces patterns from training data, including bad ones.
- Check your organization's policy on AI-generated code. Some require disclosure or have rules about which repositories can use it.

### Don't accept code you don't understand

If you can't explain a generated block to a colleague, you probably shouldn't ship it. Reading and understanding is faster long-term than debugging mysterious code later.

### Bias toward your own logic for hard parts

For business logic, novel algorithms, and decisions that depend on product context, write the structure yourself and let Copilot fill in the mechanical parts. The higher the stakes, the more you should drive.

### Tests are not optional

AI-assisted code makes tests more important, not less. They're how you verify what was generated actually works. Write tests for the behavior you want, then accept suggestions that pass them.

## Productivity Tips

- **Cycle through suggestions.** The first suggestion isn't always the best. `Alt + ]` to see alternatives.
- **Use the Copilot panel** (`Ctrl + Enter`) to see ten suggestions at once for tricky completions.
- **Partial accepts** — accept word-by-word with `Cmd/Ctrl + →` instead of taking the whole suggestion.
- **Reject and retype** when a suggestion is misleading you. Sometimes typing two more characters changes the suggestion entirely.
- **Disable it for sensitive files.** Use `.copilotignore` or settings to exclude config files, secrets directories, or files where suggestions are more distracting than helpful.
- **Use chat for thinking, inline for typing.** Chat is better for "how should I approach this" questions; inline completions are better for "I know what I want, just write it faster."

## A Mental Model That Helps

Think of Copilot as a junior developer with broad but shallow knowledge. They've seen a huge amount of code, they're fast, and they're enthusiastic — but they don't know your codebase, your users, or your constraints unless you tell them. They'll happily produce something confident-looking that's subtly wrong.

Your job is the same as with any junior collaborator: give clear direction, review the output, and own the result.

## Quick Reference

**Do:**
- Write specific comments and good names before generating code
- Keep relevant files open as context
- Verify suggestions, especially for APIs and security-sensitive code
- Iterate on partial suggestions instead of restarting
- Use chat for design questions, inline for typing speed

**Don't:**
- Accept code you don't understand
- Paste secrets or proprietary data into prompts
- Skip tests because the code looked right
- Use it as a substitute for learning the language or framework
- Assume it knows your codebase's conventions without seeing them
