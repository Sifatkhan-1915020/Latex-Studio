// Dashboard Controller

class DashboardApp {
  constructor() {
    this.projects = [];
    this.selectedTemplate = 'blank';
    this.init();
  }

  init() {
    this.loadProjects();
    this.setupEventListeners();
  }

  async loadProjects(searchQuery = '', sortOrder = 'updated_desc') {
    const listContainer = document.getElementById('projects-container');
    if (!listContainer) return;

    try {
      const url = `/api/projects?sort=${sortOrder}${searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : ''}`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.success) {
        this.projects = data.projects;
        this.renderProjects();
      }
    } catch (err) {
      console.error(err);
    }
  }

  renderProjects() {
    const container = document.getElementById('projects-container');
    if (!container) return;

    if (this.projects.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">
            <i data-lucide="folder-plus" style="width: 32px; height: 32px;"></i>
          </div>
          <h3>No Projects Found</h3>
          <p>Create your first LaTeX document by selecting a template above or clicking New Project.</p>
          <button class="btn btn-primary" onclick="dashboardApp.openCreateModal('blank')">
            <i data-lucide="plus" style="width: 16px; height: 16px;"></i> Create Project
          </button>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    container.innerHTML = '';
    this.projects.forEach(p => {
      const card = document.createElement('div');
      card.className = 'project-card';
      
      const createdDate = new Date(p.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
      const updatedDate = new Date(p.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });

      card.innerHTML = `
        <div>
          <div class="project-card-header">
            <div>
              <div class="project-card-title">${this.escapeHtml(p.title)}</div>
              <div class="project-card-desc">${this.escapeHtml(p.description || 'No description')}</div>
            </div>
            <span class="badge badge-emerald">${p.template}</span>
          </div>
        </div>

        <div class="project-card-footer">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i data-lucide="file-text" style="width: 14px; height: 14px;"></i>
            <span>${p.file_count || 1} files</span>
            <span>•</span>
            <span>${updatedDate}</span>
          </div>

          <div style="display: flex; align-items: center; gap: 4px;" onclick="event.stopPropagation();">
            <button class="project-menu-btn" title="Duplicate Project" onclick="dashboardApp.duplicateProject('${p.id}')">
              <i data-lucide="copy" style="width: 14px; height: 14px;"></i>
            </button>
            <button class="project-menu-btn" title="Export ZIP" onclick="dashboardApp.exportZip('${p.id}')">
              <i data-lucide="download" style="width: 14px; height: 14px;"></i>
            </button>
            <button class="project-menu-btn" title="Delete Project" onclick="dashboardApp.deleteProject('${p.id}', '${this.escapeHtml(p.title)}')">
              <i data-lucide="trash-2" style="width: 14px; height: 14px; color: #fb7185;"></i>
            </button>
          </div>
        </div>
      `;

      card.onclick = () => {
        window.location.href = `/project/${p.id}`;
      };

      container.appendChild(card);
    });

    if (window.lucide) lucide.createIcons();
  }

  openCreateModal(templateId = 'blank') {
    this.selectedTemplate = templateId;
    const modal = document.getElementById('new-project-modal');
    const tplSelect = document.getElementById('modal-template-select');
    const titleInput = document.getElementById('modal-project-title');
    
    if (tplSelect) tplSelect.value = templateId;
    if (titleInput) {
      const tplNames = {
        blank: 'Untitled Document',
        research_paper: 'Deep Learning Research Paper',
        cv_resume: 'My Curriculum Vitae',
        beamer_slides: 'Research Presentation Deck',
        lab_report: 'Laboratory Technical Report'
      };
      titleInput.value = tplNames[templateId] || 'New LaTeX Document';
      setTimeout(() => titleInput.focus(), 100);
    }

    if (modal) modal.classList.add('active');
  }

  closeCreateModal() {
    const modal = document.getElementById('new-project-modal');
    if (modal) modal.classList.remove('active');
  }

  async handleCreateProject(e) {
    e.preventDefault();
    const titleInput = document.getElementById('modal-project-title');
    const descInput = document.getElementById('modal-project-desc');
    const tplSelect = document.getElementById('modal-template-select');

    const title = titleInput ? titleInput.value.trim() : 'Untitled';
    const description = descInput ? descInput.value.trim() : '';
    const template = tplSelect ? tplSelect.value : 'blank';

    if (!title) {
      showToast('Please enter a project title', 'error');
      return;
    }

    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, template })
      });
      const data = await res.json();
      if (data.success) {
        this.closeCreateModal();
        showToast('Project created! Opening editor...', 'success');
        setTimeout(() => {
          window.location.href = `/project/${data.project.id}`;
        }, 500);
      } else {
        showToast(data.detail || 'Failed to create project', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async duplicateProject(projectId) {
    try {
      const res = await fetch(`/api/projects/${projectId}/duplicate`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast('Project duplicated', 'success');
        this.loadProjects();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  exportZip(projectId) {
    window.location.href = `/api/projects/${projectId}/export-zip`;
  }

  async deleteProject(projectId, title) {
    if (!confirm(`Are you sure you want to delete "${title}"? This cannot be undone.`)) return;
    try {
      const res = await fetch(`/api/projects/${projectId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        showToast('Project deleted', 'info');
        this.loadProjects();
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    let debounceTimer;
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          const sortSelect = document.getElementById('sort-select');
          this.loadProjects(e.target.value, sortSelect ? sortSelect.value : 'updated_desc');
        }, 300);
      });
    }

    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        const sVal = searchInput ? searchInput.value : '';
        this.loadProjects(sVal, e.target.value);
      });
    }
  }
}
