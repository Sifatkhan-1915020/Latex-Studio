// AI Copilot & LaTeX Expert Agent Controller

class AICopilotController {
  constructor(editorInstance) {
    this.editorInstance = editorInstance;
    this.apiKey = localStorage.getItem('overleaf_ai_gemini_key') || '';
    this.provider = localStorage.getItem('overleaf_ai_provider') || 'auto';
    this.isLoading = false;
    this.lastFixResult = null;

    this.init();
  }

  init() {
    this.setupListeners();
  }

  setupListeners() {
    const aiToggleBtn = document.getElementById('btn-ai-copilot');
    const aiCloseBtn = document.getElementById('btn-close-ai');
    const aiDrawer = document.getElementById('ai-copilot-drawer');
    const aiSettingsBtn = document.getElementById('btn-ai-settings');
    const aiSettingsModal = document.getElementById('ai-settings-modal');
    const aiSaveSettingsBtn = document.getElementById('btn-save-ai-settings');
    const aiCancelSettingsBtn = document.getElementById('btn-cancel-ai-settings');
    const aiSubmitPromptBtn = document.getElementById('btn-ai-submit-prompt');
    const aiPromptInput = document.getElementById('ai-prompt-input');
    const applyAiFixBtn = document.getElementById('btn-apply-ai-fix');
    const discardAiFixBtn = document.getElementById('btn-discard-ai-fix');

    if (aiToggleBtn && aiDrawer) {
      aiToggleBtn.onclick = () => {
        aiDrawer.classList.toggle('open');
        if (aiDrawer.classList.contains('open') && !this.lastFixResult) {
          // If first open with warnings/errors, suggest quick diagnosis
          if (this.editorInstance.currentErrors.length > 0 || this.editorInstance.currentWarnings.length > 0) {
            this.requestAIAssist('Diagnose current compiler errors and warnings, and provide optimal fixes.');
          }
        }
      };
    }

    if (aiCloseBtn && aiDrawer) {
      aiCloseBtn.onclick = () => aiDrawer.classList.remove('open');
    }

    // Quick Action Chips
    const chips = document.querySelectorAll('.ai-chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        const prompt = chip.getAttribute('data-prompt');
        if (prompt) {
          if (aiPromptInput) aiPromptInput.value = prompt;
          this.requestAIAssist(prompt);
        }
      });
    });

    // Custom prompt submission
    if (aiSubmitPromptBtn && aiPromptInput) {
      aiSubmitPromptBtn.onclick = () => {
        const prompt = aiPromptInput.value.trim();
        if (prompt) this.requestAIAssist(prompt);
      };

      aiPromptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
          const prompt = aiPromptInput.value.trim();
          if (prompt) this.requestAIAssist(prompt);
        }
      });
    }

    // Apply AI Fix to Monaco Editor
    if (applyAiFixBtn) {
      applyAiFixBtn.onclick = () => this.applyLastFix();
    }

    if (discardAiFixBtn) {
      discardAiFixBtn.onclick = () => {
        const previewEl = document.getElementById('ai-fix-preview-card');
        if (previewEl) previewEl.style.display = 'none';
        showToast('AI Fix discarded', 'info');
      };
    }

    // Settings Modal
    if (aiSettingsBtn && aiSettingsModal) {
      aiSettingsBtn.onclick = () => {
        const keyInput = document.getElementById('ai-settings-gemini-key');
        const providerSelect = document.getElementById('ai-settings-provider');
        if (keyInput) keyInput.value = this.apiKey;
        if (providerSelect) providerSelect.value = this.provider;
        aiSettingsModal.classList.add('active');
      };
    }

    if (aiCancelSettingsBtn && aiSettingsModal) {
      aiCancelSettingsBtn.onclick = () => aiSettingsModal.classList.remove('active');
    }

    if (aiSaveSettingsBtn && aiSettingsModal) {
      aiSaveSettingsBtn.onclick = () => {
        const keyInput = document.getElementById('ai-settings-gemini-key');
        const providerSelect = document.getElementById('ai-settings-provider');
        if (keyInput) {
          this.apiKey = keyInput.value.trim();
          localStorage.setItem('overleaf_ai_gemini_key', this.apiKey);
        }
        if (providerSelect) {
          this.provider = providerSelect.value;
          localStorage.setItem('overleaf_ai_provider', this.provider);
        }
        aiSettingsModal.classList.remove('active');
        showToast('AI Agent preferences saved', 'success');
      };
    }
  }

  async requestAIAssist(userPrompt) {
    if (this.isLoading) return;
    this.isLoading = true;

    const aiDrawer = document.getElementById('ai-copilot-drawer');
    if (aiDrawer) aiDrawer.classList.add('open');

    const statusEl = document.getElementById('ai-agent-status');
    const responseBox = document.getElementById('ai-response-box');
    const previewEl = document.getElementById('ai-fix-preview-card');
    const submitBtn = document.getElementById('btn-ai-submit-prompt');

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<div class="spinner"></div> <span>Thinking...</span>';
    }

    if (statusEl) {
      statusEl.innerHTML = '<div class="pulse-dot" style="background: var(--accent-emerald);"></div> <span>AI Agent is analyzing LaTeX AST & logs...</span>';
    }

    if (responseBox) {
      responseBox.innerHTML = `
        <div class="ai-loading-skeleton">
          <div class="skeleton-line" style="width: 70%;"></div>
          <div class="skeleton-line" style="width: 90%;"></div>
          <div class="skeleton-line" style="width: 60%;"></div>
        </div>
      `;
    }

    const currentCode = this.editorInstance.editor ? this.editorInstance.editor.getValue() : '';

    try {
      const res = await fetch('/api/ai/assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: this.editorInstance.projectId,
          filename: this.editorInstance.activeFile,
          code: currentCode,
          user_prompt: userPrompt,
          errors: this.editorInstance.currentErrors,
          warnings: this.editorInstance.currentWarnings,
          api_key: this.apiKey,
          provider: this.provider
        })
      });

      const data = await res.json();
      if (data.success && data.result) {
        this.lastFixResult = data.result;
        this.renderAIResponse(data.result);
      } else {
        if (responseBox) {
          responseBox.innerHTML = `<div class="ai-error-box"><i data-lucide="alert-circle"></i> <span>${data.error || 'Failed to generate AI guidance.'}</span></div>`;
        }
      }
    } catch (err) {
      if (responseBox) {
        responseBox.innerHTML = `<div class="ai-error-box"><i data-lucide="alert-circle"></i> <span>Connection error: ${err.message}</span></div>`;
      }
    } finally {
      this.isLoading = false;
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i data-lucide="sparkles" style="width: 14px; height: 14px;"></i> <span>Ask AI</span>';
      }
      if (statusEl) {
        const modelName = (this.lastFixResult && this.lastFixResult.model_used) || 'AI Agent';
        statusEl.innerHTML = `<span class="badge badge-emerald" style="font-size: 10px;">${modelName}</span> <span style="color: #94a3b8; font-size: 11px;">Ready</span>`;
      }
      if (window.lucide) lucide.createIcons();
    }
  }

  renderAIResponse(result) {
    const responseBox = document.getElementById('ai-response-box');
    const previewEl = document.getElementById('ai-fix-preview-card');
    const changesListEl = document.getElementById('ai-changes-list');

    if (!responseBox) return;

    // Format markdown-like explanation
    let formattedHtml = this.formatMarkdown(result.explanation || 'Diagnosis completed.');
    responseBox.innerHTML = formattedHtml;

    // Render changes list & preview card if fixed_code is present
    if (result.fixed_code && result.fixed_code !== this.editorInstance.editor.getValue()) {
      if (previewEl) previewEl.style.display = 'block';
      if (changesListEl && result.changes_summary) {
        changesListEl.innerHTML = '';
        result.changes_summary.forEach(ch => {
          const li = document.createElement('li');
          li.innerHTML = `<i data-lucide="check" style="width: 12px; height: 12px; color: var(--accent-emerald); display: inline-block; vertical-align: middle; margin-right: 4px;"></i> ${ch}`;
          changesListEl.appendChild(li);
        });
      }
    } else {
      if (previewEl) previewEl.style.display = 'none';
    }

    if (window.lucide) lucide.createIcons();
  }

  formatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/^### (.*$)/gim, '<h4 class="ai-heading">$1</h4>')
      .replace(/^## (.*$)/gim, '<h3 class="ai-heading">$1</h3>')
      .replace(/^# (.*$)/gim, '<h2 class="ai-heading">$1</h2>')
      .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em>$1</em>')
      .replace(/`([^`]+)`/gim, '<code class="ai-code-inline">$1</code>')
      .replace(/^\s*-\s+(.*$)/gim, '<div class="ai-bullet"><i data-lucide="chevron-right" style="width: 13px; height: 13px; color: var(--accent-emerald);"></i> <span>$1</span></div>')
      .replace(/\n\n/gim, '<div style="height: 8px;"></div>');
    return html;
  }

  applyLastFix() {
    if (!this.lastFixResult || !this.lastFixResult.fixed_code) {
      showToast('No AI fix available to apply', 'warning');
      return;
    }

    if (this.editorInstance && this.editorInstance.editor) {
      this.editorInstance.editor.setValue(this.lastFixResult.fixed_code);
      this.editorInstance.saveActiveFile().then(() => {
        this.editorInstance.compile();
      });

      const previewEl = document.getElementById('ai-fix-preview-card');
      if (previewEl) previewEl.style.display = 'none';

      showToast('⚡ AI Corrections applied to code & recompiled!', 'success');
    }
  }
}

window.AICopilotController = AICopilotController;
