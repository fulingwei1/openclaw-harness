# OpenClaw Harness - VS Code Extension

AI-powered code generation, evaluation, and refactoring for Visual Studio Code.

## Features

### 🚀 Code Generation
- Generate code from natural language descriptions
- Support for multiple programming languages
- Context-aware generation
- Auto-evaluation after generation

### ✅ Code Evaluation
- Automatic code quality assessment
- Best practices checking
- Performance analysis
- Security vulnerability detection

### 📖 Code Explanation
- Detailed code explanation
- Step-by-step breakdown
- Complexity analysis

### 🔧 Code Refactoring
- Automatic code refactoring
- Style improvements
- Performance optimizations

### 🔍 Semantic Search
- Search for similar code
- Code snippet reuse
- Pattern recognition

## Installation

### From VSIX (Recommended)

1. Download `openclaw-harness-0.3.0.vsix`
2. Open VS Code
3. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
4. Type "Install from VSIX"
5. Select the downloaded file

### From Source

```bash
cd vscode-extension
npm install
npm run compile
```

Press `F5` to run in development mode.

## Usage

### Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `Harness: Generate Code` | `Ctrl+Alt+G` | Generate code from description |
| `Harness: Evaluate Code` | `Ctrl+Alt+E` | Evaluate current code |
| `Harness: Explain Code` | - | Explain selected code |
| `Harness: Refactor Code` | - | Refactor current code |
| `Harness: Search Code` | - | Search for similar code |

### Context Menu

Right-click in the editor to access Harness commands:
- **Generate Code**: Generate code at cursor position
- **Evaluate Code**: Evaluate entire file or selection
- **Explain Code**: Explain selected code

## Configuration

Configure in VS Code settings (`Ctrl+,`):

```json
{
  "harness.provider": "openai",
  "harness.model": "gpt-4",
  "harness.apiKey": "your-api-key",
  "harness.autoEvaluate": true,
  "harness.evaluatorThreshold": 0.9
}
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `harness.provider` | string | `"openai"` | LLM provider (openai, anthropic, zai, kimi) |
| `harness.model` | string | `"gpt-4"` | Model to use |
| `harness.apiKey` | string | `""` | API key for the provider |
| `harness.autoEvaluate` | boolean | `false` | Auto-evaluate generated code |
| `harness.evaluatorThreshold` | number | `0.9` | Evaluation threshold |

## Requirements

- OpenClaw Harness server running on `http://localhost:8000`
- Valid API key for your LLM provider

## Example Workflow

### 1. Generate Code

1. Press `Ctrl+Alt+G`
2. Enter task description: "Create a REST API endpoint for user login"
3. Code will be generated and inserted at cursor position

### 2. Evaluate Code

1. Press `Ctrl+Alt+E`
2. View evaluation score and feedback
3. Improve code based on suggestions

### 3. Explain Code

1. Select code to explain
2. Right-click → Harness: Explain Code
3. View detailed explanation in new panel

## Keyboard Shortcuts

- `Ctrl+Alt+G` (Windows/Linux) / `Cmd+Alt+G` (macOS): Generate Code
- `Ctrl+Alt+E` (Windows/Linux) / `Cmd+Alt+E` (macOS): Evaluate Code

## Troubleshooting

### "API 调用失败"

Ensure Harness server is running:
```bash
cd ~/Projects/openclaw-harness
make web
```

### "No editor active"

Open a file in VS Code before using Harness commands.

## Contributing

Found a bug? Have a feature request?

Open an issue: https://github.com/fulingwei1/openclaw-harness/issues

## License

MIT

## Links

- [GitHub Repository](https://github.com/fulingwei1/openclaw-harness)
- [Documentation](https://github.com/fulingwei1/openclaw-harness/blob/main/README.md)
- [OpenClaw](https://openclaw.ai)

---

**Enjoy coding with AI! 🎉**
