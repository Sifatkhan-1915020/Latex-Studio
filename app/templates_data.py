TEMPLATES = {
    "blank": {
        "id": "blank",
        "name": "Blank Document",
        "category": "Basic",
        "description": "Minimal clean starter document with amsmath and geometry.",
        "icon": "file-text",
        "files": {
            "main.tex": r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=cyan}

\title{\textbf{My First LaTeX Document}}
\author{Your Name}
\date{\today}

\begin{document}

\maketitle

\section{Introduction}
Welcome to your new LaTeX project! You can start editing this document right away.

\section{Mathematics}
LaTeX makes mathematical typesetting intuitive and beautiful. Here is Euler's identity:
\begin{equation}
e^{i\pi} + 1 = 0
\end{equation}

And a Gaussian integral:
\begin{equation}
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
\end{equation}

\section{Lists}
\begin{itemize}
    \item Real-time side-by-side PDF preview
    \item Full autocompletion for LaTeX commands
    \item Fast compilation powered by Python \& Tectonic
\end{itemize}

\end{document}
"""
        }
    },
    "research_paper": {
        "id": "research_paper",
        "name": "Academic Research Paper",
        "category": "Academic",
        "description": "Two-column IEEE/ACM-style research paper with equations, tables, and bibliography.",
        "icon": "book-open",
        "files": {
            "main.tex": r"""\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{cite}
\usepackage{geometry}
\geometry{top=0.75in,bottom=0.75in,left=0.75in,right=0.75in}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=cyan}

\title{\textbf{Deep Learning Architectures for Real-Time Neural Reasoning}}
\author{
    \textbf{Alex Johnson}$^1$, \textbf{Elena Rostova}$^2$, \textbf{Marcus Vance}$^1$ \\
    $^1$Department of Computer Science, Stanford University \\
    $^2$Department of Mathematics, MIT \\
    \texttt{\{alexj, mvance\}@stanford.edu, elenar@mit.edu}
}
\date{}

\begin{document}

\maketitle

\begin{abstract}
Recent advances in deep representation learning have enabled autonomous reasoning systems to achieve superhuman benchmark accuracy. In this work, we propose a novel gradient-guided latent routing mechanism that optimizes compute efficiency across multi-modal transformers. Our empirical evaluations across four standard reasoning benchmarks demonstrate a 24.3\% latency reduction with zero accuracy degradation compared to state-of-the-art baselines.
\end{abstract}

\section{Introduction}
Large-scale artificial intelligence models have transformed modern natural language understanding and automated theorem proving~\cite{vaswani2017attention}. However, scaling inference compute while maintaining latency bounds remains a formidable challenge.

In this paper, we formulate a dynamic latent space trajectory optimization scheme:
\begin{equation}
\label{eq:objective}
\mathcal{L}(\theta) = \mathbb{E}_{(x,y)\sim \mathcal{D}} \left[ \ell(f_\theta(x), y) + \lambda \sum_{l=1}^L \|\Omega_l(x)\|_2^2 \right]
\end{equation}
where $\Omega_l(x)$ represents the sparse token routing penalty at layer $l$, and $\lambda \in [0, 1]$ is a tunable regularization coefficient.

\section{Methodology}
Our architecture decomposes the sequence transformation into three synchronized stages:

\subsection{Latent Manifold Projection}
Given an input sequence $\mathbf{X} = \{x_1, x_2, \dots, x_N\} \in \mathbb{R}^{N \times d}$, the attention weight matrix $\mathbf{A}$ is computed as:
\begin{equation}
\mathbf{A} = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} + \mathbf{M}\right) \mathbf{V}
\end{equation}
where $\mathbf{M}$ is the structured attention bias matrix.

\subsection{Benchmark Performance}
Table~\ref{tab:results} summarizes the accuracy and throughput comparisons across multiple reasoning benchmarks.

\begin{table}[htbp]
\centering
\caption{Benchmark results across reasoning datasets.}
\label{tab:results}
\begin{tabular}{lccc}
\toprule
\textbf{Model} & \textbf{GSM8K (\%)} & \textbf{MATH (\%)} & \textbf{Speed (tok/s)} \\
\midrule
Baseline-7B    & 78.4 & 42.1 & 45.2 \\
Route-7B (Ours) & \textbf{86.7} & \textbf{51.8} & \textbf{72.5} \\
Baseline-70B   & 91.2 & 64.3 & 12.1 \\
Route-70B (Ours)& \textbf{93.5} & \textbf{68.9} & \textbf{19.8} \\
\bottomrule
\end{tabular}
\end{table}

\section{Conclusion}
We have introduced a gradient-guided routing paradigm for efficient neural inference. Future work will extend this framework to embodied physical systems.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
""",
            "references.bib": r"""@article{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, {\L}ukasz and Polosukhin, Illia},
  journal={Advances in Neural Information Processing Systems},
  volume={30},
  year={2017}
}

@article{lecun2015deep,
  title={Deep learning},
  author={LeCun, Yann and Bengio, Yoshua and Hinton, Geoffrey},
  journal={Nature},
  volume={521},
  number={7553},
  pages={436--444},
  year={2015}
}
"""
        }
    },
    "cv_resume": {
        "id": "cv_resume",
        "name": "Modern Professional CV",
        "category": "Resume",
        "description": "Sleek, high-impact LaTeX curriculum vitae with skill badges and timeline.",
        "icon": "user-check",
        "files": {
            "main.tex": r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{titlesec}

\definecolor{primary}{RGB}{16, 185, 129}
\definecolor{darkgray}{RGB}{30, 41, 59}
\definecolor{subtext}{RGB}{100, 116, 139}

\hypersetup{colorlinks=true, urlcolor=primary, linkcolor=primary}
\setlist[itemize]{leftmargin=1.5em, itemsep=2pt, parsep=0pt}
\pagestyle{empty}

% Section formatting
\titleformat{\section}{\Large\bfseries\color{primary}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{12pt}{6pt}

\begin{document}

% Header
\begin{center}
    {\Huge \textbf{ALEXANDER D. MERCER}}\\[4pt]
    {\large \textbf{Senior Full-Stack \& Machine Learning Engineer}}\\[6pt]
    \href{mailto:alex.mercer@example.com}{alex.mercer@example.com} $\;\bullet\;$
    +1 (555) 234-5678 $\;\bullet\;$
    \href{https://github.com}{github.com/alexmercer} $\;\bullet\;$
    San Francisco, CA
\end{center}

\vspace{-4pt}

\section{Summary}
Dynamic Lead Software Engineer with 7+ years of experience architecting high-throughput distributed systems, modern web platforms, and deep learning pipelines. Passionate about performant developer tooling, Python, FastAPI, and responsive UI engineering.

\section{Work Experience}

\textbf{Lead Cloud Architect} \hfill \textit{Jan 2022 -- Present} \\
\textit{OmniScale AI Inc.} \hfill \textit{San Francisco, CA}
\begin{itemize}
    \item Architected real-time inference microservices handling 45M+ daily requests with 99.99\% uptime.
    \item Designed an asynchronous Python/FastAPI compilation pipeline that reduced task execution times by 65\%.
    \item Mentored 12 junior and mid-level engineers across frontend and distributed systems domains.
\end{itemize}

\vspace{6pt}
\textbf{Senior Software Engineer} \hfill \textit{Aug 2019 -- Dec 2021} \\
\textit{Vector Labs} \hfill \textit{Seattle, WA}
\begin{itemize}
    \item Built end-to-end telemetry pipelines using Python, PostgreSQL, and WebSockets.
    \item Optimized frontend render cycles, slashing Time-To-Interactive from 3.2s to 680ms.
    \item Implemented automated CI/CD workflows reducing deploy turnaround to under 4 minutes.
\end{itemize}

\section{Education}
\textbf{B.S. in Computer Science \& Applied Mathematics} \hfill \textit{2015 -- 2019} \\
\textit{University of California, Berkeley} \hfill \textit{GPA: 3.92 / 4.00 (Summa Cum Laude)}

\section{Technical Skills}
\textbf{Languages:} Python, TypeScript, JavaScript, C++, Go, SQL, LaTeX, HTML5/CSS3 \\
\textbf{Frameworks \& Tools:} FastAPI, React, Vue, Uvicorn, Docker, Kubernetes, Git, PostgreSQL, Redis \\
\textbf{Specializations:} High-Performance APIs, Compilers, Distributed Systems, Web Performance

\section{Key Projects}
\textbf{FastTeX Live Engine:} Open-source web-based LaTeX editor with real-time compilation and Monaco integration. \\
\textbf{VectorSQL Engine:} Ultra-lightweight SIMD-accelerated in-memory vector indexing library.

\end{document}
"""
        }
    },
    "beamer_slides": {
        "id": "beamer_slides",
        "name": "Presentation Slides (Beamer)",
        "category": "Presentation",
        "description": "Modern presentation slides with custom theme, block callouts, and math proofs.",
        "icon": "monitor",
        "files": {
            "main.tex": r"""\documentclass[aspectratio=169,11pt]{beamer}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{hyperref}

\usetheme{Madrid}
\usecolortheme{beaver}

\title{\textbf{Next-Generation LaTeX Engine}}
\subtitle{Real-Time Compilation \& Modern Web Workspaces}
\author{Dr. Morgan Vance}
\institute{Quantum Systems Institute}
\date{\today}

\begin{document}

\begin{frame}
\titlepage
\end{frame}

\begin{frame}{Agenda \& Key Takeaways}
\tableofcontents
\end{frame}

\section{Introduction}
\begin{frame}{Why Modernize the LaTeX Workflow?}
\begin{itemize}
    \item \textbf{Instant Gratification:} Sub-second live PDF updates right in the browser.
    \item \textbf{Smart Auto-Suggestions:} Context-aware autocompletions for equations, citations, and environments.
    \item \textbf{Zero Bloat:} High-speed compilation powered by Python and Tectonic.
\end{itemize}
\end{frame}

\section{Mathematical Formulation}
\begin{frame}{Optimization Formulation}
\begin{block}{Convex Optimization Problem}
Given convex objective function $f_0(x)$ and affine equality constraints:
\begin{equation}
\begin{aligned}
\min_{x \in \mathbb{R}^n} \quad & f_0(x) \\
\text{s.t.} \quad & f_i(x) \le 0, \quad i = 1, \dots, m \\
& A x = b
\end{aligned}
\end{equation}
\end{block}

\begin{alertblock}{Key Theorem}
If Slater's condition holds, strong duality is guaranteed: $d^* = p^*$.
\end{alertblock}
\end{frame}

\section{Conclusion}
\begin{frame}{Summary \& Next Steps}
\begin{columns}
\begin{column}{0.5\textwidth}
\textbf{Key Milestones:}
\begin{enumerate}
    \item Fast local deployment
    \item Full Monaco Editor integration
    \item Multi-file project trees
\end{enumerate}
\end{column}
\begin{column}{0.5\textwidth}
\textbf{Try it out:}
\begin{itemize}
    \item Edit LaTeX in the center pane
    \item Watch real-time PDF update on the right!
\end{itemize}
\end{column}
\end{columns}
\end{frame}

\end{document}
"""
        }
    },
    "lab_report": {
        "id": "lab_report",
        "name": "Technical Lab Report",
        "category": "Report",
        "description": "Structured engineering report with title cover, methodology, and data analysis.",
        "icon": "clipboard",
        "files": {
            "main.tex": r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{booktabs}
\usepackage{fancyhdr}
\usepackage{hyperref}

\pagestyle{fancy}
\fancyhf{}
\rhead{ECE-402: Advanced Digital Systems}
\lhead{Lab Report \#3}
\cfoot{\thepage}

\title{
    \vspace{-1.5in}
    \huge \textbf{Laboratory Report \#3} \\
    \Large \textbf{Signal Processing and Spectral Analysis of Non-Stationary Waveforms}
}
\author{\textbf{Team Delta:} Jane Doe, Alex Smith, David Lee}
\date{Date of Experiment: \today}

\begin{document}

\maketitle

\hrule
\vspace{10pt}

\section*{Executive Summary}
This laboratory experiment investigates Fast Fourier Transform (FFT) algorithms applied to noisy non-stationary frequency-modulated audio signals. We observed that applying a Hann window reduced spectral leakage side-lobes by 32.4 dB relative to a rectangular window.

\section{Experimental Methodology}
A synthetic continuous-time chirp signal $x(t) = \sin(2\pi (f_0 + \frac{k}{2}t)t)$ was sampled at $F_s = 44.1\,\text{kHz}$ with parameters:
\begin{itemize}
    \item Initial frequency $f_0 = 200\,\text{Hz}$
    \item Chirp rate $k = 1200\,\text{Hz/s}$
    \item Duration $T = 2.5\,\text{seconds}$
\end{itemize}

\subsection{Discrete Fourier Transform Formulation}
The $N$-point Discrete Fourier Transform is computed as:
\begin{equation}
X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j 2\pi k n / N}, \quad k = 0, 1, \dots, N-1
\end{equation}

\section{Experimental Results}
Table~\ref{tab:snr} records the measured Signal-to-Noise Ratio (SNR) under various windowing functions.

\begin{table}[htbp]
\centering
\caption{Spectral window performance comparison.}
\label{tab:snr}
\begin{tabular}{lccc}
\toprule
\textbf{Window Type} & \textbf{Main Lobe Width (-3dB)} & \textbf{Side Lobe Attenuation (dB)} & \textbf{SNR (dB)} \\
\midrule
Rectangular & $0.89 / N$ & -13.3 & 18.2 \\
Hann        & $1.44 / N$ & -31.5 & 27.8 \\
Blackman    & $1.68 / N$ & -58.1 & 34.6 \\
\bottomrule
\end{tabular}
\end{table}

\section{Discussion \& Conclusion}
The experimental results closely align with analytical predictions. The Blackman window demonstrated the highest suppression of spurious harmonics at the cost of slight main-lobe broadening.

\end{document}
"""
        }
    }
}
