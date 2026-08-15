// PDF Viewer Controller

class PDFViewerController {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.iframe = null;
    this.currentUrl = null;
    this.zoomLevel = 100;
  }

  loadPDF(pdfUrl) {
    if (!this.container) return;

    this.currentUrl = pdfUrl;
    // Add cache busting timestamp and PDF view params
    const viewerUrl = `${pdfUrl}#toolbar=0&navpanes=0&scrollbar=1&zoom=${this.zoomLevel}`;

    if (!this.iframe) {
      this.container.innerHTML = '';
      this.iframe = document.createElement('iframe');
      this.iframe.className = 'pdf-iframe';
      this.iframe.src = viewerUrl;
      this.container.appendChild(this.iframe);
    } else {
      this.iframe.src = viewerUrl;
    }
  }

  showError(message) {
    if (!this.container) return;
    this.container.innerHTML = `
      <div class="pdf-placeholder">
        <div style="width: 48px; height: 48px; border-radius: 50%; background: rgba(244, 63, 94, 0.15); color: #fb7185; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
          <i data-lucide="alert-circle" style="width: 24px; height: 24px;"></i>
        </div>
        <h4 style="font-size: 15px; font-weight: 600; color: #f8fafc;">Compilation Error</h4>
        <p style="font-size: 12.5px; color: #94a3b8; max-width: 320px;">${message || 'Please fix the LaTeX errors shown in the bottom log panel.'}</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    this.iframe = null;
  }

  setZoom(delta) {
    this.zoomLevel = Math.max(50, Math.min(250, this.zoomLevel + delta));
    const zoomText = document.getElementById('zoom-display');
    if (zoomText) zoomText.innerText = `${this.zoomLevel}%`;

    if (this.currentUrl && this.iframe) {
      this.iframe.src = `${this.currentUrl}#toolbar=0&navpanes=0&zoom=${this.zoomLevel}`;
    }
  }

  resetZoom() {
    this.zoomLevel = 100;
    const zoomText = document.getElementById('zoom-display');
    if (zoomText) zoomText.innerText = `100%`;
    if (this.currentUrl && this.iframe) {
      this.iframe.src = `${this.currentUrl}#toolbar=0&navpanes=0&zoom=100`;
    }
  }
}
