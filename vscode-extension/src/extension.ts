import * as vscode from 'vscode';
import axios from 'axios';

let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('OpenClaw Harness');
    outputChannel.appendLine('OpenClaw Harness 已激活');

    // 注册命令
    const generateCommand = vscode.commands.registerCommand('harness.generate', generateCode);
    const evaluateCommand = vscode.commands.registerCommand('harness.evaluate', evaluateCode);
    const explainCommand = vscode.commands.registerCommand('harness.explain', explainCode);
    const refactorCommand = vscode.commands.registerCommand('harness.refactor', refactorCode);
    const searchCommand = vscode.commands.registerCommand('harness.search', searchCode);

    context.subscriptions.push(
        generateCommand,
        evaluateCommand,
        explainCommand,
        refactorCommand,
        searchCommand,
        outputChannel
    );
}

async function generateCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的编辑器');
        return;
    }

    // 获取任务描述
    const task = await vscode.window.showInputBox({
        prompt: '输入任务描述',
        placeHolder: '例如：创建一个 REST API endpoint'
    });

    if (!task) {
        return;
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "正在生成代码...",
                cancellable: false
            },
            async (progress) => {
                const config = vscode.workspace.getConfiguration('harness');
                const response = await callHarnessAPI('/generate', {
                    task,
                    language: getLanguage(editor.document.languageId),
                    framework: '',
                    style: 'clean'
                });

                if (response.success) {
                    // 插入生成的代码
                    const position = editor.selection.active;
                    editor.edit(editBuilder => {
                        editBuilder.insert(position, response.code);
                    });

                    vscode.window.showInformationMessage('✓ 代码生成成功');
                    outputChannel.appendLine(`生成代码: ${task}`);

                    // 自动评估
                    if (config.get<boolean>('autoEvaluate')) {
                        await evaluateCode();
                    }
                } else {
                    vscode.window.showErrorMessage(`生成失败: ${response.error}`);
                }
            }
        );
    } catch (error) {
        vscode.window.showErrorMessage(`错误: ${error}`);
        outputChannel.appendLine(`错误: ${error}`);
    }
}

async function evaluateCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的编辑器');
        return;
    }

    const code = editor.document.getText();
    if (!code.trim()) {
        vscode.window.showWarningMessage('代码为空');
        return;
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "正在评估代码...",
                cancellable: false
            },
            async (progress) => {
                const response = await callHarnessAPI('/evaluate', {
                    code,
                    language: getLanguage(editor.document.languageId)
                });

                if (response.success) {
                    const config = vscode.workspace.getConfiguration('harness');
                    const threshold = config.get<number>('evaluatorThreshold') || 0.9;

                    const message = response.score >= threshold
                        ? `✓ 评估通过: ${response.score.toFixed(2)}`
                        : `⚠ 评估未达标: ${response.score.toFixed(2)} (阈值: ${threshold})`;

                    vscode.window.showInformationMessage(message);

                    // 显示详细反馈
                    const items = ['查看详情', '关闭'];
                    const selection = await vscode.window.showInformationMessage(
                        message,
                        ...items
                    );

                    if (selection === '查看详情') {
                        const panel = vscode.window.createWebviewPanel(
                            'evaluationResult',
                            '代码评估结果',
                            vscode.ViewColumn.Two,
                            {}
                        );

                        panel.webview.html = getEvaluationWebview(response);
                    }

                    outputChannel.appendLine(`评估结果: ${response.score}`);
                } else {
                    vscode.window.showErrorMessage(`评估失败: ${response.error}`);
                }
            }
        );
    } catch (error) {
        vscode.window.showErrorMessage(`错误: ${error}`);
    }
}

async function explainCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的编辑器');
        return;
    }

    const selection = editor.selection;
    const code = selection.isEmpty
        ? editor.document.getText()
        : editor.document.getText(selection);

    if (!code.trim()) {
        vscode.window.showWarningMessage('请选择代码');
        return;
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "正在分析代码...",
                cancellable: false
            },
            async (progress) => {
                const response = await callHarnessAPI('/explain', {
                    code,
                    language: getLanguage(editor.document.languageId)
                });

                if (response.success) {
                    const panel = vscode.window.createWebviewPanel(
                        'codeExplanation',
                        '代码解释',
                        vscode.ViewColumn.Two,
                        {}
                    );

                    panel.webview.html = getExplanationWebview(response.explanation);
                    outputChannel.appendLine('代码解释完成');
                } else {
                    vscode.window.showErrorMessage(`解释失败: ${response.error}`);
                }
            }
        );
    } catch (error) {
        vscode.window.showErrorMessage(`错误: ${error}`);
    }
}

async function refactorCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的编辑器');
        return;
    }

    const code = editor.document.getText();
    if (!code.trim()) {
        vscode.window.showWarningMessage('代码为空');
        return;
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "正在重构代码...",
                cancellable: false
            },
            async (progress) => {
                const response = await callHarnessAPI('/refactor', {
                    code,
                    language: getLanguage(editor.document.languageId)
                });

                if (response.success) {
                    // 显示重构后的代码
                    const document = await vscode.workspace.openTextDocument({
                        content: response.refactored_code,
                        language: editor.document.languageId
                    });

                    await vscode.window.showTextDocument(document, vscode.ViewColumn.Two);
                    vscode.window.showInformationMessage('✓ 代码重构完成');

                    outputChannel.appendLine('代码重构完成');
                } else {
                    vscode.window.showErrorMessage(`重构失败: ${response.error}`);
                }
            }
        );
    } catch (error) {
        vscode.window.showErrorMessage(`错误: ${error}`);
    }
}

async function searchCode() {
    const query = await vscode.window.showInputBox({
        prompt: '输入搜索查询',
        placeHolder: '例如：authentication function'
    });

    if (!query) {
        return;
    }

    try {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "正在搜索代码...",
                cancellable: false
            },
            async (progress) => {
                const response = await callHarnessAPI('/search', {
                    query,
                    top_k: 5
                });

                if (response.success && response.results.length > 0) {
                    const items = response.results.map((r: any, i: number) => ({
                        label: `结果 ${i + 1} (相似度: ${r.score.toFixed(2)})`,
                        description: r.code.substring(0, 100) + '...',
                        code: r.code
                    }));

                    const selected = await vscode.window.showQuickPick(items, {
                        placeHolder: '选择一个结果'
                    });

                    if (selected) {
                        const editor = vscode.window.activeTextEditor;
                        if (editor) {
                            const position = editor.selection.active;
                            editor.edit(editBuilder => {
                                editBuilder.insert(position, selected.code);
                            });
                        }
                    }
                } else {
                    vscode.window.showInformationMessage('未找到相关代码');
                }
            }
        );
    } catch (error) {
        vscode.window.showErrorMessage(`错误: ${error}`);
    }
}

async function callHarnessAPI(endpoint: string, data: any): Promise<any> {
    const config = vscode.workspace.getConfiguration('harness');
    const serverUrl = 'http://localhost:8000'; // 默认 Harness Web 服务

    try {
        const response = await axios.post(`${serverUrl}/api${endpoint}`, data, {
            timeout: 60000
        });
        return response.data;
    } catch (error) {
        throw new Error(`API 调用失败: ${error}`);
    }
}

function getLanguage(vscodeLang: string): string {
    const mapping: { [key: string]: string } = {
        'python': 'python',
        'javascript': 'javascript',
        'typescript': 'typescript',
        'java': 'java',
        'go': 'go',
        'rust': 'rust'
    };
    return mapping[vscodeLang] || vscodeLang;
}

function getEvaluationWebview(result: any): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .score { font-size: 48px; font-weight: bold; color: ${result.score >= 0.9 ? '#28a745' : '#ffc107'}; }
        .feedback { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>代码评估结果</h1>
    <div class="score">${result.score.toFixed(2)}</div>
    <p>状态: ${result.passed ? '✓ 通过' : '✗ 未通过'}</p>
    <div class="feedback">
        <h3>反馈</h3>
        <p>${result.feedback}</p>
    </div>
</body>
</html>`;
}

function getExplanationWebview(explanation: string): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: sans-serif; padding: 20px; line-height: 1.6; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>代码解释</h1>
    <div>${explanation}</div>
</body>
</html>`;
}

export function deactivate() {
    outputChannel.appendLine('OpenClaw Harness 已停用');
}
