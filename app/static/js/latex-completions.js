// Overleaf LaTeX Autocompletions & Snippets Catalog for Monaco Editor

window.LaTeXCompletions = (function () {
  const snippets = [
    // Environments
    {
      label: '\\begin{equation}',
      insertText: '\\begin{equation}\n\t${1:E = mc^2}\n\\end{equation}',
      documentation: 'Numbered mathematical equation environment'
    },
    {
      label: '\\begin{align}',
      insertText: '\\begin{align}\n\t${1:a} &= ${2:b} \\\\\n\t${3:c} &= ${4:d}\n\\end{align}',
      documentation: 'Multi-line aligned mathematical equations'
    },
    {
      label: '\\begin{figure}',
      insertText: '\\begin{figure}[htbp]\n\t\\centering\n\t\\includegraphics[width=${1:0.8}\\textwidth]{${2:image.png}}\n\t\\caption{${3:Caption text}}\n\t\\label{fig:${4:label}}\n\\end{figure}',
      documentation: 'Floating figure environment with image inclusion and caption'
    },
    {
      label: '\\begin{table}',
      insertText: '\\begin{table}[htbp]\n\t\\centering\n\t\\caption{${1:Table caption}}\n\t\\label{tab:${2:label}}\n\t\\begin{tabular}{${3:lcc}}\n\t\t\\toprule\n\t\t${4:Col 1} & ${5:Col 2} & ${6:Col 3} \\\\\n\t\t\\midrule\n\t\t${7:A} & ${8:B} & ${9:C} \\\\\n\t\t\\bottomrule\n\t\\end{tabular}\n\\end{table}',
      documentation: 'Standard floating table with booktabs formatting'
    },
    {
      label: '\\begin{itemize}',
      insertText: '\\begin{itemize}\n\t\\item ${1:First item}\n\t\\item ${2:Second item}\n\\end{itemize}',
      documentation: 'Unordered bulleted list environment'
    },
    {
      label: '\\begin{enumerate}',
      insertText: '\\begin{enumerate}\n\t\\item ${1:First item}\n\t\\item ${2:Second item}\n\\end{enumerate}',
      documentation: 'Numbered ordered list environment'
    },
    {
      label: '\\begin{matrix}',
      insertText: '\\begin{matrix}\n\t${1:a} & ${2:b} \\\\\n\t${3:c} & ${4:d}\n\\end{matrix}',
      documentation: 'Plain mathematical matrix'
    },
    {
      label: '\\begin{pmatrix}',
      insertText: '\\begin{pmatrix}\n\t${1:a} & ${2:b} \\\\\n\t${3:c} & ${4:d}\n\\end{pmatrix}',
      documentation: 'Parenthesized matrix ( )'
    },
    {
      label: '\\begin{bmatrix}',
      insertText: '\\begin{bmatrix}\n\t${1:a} & ${2:b} \\\\\n\t${3:c} & ${4:d}\n\\end{bmatrix}',
      documentation: 'Bracketed matrix [ ]'
    },
    {
      label: '\\begin{cases}',
      insertText: '\\begin{cases}\n\t${1:expression_1}, & \\text{if } ${2:condition_1} \\\\\n\t${3:expression_2}, & \\text{otherwise}\n\\end{cases}',
      documentation: 'Piecewise defined mathematical cases'
    },
    {
      label: '\\begin{theorem}',
      insertText: '\\begin{theorem}[${1:Title}]\n\t${2:Theorem statement here.}\n\\end{theorem}',
      documentation: 'Theorem environment'
    },
    {
      label: '\\begin{proof}',
      insertText: '\\begin{proof}\n\t${1:Proof content here.}\n\\end{proof}',
      documentation: 'Mathematical proof environment with Q.E.D. box'
    },
    {
      label: '\\begin{abstract}',
      insertText: '\\begin{abstract}\n\t${1:Abstract summary goes here.}\n\\end{abstract}',
      documentation: 'Document abstract section'
    },
    {
      label: '\\begin{frame}',
      insertText: '\\begin{frame}{${1:Slide Title}}\n\t\\begin{itemize}\n\t\t\\item ${2:Key point}\n\t\\end{itemize}\n\\end{frame}',
      documentation: 'Beamer presentation slide frame'
    },

    // Document Structure & Formatting
    { label: '\\section{}', insertText: '\\section{${1:Section Title}}\n\\label{sec:${2:label}}', documentation: 'Top-level numbered section' },
    { label: '\\subsection{}', insertText: '\\subsection{${1:Subsection Title}}\n\\label{subsec:${2:label}}', documentation: 'Second-level subsection' },
    { label: '\\subsubsection{}', insertText: '\\subsubsection{${1:Subsubsection Title}}', documentation: 'Third-level subsubsection' },
    { label: '\\paragraph{}', insertText: '\\paragraph{${1:Paragraph Title}} ${2:Content}', documentation: 'Inline paragraph heading' },

    // Text Styles
    { label: '\\textbf{}', insertText: '\\textbf{${1:bold text}}', documentation: 'Bold typeface' },
    { label: '\\textit{}', insertText: '\\textit{${1:italic text}}', documentation: 'Italic typeface' },
    { label: '\\texttt{}', insertText: '\\texttt{${1:monospace text}}', documentation: 'Monospace / typewriter font' },
    { label: '\\underline{}', insertText: '\\underline{${1:underlined text}}', documentation: 'Underlined text' },
    { label: '\\emph{}', insertText: '\\emph{${1:emphasized text}}', documentation: 'Emphasized text' },

    // Math Functions & Symbols
    { label: '\\frac{}{}', insertText: '\\frac{${1:numerator}}{${2:denominator}}', documentation: 'Fraction: a/b' },
    { label: '\\sqrt{}', insertText: '\\sqrt{${1:x}}', documentation: 'Square root radical' },
    { label: '\\sqrt[]{}', insertText: '\\sqrt[${1:n}]{${2:x}}', documentation: 'N-th root radical' },
    { label: '\\sum_{}^{}', insertText: '\\sum_{${1:i=1}}^{${2:n}} ${3:x_i}', documentation: 'Summation operator with lower and upper limits' },
    { label: '\\prod_{}^{}', insertText: '\\prod_{${1:i=1}}^{${2:n}} ${3:x_i}', documentation: 'Product operator with lower and upper limits' },
    { label: '\\int_{}^{}', insertText: '\\int_{${1:a}}^{${2:b}} ${3:f(x)} \\, dx', documentation: 'Definite integral' },
    { label: '\\lim_{}', insertText: '\\lim_{${1:x \\to 0}} ${2:f(x)}', documentation: 'Limit operator' },

    // Delimiters
    { label: '\\left( \\right)', insertText: '\\left( ${1:expression} \\right)', documentation: 'Auto-sizing round parentheses' },
    { label: '\\left[ \\right]', insertText: '\\left[ ${1:expression} \\right]', documentation: 'Auto-sizing square brackets' },
    { label: '\\left\\{ \\right\\}', insertText: '\\left\\{ ${1:expression} \\right\\}', documentation: 'Auto-sizing curly braces' },

    // Greek Alphabet
    { label: '\\alpha', insertText: '\\alpha', documentation: 'Greek letter alpha (α)' },
    { label: '\\beta', insertText: '\\beta', documentation: 'Greek letter beta (β)' },
    { label: '\\gamma', insertText: '\\gamma', documentation: 'Greek letter gamma (γ)' },
    { label: '\\delta', insertText: '\\delta', documentation: 'Greek letter delta (δ)' },
    { label: '\\epsilon', insertText: '\\epsilon', documentation: 'Greek letter epsilon (ε)' },
    { label: '\\zeta', insertText: '\\zeta', documentation: 'Greek letter zeta (ζ)' },
    { label: '\\eta', insertText: '\\eta', documentation: 'Greek letter eta (η)' },
    { label: '\\theta', insertText: '\\theta', documentation: 'Greek letter theta (θ)' },
    { label: '\\lambda', insertText: '\\lambda', documentation: 'Greek letter lambda (λ)' },
    { label: '\\mu', insertText: '\\mu', documentation: 'Greek letter mu (μ)' },
    { label: '\\nu', insertText: '\\nu', documentation: 'Greek letter nu (ν)' },
    { label: '\\xi', insertText: '\\xi', documentation: 'Greek letter xi (ξ)' },
    { label: '\\pi', insertText: '\\pi', documentation: 'Greek letter pi (π)' },
    { label: '\\rho', insertText: '\\rho', documentation: 'Greek letter rho (ρ)' },
    { label: '\\sigma', insertText: '\\sigma', documentation: 'Greek letter sigma (σ)' },
    { label: '\\tau', insertText: '\\tau', documentation: 'Greek letter tau (τ)' },
    { label: '\\phi', insertText: '\\phi', documentation: 'Greek letter phi (φ)' },
    { label: '\\chi', insertText: '\\chi', documentation: 'Greek letter chi (χ)' },
    { label: '\\psi', insertText: '\\psi', documentation: 'Greek letter psi (ψ)' },
    { label: '\\omega', insertText: '\\omega', documentation: 'Greek letter omega (ω)' },

    // Capital Greek
    { label: '\\Gamma', insertText: '\\Gamma', documentation: 'Greek capital Gamma (Γ)' },
    { label: '\\Delta', insertText: '\\Delta', documentation: 'Greek capital Delta (Δ)' },
    { label: '\\Theta', insertText: '\\Theta', documentation: 'Greek capital Theta (Θ)' },
    { label: '\\Lambda', insertText: '\\Lambda', documentation: 'Greek capital Lambda (Λ)' },
    { label: '\\Sigma', insertText: '\\Sigma', documentation: 'Greek capital Sigma (Σ)' },
    { label: '\\Phi', insertText: '\\Phi', documentation: 'Greek capital Phi (Φ)' },
    { label: '\\Psi', insertText: '\\Psi', documentation: 'Greek capital Psi (Ψ)' },
    { label: '\\Omega', insertText: '\\Omega', documentation: 'Greek capital Omega (Ω)' },

    // Math Operators & Relations
    { label: '\\times', insertText: '\\times', documentation: 'Multiplication cross (×)' },
    { label: '\\cdot', insertText: '\\cdot', documentation: 'Multiplication center dot (·)' },
    { label: '\\div', insertText: '\\div', documentation: 'Division symbol (÷)' },
    { label: '\\pm', insertText: '\\pm', documentation: 'Plus-minus sign (±)' },
    { label: '\\leq', insertText: '\\leq', documentation: 'Less than or equal (≤)' },
    { label: '\\geq', insertText: '\\geq', documentation: 'Greater than or equal (≥)' },
    { label: '\\neq', insertText: '\\neq', documentation: 'Not equal (≠)' },
    { label: '\\approx', insertText: '\\approx', documentation: 'Approximately equal (≈)' },
    { label: '\\equiv', insertText: '\\equiv', documentation: 'Identical / equivalent to (≡)' },
    { label: '\\infty', insertText: '\\infty', documentation: 'Infinity symbol (∞)' },
    { label: '\\partial', insertText: '\\partial', documentation: 'Partial derivative symbol (∂)' },
    { label: '\\nabla', insertText: '\\nabla', documentation: 'Del / Nabla vector operator (∇)' },
    { label: '\\in', insertText: '\\in', documentation: 'Element of set (∈)' },
    { label: '\\notin', insertText: '\\notin', documentation: 'Not element of set (∉)' },
    { label: '\\subset', insertText: '\\subset', documentation: 'Subset of (⊂)' },
    { label: '\\subseteq', insertText: '\\subseteq', documentation: 'Subset or equal (⊆)' },
    { label: '\\cup', insertText: '\\cup', documentation: 'Set union (∪)' },
    { label: '\\cap', insertText: '\\cap', documentation: 'Set intersection (∩)' },
    { label: '\\forall', insertText: '\\forall', documentation: 'Universal quantifier (∀)' },
    { label: '\\exists', insertText: '\\exists', documentation: 'Existential quantifier (∃)' },
    { label: '\\rightarrow', insertText: '\\rightarrow', documentation: 'Right arrow (→)' },
    { label: '\\Rightarrow', insertText: '\\Rightarrow', documentation: 'Right double implication arrow (⇒)' },
    { label: '\\iff', insertText: '\\iff', documentation: 'If and only if arrow (⟺)' },
    { label: '\\mathbb{}', insertText: '\\mathbb{${1:R}}', documentation: 'Blackboard bold font (ℝ, ℂ, ℕ, ℤ)' },
    { label: '\\mathcal{}', insertText: '\\mathcal{${1:L}}', documentation: 'Calligraphic mathematical font' },

    // References & Citations
    { label: '\\label{}', insertText: '\\label{${1:key}}', documentation: 'Define cross-reference label' },
    { label: '\\ref{}', insertText: '\\ref{${1:key}}', documentation: 'Insert cross-reference to label' },
    { label: '\\eqref{}', insertText: '\\eqref{${1:eq_key}}', documentation: 'Insert parenthesized equation reference' },
    { label: '\\cite{}', insertText: '\\cite{${1:bib_key}}', documentation: 'Insert bibliographic citation' },
    { label: '\\bibliography{}', insertText: '\\bibliography{${1:references}}', documentation: 'Include BibTeX database' },
    { label: '\\bibliographystyle{}', insertText: '\\bibliographystyle{${1:plain}}', documentation: 'Set bibliography formatting style' }
  ];

  function registerProvider(monaco, getProjectFilesCallback) {
    monaco.languages.registerCompletionItemProvider('latex', {
      triggerCharacters: ['\\', '{', ':', '@'],
      provideCompletionItems: function (model, position) {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });

        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn
        };

        const suggestions = [];

        // Check if user is typing a \cite{...}
        if (/\\cite\{[^}]*$/.test(textUntilPosition)) {
          const files = getProjectFilesCallback ? getProjectFilesCallback() : [];
          // Scan bib files for citation keys
          files.filter(f => f.filename.endsWith('.bib')).forEach(f => {
            if (f.content) {
              const bibRegex = /@\w+\s*\{\s*([^,\s]+)/g;
              let match;
              while ((match = bibRegex.exec(f.content)) !== null) {
                suggestions.push({
                  label: match[1],
                  kind: monaco.languages.CompletionItemKind.Reference,
                  insertText: match[1],
                  detail: `BibTeX entry from ${f.filename}`,
                  range: range
                });
              }
            }
          });
          if (suggestions.length > 0) {
            return { suggestions: suggestions };
          }
        }

        // Check if user is typing a \ref{...} or \eqref{...}
        if (/\\(eq)?ref\{[^}]*$/.test(textUntilPosition)) {
          const allText = model.getValue();
          const labelRegex = /\\label\{([^}]+)\}/g;
          let match;
          while ((match = labelRegex.exec(allText)) !== null) {
            suggestions.push({
              label: match[1],
              kind: monaco.languages.CompletionItemKind.Reference,
              insertText: match[1],
              detail: 'Document label',
              range: range
            });
          }
          if (suggestions.length > 0) {
            return { suggestions: suggestions };
          }
        }

        // Standard LaTeX snippets and commands
        snippets.forEach(s => {
          suggestions.push({
            label: s.label,
            kind: s.label.startsWith('\\begin') ? monaco.languages.CompletionItemKind.Snippet : monaco.languages.CompletionItemKind.Function,
            insertText: s.insertText,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: s.documentation,
            range: range
          });
        });

        return { suggestions: suggestions };
      }
    });
  }

  return {
    registerProvider: registerProvider,
    snippets: snippets
  };
})();
