// Overleaf Main Editor Controller

class OverleafEditor {
  constructor(projectId, initialMainFile) {
    this.projectId = projectId;
    this.mainFile = initialMainFile || 'main.tex';
    this.activeFile = this.mainFile;
    this.files = [];
    this.editor = null;
    this.models = {}; // filename -> monaco model
    this.pdfViewer = new PDFViewerController('pdf-view-container');
    this.autoCompileEnabled = true;
    this.isCompiling = false;
    this.compileDebounceTimer = null;
    this.currentErrors = [];
    this.currentWarnings = [];
    this.lastFixes = [];
    this.lastHealedContent = null;

    this.init();
  }

  async init() {
    this.setupSplitPanes();
    this.setupEventListeners();
    await this.loadProjectFiles();
    this.initMonaco();
  }

  // Split Panes Resizing using drag events
  setupSplitPanes() {
    const sidebar = document.getElementById('sidebar-panel');
    const codePanel = document.getElementById('code-panel');
    const pdfPanel = document.getElementById('pdf-panel');
    const gutterLeft = document.getElementById('gutter-left');
    const gutterRight = document.getElementById('gutter-right');

    if (gutterLeft && sidebar) {
      let isDraggingLeft = false;
      gutterLeft.addEventListener('mousedown', (e) => {
        isDraggingLeft = true;
        gutterLeft.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isDraggingLeft) return;
        const newWidth = Math.max(160, Math.min(400, e.clientX));
        sidebar.style.width = `${newWidth}px`;
        if (this.editor) this.editor.layout();
      });

      window.addEventListener('mouseup', () => {
        if (isDraggingLeft) {
          isDraggingLeft = false;
          gutterLeft.classList.remove('dragging');
          document.body.style.cursor = '';
          if (this.editor) this.editor.layout();
        }
      });
    }

    if (gutterRight && pdfPanel) {
      let isDraggingRight = false;
      gutterRight.addEventListener('mousedown', (e) => {
        isDraggingRight = true;
        gutterRight.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isDraggingRight) return;
        const containerWidth = document.getElementById('editor-main-split').clientWidth;
        const newWidth = Math.max(280, Math.min(containerWidth - 350, containerWidth - e.clientX));
        pdfPanel.style.width = `${newWidth}px`;
        if (this.editor) this.editor.layout();
      });

      window.addEventListener('mouseup', () => {
        if (isDraggingRight) {
          isDraggingRight = false;
          gutterRight.classList.remove('dragging');
          document.body.style.cursor = '';
          if (this.editor) this.editor.layout();
        }
      });
    }

    window.addEventListener('resize', () => {
      if (this.editor) this.editor.layout();
    });
  }

  // Load Monaco Editor
  initMonaco() {
    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });

    require(['vs/editor/editor.main'], () => {
      // Define custom Overleaf Emerald Dark theme
      monaco.editor.defineTheme('overleaf-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment', foreground: '64748b', fontStyle: 'italic' },
          { token: 'keyword', foreground: '10b981', fontStyle: 'bold' },
          { token: 'delimiter', foreground: '94a3b8' },
          { token: 'string', foreground: '34d399' },
          { token: 'number', foreground: 'f59e0b' },
          { token: 'tag', foreground: '38bdf8' }
        ],
        colors: {
          'editor.background': '#090d16',
          'editor.foreground': '#f8fafc',
          'editorCursor.foreground': '#10b981',
          'editor.lineHighlightBackground': '#0f172a',
          'editorLineNumber.foreground': '#475569',
          'editorLineNumber.activeForeground': '#10b981',
          'editor.selectionBackground': '#1e3a5f',
          'editor.inactiveSelectionBackground': '#162842',
          'editorIndentGuide.background1': '#1e293b',
          'editorIndentGuide.activeBackground1': '#334155'
        }
      });

      // Register custom LaTeX completions
      if (window.LaTeXCompletions) {
        window.LaTeXCompletions.registerProvider(monaco, () => this.files);
      }

      const container = document.getElementById('monaco-container');
      const activeFileData = this.files.find(f => f.filename === this.activeFile);
      const initialContent = activeFileData ? (activeFileData.content || '') : '';

      this.editor = monaco.editor.create(container, {
        value: initialContent,
        language: this.getLanguageForFile(this.activeFile),
        theme: 'overleaf-dark',
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: 13.5,
        lineHeight: 22,
        letterSpacing: 0.2,
        tabSize: 2,
        insertSpaces: true,
        automaticLayout: true,
        wordWrap: 'on',
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        padding: { top: 14, bottom: 14 },
        renderLineHighlight: 'all',
        suggestOnTriggerCharacters: true,
        quickSuggestions: { other: true, comments: false, strings: true },
        parameterHints: { enabled: true }
      });

      // Create model for initial active file
      const model = this.editor.getModel();
      this.models[this.activeFile] = model;

      // Track cursor position for status bar
      this.editor.onDidChangeCursorPosition((e) => {
        const lineEl = document.getElementById('status-cursor');
        if (lineEl) {
          lineEl.innerText = `Ln ${e.position.lineNumber}, Col ${e.position.column}`;
        }
      });

      // Editor content change listener (autosave & debounce compile)
      model.onDidChangeContent(() => {
        const curFile = this.files.find(f => f.filename === this.activeFile);
        if (curFile) {
          curFile.content = model.getValue();
          curFile.isDirty = true;
        }

        const saveStatusEl = document.getElementById('status-save');
        if (saveStatusEl) {
          saveStatusEl.innerText = 'Unsaved changes...';
          saveStatusEl.style.color = '#f59e0b';
        }

        if (this.autoCompileEnabled) {
          if (this.compileDebounceTimer) clearTimeout(this.compileDebounceTimer);
          this.compileDebounceTimer = setTimeout(() => {
            this.saveActiveFile().then(() => this.compile());
          }, 1200);
        }
      });

      // Register Hotkeys
      this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        this.saveActiveFile();
      });

      this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        this.saveActiveFile().then(() => this.compile());
      });

      // Initial Compile on open
      this.compile();
    });
  }

  getLanguageForFile(filename) {
    if (filename.endsWith('.tex') || filename.endsWith('.sty') || filename.endsWith('.cls')) return 'latex';
    if (filename.endsWith('.bib')) return 'bibtex';
    if (filename.endsWith('.json')) return 'json';
    if (filename.endsWith('.xml') || filename.endsWith('.svg')) return 'xml';
    return 'plaintext';
  }

  // Load all project files from API
  async loadProjectFiles() {
    try {
      const res = await fetch(`/api/projects/${this.projectId}/files`);
      const data = await res.json();
      if (data.success) {
        this.files = data.files;
        // Fetch content for each text file
        for (let file of this.files) {
          if (!file.filename.match(/\.(png|jpg|jpeg|gif|webp|pdf)$/i)) {
            const fRes = await fetch(`/api/projects/${this.projectId}/files/${file.filename}`);
            const fData = await fRes.json();
            file.content = fData.content || '';
          }
        }
        this.renderFileTree();
      }
    } catch (err) {
      console.error('Error loading files:', err);
    }
  }

  renderFileTree() {
    const treeEl = document.getElementById('file-tree');
    if (!treeEl) return;

    treeEl.innerHTML = '';
    this.files.forEach(f => {
      const item = document.createElement('div');
      item.className = `file-item ${f.filename === this.activeFile ? 'active' : ''}`;
      
      const isTex = f.filename.endsWith('.tex');
      const isBib = f.filename.endsWith('.bib');
      const isImg = f.filename.match(/\.(png|jpg|jpeg|gif|webp|svg)$/i);
      const iconName = isTex ? 'file-code' : (isBib ? 'bookmark' : (isImg ? 'image' : 'file-text'));

      item.innerHTML = `
        <div class="file-item-left" title="${f.filename}">
          <i data-lucide="${iconName}" class="file-item-icon" style="width: 16px; height: 16px;"></i>
          <span>${f.filename}</span>
          ${f.filename === this.mainFile ? '<span class="badge badge-emerald" style="font-size: 9px; padding: 1px 4px;">Main</span>' : ''}
        </div>
        <div class="file-item-actions">
          ${f.filename !== this.mainFile ? `
            <button class="sidebar-btn" title="Delete file" onclick="event.stopPropagation(); window.editorApp.deleteFile('${f.filename}')">
              <i data-lucide="trash-2" style="width: 14px; height: 14px; color: #fb7185;"></i>
            </button>
          ` : ''}
        </div>
      `;

      item.onclick = () => this.switchActiveFile(f.filename);
      treeEl.appendChild(item);
    });

    if (window.lucide) lucide.createIcons();
    this.renderTabs();
  }

  renderTabs() {
    const tabsBar = document.getElementById('code-tabs-bar');
    if (!tabsBar) return;

    tabsBar.innerHTML = '';
    const tab = document.createElement('div');
    tab.className = 'code-tab active';
    tab.innerHTML = `
      <i data-lucide="file-code" style="width: 14px; height: 14px; color: var(--accent-emerald);"></i>
      <span>${this.activeFile}</span>
    `;
    tabsBar.appendChild(tab);
    if (window.lucide) lucide.createIcons();
  }

  // Switch Active File
  switchActiveFile(filename) {
    if (filename === this.activeFile) return;

    // Check if binary image
    if (filename.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
      showToast(`Selected image asset: ${filename}`, 'info');
      return;
    }

    this.activeFile = filename;
    const fileData = this.files.find(f => f.filename === filename);
    const content = fileData ? (fileData.content || '') : '';

    if (this.editor && window.monaco) {
      let model = this.models[filename];
      if (!model) {
        model = monaco.editor.createModel(content, this.getLanguageForFile(filename));
        this.models[filename] = model;

        model.onDidChangeContent(() => {
          if (fileData) {
            fileData.content = model.getValue();
            fileData.isDirty = true;
          }
          if (this.autoCompileEnabled) {
            if (this.compileDebounceTimer) clearTimeout(this.compileDebounceTimer);
            this.compileDebounceTimer = setTimeout(() => {
              this.saveActiveFile().then(() => this.compile());
            }, 1200);
          }
        });
      }
      this.editor.setModel(model);
    }

    this.renderFileTree();
  }

  // Save current active file to server
  async saveActiveFile() {
    if (!this.editor) return;
    const content = this.editor.getValue();
    const saveStatusEl = document.getElementById('status-save');
    if (saveStatusEl) {
      saveStatusEl.innerText = 'Saving...';
      saveStatusEl.style.color = '#94a3b8';
    }

    try {
      const res = await fetch(`/api/projects/${this.projectId}/files`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: this.activeFile, content: content })
      });
      const data = await res.json();
      if (data.success) {
        const fileObj = this.files.find(f => f.filename === this.activeFile);
        if (fileObj) {
          fileObj.content = content;
          fileObj.isDirty = false;
        }
        if (saveStatusEl) {
          saveStatusEl.innerText = 'All changes saved';
          saveStatusEl.style.color = '#10b981';
        }
      }
    } catch (err) {
      if (saveStatusEl) {
        saveStatusEl.innerText = 'Save failed';
        saveStatusEl.style.color = '#fb7185';
      }
    }
  }

  // Apply Auto-Healed code to Monaco editor
  applyHealedCode() {
    if (!this.lastHealedContent || !this.editor) return;
    this.editor.setValue(this.lastHealedContent);
    this.saveActiveFile();
    const banner = document.getElementById('heal-banner');
    if (banner) banner.remove();
    showToast('Applied auto-fixes to editor!', 'success');
  }

  // Trigger manual Auto-Fix
  async autoFixCode() {
    showToast('Auto-repairing LaTeX syntax bugs...', 'info');
    await this.saveActiveFile();
    await this.compile();
    if (this.lastHealedContent) {
      this.applyHealedCode();
    } else {
      showToast('No syntax bugs needed auto-repairing!', 'success');
    }
  }

  // Compile Project to PDF
  async compile() {
    if (this.isCompiling) return;
    this.isCompiling = true;

    const compileBtn = document.getElementById('btn-compile');
    const statusCompileEl = document.getElementById('status-compile');
    if (compileBtn) {
      compileBtn.classList.add('compiling');
      compileBtn.innerHTML = '<div class="spinner"></div> <span>Compiling...</span>';
    }
    if (statusCompileEl) {
      statusCompileEl.innerHTML = '<div class="pulse-dot" style="background: #f59e0b;"></div> <span>Compiling...</span>';
    }

    try {
      const res = await fetch(`/api/projects/${this.projectId}/compile`, { method: 'POST' });
      const data = await res.json();

      this.currentErrors = data.errors || [];
      this.currentWarnings = data.warnings || [];
      this.lastFixes = data.fixes_applied || [];
      this.lastHealedContent = data.healed_content || null;

      // Update Error Markers on Monaco Editor
      this.updateMonacoMarkers(this.currentErrors, this.currentWarnings);

      // Handle Auto-Heal Banner
      const existingBanner = document.getElementById('heal-banner');
      if (existingBanner) existingBanner.remove();

      if (data.healed && this.lastFixes.length > 0) {
        const codePanel = document.getElementById('code-panel');
        if (codePanel) {
          const banner = document.createElement('div');
          banner.id = 'heal-banner';
          banner.className = 'heal-banner';
          banner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
              <i data-lucide="sparkles" style="width: 16px; height: 16px; color: var(--accent-emerald);"></i>
              <span><strong>Auto-Repaired:</strong> ${this.lastFixes.length} syntax bug(s) fixed to generate PDF.</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <button class="btn btn-primary btn-sm" onclick="window.editorApp.applyHealedCode()">
                <i data-lucide="check" style="width: 14px; height: 14px;"></i> Apply Fixes to Code
              </button>
              <button class="sidebar-btn" onclick="this.parentElement.parentElement.remove()" title="Dismiss">
                <i data-lucide="x" style="width: 14px; height: 14px;"></i>
              </button>
            </div>
          `;
          codePanel.insertBefore(banner, codePanel.children[1]);
          if (window.lucide) lucide.createIcons();
        }
      }

      // Update status indicators
      const errorCountEl = document.getElementById('error-count-badge');
      if (errorCountEl) {
        if (data.healed) {
          errorCountEl.innerText = `${this.lastFixes.length} auto-fixed`;
          errorCountEl.className = 'badge badge-emerald';
          errorCountEl.style.background = 'rgba(16, 185, 129, 0.2)';
          errorCountEl.style.color = '#34d399';
        } else if (this.currentErrors.length > 0) {
          errorCountEl.innerText = `${this.currentErrors.length} errors`;
          errorCountEl.className = 'badge badge-amber';
          errorCountEl.style.background = 'rgba(244, 63, 94, 0.2)';
          errorCountEl.style.color = '#fb7185';
        } else {
          errorCountEl.innerText = '0 errors';
          errorCountEl.className = 'badge badge-emerald';
          errorCountEl.style.background = 'rgba(16, 185, 129, 0.15)';
          errorCountEl.style.color = '#34d399';
        }
      }

      if (data.success && data.pdf_url) {
        this.pdfViewer.loadPDF(data.pdf_url);
        if (statusCompileEl) {
          const healText = data.healed ? ' (Auto-Healed)' : '';
          statusCompileEl.innerHTML = `<div class="pulse-dot"></div> <span>Compiled in ${data.duration_ms}ms${healText}</span>`;
        }
      } else {
        const firstErr = this.currentErrors[0] ? this.currentErrors[0].message : 'Compilation failed';
        this.pdfViewer.showError(firstErr);
        if (statusCompileEl) {
          statusCompileEl.innerHTML = `<div class="pulse-dot" style="background: #fb7185;"></div> <span style="color: #fb7185;">Compile failed</span>`;
        }
      }

      // Update logs drawer
      this.renderLogs(data);

    } catch (err) {
      this.pdfViewer.showError(err.message);
    } finally {
      this.isCompiling = false;
      if (compileBtn) {
        compileBtn.classList.remove('compiling');
        compileBtn.innerHTML = '<i data-lucide="play" style="width: 15px; height: 15px; fill: white;"></i> <span>Recompile</span>';
        if (window.lucide) lucide.createIcons();
      }
    }
  }

  // Monaco Error / Warning Squiggles
  updateMonacoMarkers(errors, warnings) {
    if (!window.monaco || !this.editor) return;
    const model = this.editor.getModel();
    if (!model) return;

    const markers = [];

    errors.forEach(err => {
      const line = Math.max(1, Math.min(err.line || 1, model.getLineCount()));
      markers.push({
        severity: monaco.MarkerSeverity.Error,
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: model.getLineMaxColumn(line),
        message: err.message
      });
    });

    warnings.forEach(warn => {
      const line = Math.max(1, Math.min(warn.line || 1, model.getLineCount()));
      markers.push({
        severity: monaco.MarkerSeverity.Warning,
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: model.getLineMaxColumn(line),
        message: warn.message
      });
    });

    monaco.editor.setModelMarkers(model, 'latex', markers);
  }

  // Logs & Error Drawer
  renderLogs(data) {
    const errorListEl = document.getElementById('log-error-list');
    const fixesListEl = document.getElementById('log-fixes-list');
    const rawLogEl = document.getElementById('log-raw-content');

    if (rawLogEl) {
      rawLogEl.innerText = data.raw_log || 'No compiler output.';
    }

    // Render Auto-Fixes List
    if (fixesListEl) {
      fixesListEl.innerHTML = '';
      if (this.lastFixes.length === 0) {
        fixesListEl.innerHTML = `
          <div style="color: #94a3b8; display: flex; align-items: center; gap: 8px; padding: 12px 0;">
            <i data-lucide="info" style="width: 16px; height: 16px;"></i>
            <span>No auto-fixes were required for this build.</span>
          </div>
        `;
      } else {
        this.lastFixes.forEach(fix => {
          const card = document.createElement('div');
          card.className = 'heal-card';
          card.innerHTML = `
            <div class="heal-card-header">
              <i data-lucide="sparkles" style="width: 15px; height: 15px;"></i>
              <span>Line ${fix.line}: ${fix.message}</span>
            </div>
            ${fix.original ? `<div class="heal-card-snippet" style="color: #fb7185;">- ${this.escapeHtml(fix.original)}</div>` : ''}
            ${fix.fixed ? `<div class="heal-card-snippet" style="color: #34d399;">+ ${this.escapeHtml(fix.fixed)}</div>` : ''}
          `;
          card.onclick = () => {
            if (this.editor && fix.line) {
              this.editor.revealLineInCenter(fix.line);
              this.editor.setPosition({ lineNumber: fix.line, column: 1 });
              this.editor.focus();
            }
          };
          fixesListEl.appendChild(card);
        });
      }
    }

    // Render Errors List
    if (errorListEl) {
      errorListEl.innerHTML = '';
      if (this.currentErrors.length === 0 && this.currentWarnings.length === 0) {
        errorListEl.innerHTML = `
          <div style="color: #34d399; display: flex; align-items: center; gap: 8px; padding: 12px 0;">
            <i data-lucide="check-circle" style="width: 18px; height: 18px;"></i>
            <span>Clean build! No errors or warnings found.</span>
          </div>
        `;
      } else {
        this.currentErrors.forEach(err => {
          const card = document.createElement('div');
          card.className = 'error-card';
          card.innerHTML = `
            <div class="error-card-header">
              <i data-lucide="alert-triangle" style="width: 16px; height: 16px;"></i>
              <span>Line ${err.line}: ${err.message}</span>
            </div>
            ${err.context ? `<div class="error-card-snippet"><code>${this.escapeHtml(err.context)}</code></div>` : ''}
          `;
          card.onclick = () => {
            if (this.editor && err.line) {
              this.editor.revealLineInCenter(err.line);
              this.editor.setPosition({ lineNumber: err.line, column: 1 });
              this.editor.focus();
            }
          };
          errorListEl.appendChild(card);
        });
      }
    }

    if (window.lucide) lucide.createIcons();
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  toggleLogDrawer(forceState) {
    const drawer = document.getElementById('log-drawer');
    if (!drawer) return;
    if (typeof forceState === 'boolean') {
      drawer.classList.toggle('open', forceState);
    } else {
      drawer.classList.toggle('open');
    }
  }

  toggleAutoCompile() {
    this.autoCompileEnabled = !this.autoCompileEnabled;
    const toggleEl = document.getElementById('auto-compile-toggle');
    if (toggleEl) {
      toggleEl.classList.toggle('active', this.autoCompileEnabled);
    }
    showToast(this.autoCompileEnabled ? 'Auto-compile enabled' : 'Auto-compile paused', 'info');
  }

  async createNewFile(filename) {
    if (!filename) return;
    try {
      const res = await fetch(`/api/projects/${this.projectId}/files`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename, content: '' })
      });
      const data = await res.json();
      if (data.success) {
        showToast(`Created ${filename}`, 'success');
        await this.loadProjectFiles();
        this.switchActiveFile(filename);
      } else {
        showToast(data.detail || 'Failed to create file', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async deleteFile(filename) {
    if (!confirm(`Are you sure you want to delete '${filename}'?`)) return;
    try {
      const res = await fetch(`/api/projects/${this.projectId}/files/${filename}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast(`Deleted ${filename}`, 'info');
        if (this.activeFile === filename) {
          this.activeFile = this.mainFile;
        }
        await this.loadProjectFiles();
        this.switchActiveFile(this.mainFile);
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async uploadFile(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`/api/projects/${this.projectId}/files/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        showToast(`Uploaded ${data.file.filename}`, 'success');
        await this.loadProjectFiles();
      } else {
        showToast(data.detail || 'Upload failed', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      fileInput.value = '';
    }
  }

  async updateProjectTitle(newTitle) {
    if (!newTitle.trim()) return;
    try {
      await fetch(`/api/projects/${this.projectId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle.trim() })
      });
      showToast('Project renamed', 'success');
    } catch (err) {
      console.error(err);
    }
  }

  setupEventListeners() {
    // Project Title Edit
    const titleInput = document.getElementById('project-title-input');
    if (titleInput) {
      titleInput.addEventListener('blur', () => this.updateProjectTitle(titleInput.value));
      titleInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') titleInput.blur();
      });
    }

    // Auto-compile toggle button
    const autoToggle = document.getElementById('auto-compile-toggle');
    if (autoToggle) {
      autoToggle.onclick = () => this.toggleAutoCompile();
    }

    // Recompile button
    const compileBtn = document.getElementById('btn-compile');
    if (compileBtn) {
      compileBtn.onclick = () => {
        this.saveActiveFile().then(() => this.compile());
      };
    }

    // Auto-Fix button
    const autoFixBtn = document.getElementById('btn-autofix');
    if (autoFixBtn) {
      autoFixBtn.onclick = () => this.autoFixCode();
    }

    // Zoom Buttons
    const zoomInBtn = document.getElementById('btn-zoom-in');
    const zoomOutBtn = document.getElementById('btn-zoom-out');
    const zoomResetBtn = document.getElementById('btn-zoom-reset');
    if (zoomInBtn) zoomInBtn.onclick = () => this.pdfViewer.setZoom(15);
    if (zoomOutBtn) zoomOutBtn.onclick = () => this.pdfViewer.setZoom(-15);
    if (zoomResetBtn) zoomResetBtn.onclick = () => this.pdfViewer.resetZoom();

    // Logs Drawer Toggle
    const logToggleBtn = document.getElementById('btn-toggle-logs');
    const logCloseBtn = document.getElementById('btn-close-logs');
    if (logToggleBtn) logToggleBtn.onclick = () => this.toggleLogDrawer();
    if (logCloseBtn) logCloseBtn.onclick = () => this.toggleLogDrawer(false);

    // Logs Tab Switchers
    const tabErrorsBtn = document.getElementById('tab-errors-btn');
    const tabFixesBtn = document.getElementById('tab-fixes-btn');
    const tabRawBtn = document.getElementById('tab-raw-btn');
    const errorListEl = document.getElementById('log-error-list');
    const fixesListEl = document.getElementById('log-fixes-list');
    const rawLogEl = document.getElementById('log-raw-content');

    const switchLogTab = (activeTab, showEl) => {
      [tabErrorsBtn, tabFixesBtn, tabRawBtn].forEach(b => b && b.classList.remove('active'));
      [errorListEl, fixesListEl, rawLogEl].forEach(e => e && (e.style.display = 'none'));
      if (activeTab) activeTab.classList.add('active');
      if (showEl) showEl.style.display = 'block';
    };

    if (tabErrorsBtn) tabErrorsBtn.onclick = () => switchLogTab(tabErrorsBtn, errorListEl);
    if (tabFixesBtn) tabFixesBtn.onclick = () => switchLogTab(tabFixesBtn, fixesListEl);
    if (tabRawBtn) tabRawBtn.onclick = () => switchLogTab(tabRawBtn, rawLogEl);

    // Download PDF Button
    const downloadPdfBtn = document.getElementById('btn-download-pdf');
    if (downloadPdfBtn) {
      downloadPdfBtn.onclick = () => {
        window.open(`/api/projects/${this.projectId}/download-pdf`, '_blank');
      };
    }

    // Export ZIP Button
    const exportZipBtn = document.getElementById('btn-export-zip');
    if (exportZipBtn) {
      exportZipBtn.onclick = () => {
        window.location.href = `/api/projects/${this.projectId}/export-zip`;
      };
    }

    // Upload Asset Button
    const fileInput = document.getElementById('file-upload-input');
    const uploadBtn = document.getElementById('btn-upload-file');
    if (uploadBtn && fileInput) {
      uploadBtn.onclick = () => fileInput.click();
      fileInput.onchange = () => this.uploadFile(fileInput);
    }

    // New File Button
    const newFileBtn = document.getElementById('btn-new-file');
    if (newFileBtn) {
      newFileBtn.onclick = () => {
        const fname = prompt('Enter new filename (e.g. chapter1.tex, data.bib):');
        if (fname) this.createNewFile(fname.trim());
      };
    }
  }
}
