// ==========================================================================
// APP LOGIC - AGENTE HÍBRIDO GEMMA OKF (REFACTORED & COMPLETE)
// ==========================================================================

let currentView = 'private'; // 'private' vs 'public'
let currentNavSection = 'graph'; // 'graph', 'chat', 'docs'
let currentChatAgent = 'cloud'; // 'cloud', 'local', 'dual'

let networkInstance = null;
let graphifyData = null;
let googleOkfData = null;
let graphReportMDText = "";

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await fetchSystemStatus();
    await fetchDocumentsList();
    await loadKnowledgeGraph(currentView);
}

// 1. Fetch System Status Metrics
async function fetchSystemStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = val || 0;
        };

        setVal('metricTotalNodes', data.total_nodes);
        setVal('metricTotalEdges', data.total_edges);
        setVal('metricPrivateNodes', data.private_nodes);
        setVal('metricPublicNodes', data.public_nodes);
    } catch (e) {
        console.error('Error al cargar status:', e);
    }
}

// 2. Fetch Ingested Documents List
async function fetchDocumentsList() {
    const listEl = document.getElementById('documentsList');
    if (!listEl) return;

    try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        
        if (!data.documents || data.documents.length === 0) {
            listEl.innerHTML = '<div class="doc-item"><span class="doc-title">No hay archivos PDF en /documents</span></div>';
            return;
        }

        listEl.innerHTML = data.documents.map(d => {
            const isPriv = d.security_level === 'PRIVATE';
            return `
            <div class="doc-item">
                <div class="doc-info">
                    <span class="doc-title" title="${d.name}">📄 ${d.name}</span>
                    <span class="doc-meta">${(d.size_bytes / 1024).toFixed(1)} KB</span>
                </div>
                <div class="doc-actions" style="display: flex; align-items: center; gap: 6px;">
                    <button class="doc-badge ${d.security_level.toLowerCase()}" onclick="toggleDocumentSecurity('${d.name}', '${d.security_level}')" title="Haz clic para cambiar visibilidad OKF" style="cursor: pointer;">
                        ${isPriv ? '🔒 Privado' : '🌐 Público'}
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="downloadDocument('${d.name}')" title="Descargar archivo PDF">
                        📥 Descargar
                    </button>
                </div>
            </div>
        `}).join('');
    } catch (e) {
        listEl.innerHTML = '<div class="doc-item"><span class="doc-title">Error al cargar documentos</span></div>';
    }
}

async function toggleDocumentSecurity(filename, currentLevel) {
    const nextLevel = currentLevel === 'PRIVATE' ? 'PUBLIC' : 'PRIVATE';
    try {
        const res = await fetch('/api/documents/toggle-security', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename, security_level: nextLevel })
        });
        const data = await res.json();
        alert(data.message);
        await fetchSystemStatus();
        await fetchDocumentsList();
        await loadKnowledgeGraph(currentView);
    } catch (e) {
        alert('Error al cambiar nivel de seguridad del documento');
    }
}

function downloadDocument(filename) {
    window.open(`/api/documents/download?file=${encodeURIComponent(filename)}`, '_blank');
}

// 3. Load & Render Knowledge Graph (OKF & Graphify)
async function loadKnowledgeGraph(view) {
    currentView = view;
    try {
        const res = await fetch(`/api/graphify?view=${view}`);
        graphifyData = await res.json();

        const resOkf = await fetch(`/api/okf?view=${view}`);
        googleOkfData = await resOkf.json();

        const resReport = await fetch('/api/report');
        graphReportMDText = await resReport.text();

        renderVisNetwork(graphifyData);
        updateJSONViewer(graphifyData);
        updateGoogleOKFViewer(googleOkfData);
        updateReportViewer(graphReportMDText);

        const subtitle = document.getElementById('graphSubtitle');
        if (subtitle) {
            if (view === 'public') {
                subtitle.innerText = '🌐 Vista Pública Cliente: Filtro de nodos público Google OKF con cero datos confidenciales';
                subtitle.style.color = 'var(--color-public)';
            } else {
                subtitle.innerText = '🔒 Vista Privada Interna: Grafo completo almacenado bajo el Estándar Google Cloud OKF (v1.0)';
                subtitle.style.color = 'var(--color-private)';
            }
        }
    } catch (e) {
        console.error('Error al cargar el grafo OKF/Graphify:', e);
    }
}

function renderVisNetwork(graphifyObj) {
    const container = document.getElementById('visNetworkCanvas');
    if (!container) return;

    const rawNodes = graphifyObj.nodes || [];
    const rawLinks = graphifyObj.links || graphifyObj.edges || [];

    const nodes = rawNodes.map(n => {
        const isPrivate = n.security_level === 'PRIVATE';
        const isOrg = n.type === 'ORGANIZATION';
        const isDoc = n.type === 'DOCUMENT';

        const baseBg = isOrg ? '#2563EB' : (isDoc ? '#4F46E5' : (isPrivate ? '#DC2626' : '#16A34A'));
        const borderColor = isOrg ? '#1D4ED8' : (isDoc ? '#3730A3' : (isPrivate ? '#B91C1C' : '#15803D'));
        
        let fontColor = '#FFFFFF';
        let iconSymbol = isOrg ? '🏢 ' : (isDoc ? '📄 ' : (isPrivate ? '🔒 ' : '🌐 '));

        const nodeDegree = n.degree || 1;
        const nodeMargin = Math.min(8 + nodeDegree * 2, 20);

        return {
            id: n.id,
            label: iconSymbol + n.label,
            shape: isOrg ? 'diamond' : (isDoc ? 'ellipse' : 'box'),
            margin: nodeMargin,
            color: {
                background: baseBg,
                border: borderColor,
                highlight: { background: '#1E293B', border: '#2563EB' }
            },
            font: { color: fontColor, face: 'Inter', size: 12, bold: true },
            borderWidth: 1.5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.12)', size: 4, x: 1, y: 2 },
            title: `<b>${n.label}</b><br/>Comunidad Graphify: Cluster ${n.community}<br/>Tipo: ${n.type}<br/>Seguridad: ${n.badge || n.security_level}<br/>Origen: ${n.source_doc}`
        };
    });

    const edges = rawLinks.map(e => {
        const isPrivate = e.security_level === 'PRIVATE';
        return {
            from: e.source,
            to: e.target,
            label: e.relation,
            font: { color: '#475569', size: 9, face: 'Inter', align: 'top' },
            color: { color: isPrivate ? '#FCA5A5' : '#94A3B8', highlight: '#2563EB' },
            arrows: { to: { enabled: true, scaleFactor: 0.6 } },
            dashes: isPrivate
        };
    });

    const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
    const options = {
        physics: {
            stabilization: false,
            barnesHut: { gravitationalConstant: -3800, springLength: 130 }
        },
        interaction: { hover: true, tooltipDelay: 100 }
    };

    if (networkInstance) {
        networkInstance.destroy();
    }
    networkInstance = new vis.Network(container, data, options);

    networkInstance.on("click", function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const targetNode = rawNodes.find(n => n.id === nodeId);
            if (targetNode) {
                showNodeDetailsModal(targetNode);
            }
        }
    });
}

function showNodeDetailsModal(node) {
    const isPrivate = node.security_level === 'PRIVATE';
    const badge = isPrivate ? '🔒 PRIVADO CONFIDENCIAL' : '🌐 PÚBLICO';
    
    let propsHTML = '';
    for (const [k, v] of Object.entries(node.properties || {})) {
        propsHTML += `<div><strong>${k}:</strong> ${v}</div>`;
    }

    const detailText = `
### ${node.label} (${node.type})
- **Comunidad Graphify:** Cluster ${node.community || 0}
- **Clasificación:** ${badge}
- **Grado de Conexión:** ${node.degree || 1}
- **Resumen:** ${node.summary || 'Sin resumen'}
- **Documento Origen:** \`${node.source_doc || 'General'}\`
#### Propiedades Estructuradas Graphify:
${propsHTML}
    `;

    // Switch to chat view to inspect details
    switchNavSection('chat');
    appendSystemMessage(detailText);
}

// 4. Sidebar Section Switcher
function switchNavSection(section) {
    currentNavSection = section;
    
    ['graph', 'chat', 'docs'].forEach(s => {
        const navBtn = document.getElementById('nav' + s.charAt(0).toUpperCase() + s.slice(1));
        const secEl = document.getElementById('section' + s.charAt(0).toUpperCase() + s.slice(1));
        
        if (navBtn) navBtn.classList.remove('active');
        if (secEl) secEl.classList.remove('active');
    });

    const activeNav = document.getElementById('nav' + section.charAt(0).toUpperCase() + section.slice(1));
    const activeSec = document.getElementById('section' + section.charAt(0).toUpperCase() + section.slice(1));

    if (activeNav) activeNav.classList.add('active');
    if (activeSec) activeSec.classList.add('active');

    if (section === 'graph') {
        setTimeout(resetGraphView, 100);
    }
}

// 5. Agent Model Selector
function selectChatAgentModel(model) {
    currentChatAgent = model;
    
    ['Cloud', 'Local', 'Dual'].forEach(m => {
        const btn = document.getElementById('btnAgent' + m);
        if (btn) btn.classList.remove('active');
    });

    const activeBtn = document.getElementById('btnAgent' + model.charAt(0).toUpperCase() + model.slice(1));
    if (activeBtn) activeBtn.classList.add('active');

    const nameEl = document.getElementById('agentName');
    const subtextEl = document.getElementById('agentSubtext');
    const avatarEl = document.getElementById('agentAvatar');

    if (model === 'local') {
        if (nameEl) nameEl.innerText = 'Agente Local Privado (gemma4:2b)';
        if (subtextEl) subtextEl.innerText = '💻 Acceso completo a Subgrafo Privado de Nómina y Salarios';
        if (avatarEl) avatarEl.innerText = '🔒';
    } else if (model === 'dual') {
        if (nameEl) nameEl.innerText = 'Modo Comparativo Dual (gemma4:2b & gemma4:31b-cloud)';
        if (subtextEl) subtextEl.innerText = '⚡ Evaluación Híbrida Simultánea de Seguridad y Aislamiento';
        if (avatarEl) avatarEl.innerText = '⚡';
    } else {
        if (nameEl) nameEl.innerText = 'Agente Cloud Público (gemma4:31b-cloud)';
        if (subtextEl) subtextEl.innerText = '☁️ Acceso a Subgrafo Público de Beneficios y Políticas';
        if (avatarEl) avatarEl.innerText = '🌐';
    }
}

function setGraphView(view) {
    const btnPriv = document.getElementById('btnViewPrivate');
    const btnPub = document.getElementById('btnViewPublic');

    if (view === 'private') {
        if (btnPriv) btnPriv.classList.add('active');
        if (btnPub) btnPub.classList.remove('active');
    } else {
        if (btnPub) btnPub.classList.add('active');
        if (btnPriv) btnPriv.classList.remove('active');
    }

    loadKnowledgeGraph(view);
}

function resetGraphView() {
    if (networkInstance) {
        networkInstance.fit({ animation: { duration: 600 } });
    }
}

// 6. Tabs Switcher for Inspectors
function switchMainTab(tab) {
    const tabVisual = document.getElementById('tabVisualGraph');
    const tabOKF = document.getElementById('tabGoogleOKF');
    const tabJSON = document.getElementById('tabGraphifyJSON');
    const tabReport = document.getElementById('tabReportMD');

    const contentVisual = document.getElementById('visualGraphContainer');
    const contentOKF = document.getElementById('googleOkfContainer');
    const contentJSON = document.getElementById('okfJsonContainer');
    const contentReport = document.getElementById('graphReportContainer');

    if (tabVisual) tabVisual.classList.remove('active');
    if (tabOKF) tabOKF.classList.remove('active');
    if (tabJSON) tabJSON.classList.remove('active');
    if (tabReport) tabReport.classList.remove('active');

    if (contentVisual) contentVisual.classList.remove('active');
    if (contentOKF) contentOKF.classList.remove('active');
    if (contentJSON) contentJSON.classList.remove('active');
    if (contentReport) contentReport.classList.remove('active');

    if (tab === 'visual') {
        if (tabVisual) tabVisual.classList.add('active');
        if (contentVisual) contentVisual.classList.add('active');
    } else if (tab === 'google_okf') {
        if (tabOKF) tabOKF.classList.add('active');
        if (contentOKF) contentOKF.classList.add('active');
    } else if (tab === 'graphify_json') {
        if (tabJSON) tabJSON.classList.add('active');
        if (contentJSON) contentJSON.classList.add('active');
    } else if (tab === 'report_md') {
        if (tabReport) tabReport.classList.add('active');
        if (contentReport) contentReport.classList.add('active');
    }
}

function updateJSONViewer(data) {
    const codeEl = document.getElementById('okfJsonCode');
    if (codeEl) codeEl.innerText = JSON.stringify(data, null, 2);
}

function updateGoogleOKFViewer(data) {
    const codeEl = document.getElementById('googleOkfCode');
    if (codeEl) codeEl.innerText = JSON.stringify(data, null, 2);
}

function updateReportViewer(mdText) {
    const codeEl = document.getElementById('graphReportCode');
    if (codeEl) codeEl.innerText = mdText;
}

function copyGoogleOKFJSON() {
    if (!googleOkfData) return;
    navigator.clipboard.writeText(JSON.stringify(googleOkfData, null, 2));
    alert('¡Esquema JSON Google Cloud OKF (v1.0) copiado al portapapeles!');
}

function copyGraphifyJSON() {
    if (!graphifyData) return;
    navigator.clipboard.writeText(JSON.stringify(graphifyData, null, 2));
    alert('¡JSON Estándar Graphify (graph.json) copiado al portapapeles!');
}

function copyGraphReportMD() {
    if (!graphReportMDText) return;
    navigator.clipboard.writeText(graphReportMDText);
    alert('¡Reporte GRAPH_REPORT.md copiado al portapapeles!');
}

function exportTypstPDFReport() {
    window.open(`/api/export-pdf?view=${currentView}`, '_blank');
}

// 7. Actions: Upload PDF, Ingest & Samples
async function handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const securitySelect = document.getElementById('uploadSecuritySelect');
    const selectedLevel = securitySelect ? securitySelect.value : 'PRIVATE';

    const payloadFiles = [];
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
            alert(`El archivo ${file.name} no es un PDF válido.`);
            continue;
        }

        const b64 = await readFileAsBase64(file);
        payloadFiles.push({
            filename: file.name,
            base64: b64,
            security_level: selectedLevel
        });
    }

    if (payloadFiles.length === 0) return;

    try {
        const btn = document.getElementById('btnUploadPdf');
        if (btn) btn.innerText = '⏳ Procesando PDFs...';

        const res = await fetch('/api/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ security_level: selectedLevel, files: payloadFiles })
        });

        const data = await res.json();
        alert(data.message);

        await fetchSystemStatus();
        await fetchDocumentsList();
        await loadKnowledgeGraph(currentView);
    } catch (e) {
        alert('Error al subir archivos PDF');
    } finally {
        const btn = document.getElementById('btnUploadPdf');
        if (btn) btn.innerText = '📤 Subir PDFs';
        event.target.value = '';
    }
}

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

async function reprocessDocuments() {
    try {
        const res = await fetch('/api/ingest', { method: 'POST' });
        const data = await res.json();
        alert(data.message);
        await fetchSystemStatus();
        await fetchDocumentsList();
        await loadKnowledgeGraph(currentView);
    } catch (e) {
        alert('Error al re-procesar carpeta PDF');
    }
}

async function generateSampleDocuments() {
    try {
        const res = await fetch('/api/generate-samples', { method: 'POST' });
        const data = await res.json();
        alert(data.message);
        await fetchSystemStatus();
        await fetchDocumentsList();
        await loadKnowledgeGraph(currentView);
    } catch (e) {
        alert('Error al generar PDFs de prueba');
    }
}

// 8. Chat System & Event Handlers
function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendUserQuery();
    }
}

function sendQuickQuery(text) {
    const input = document.getElementById('userQueryInput');
    if (input) input.value = text;

    if (text.includes('Salarios') || text.includes('Privado') || text.includes('Cédulas')) {
        selectChatAgentModel('local');
    } else {
        selectChatAgentModel('cloud');
    }
    sendUserQuery();
}

async function sendUserQuery() {
    const input = document.getElementById('userQueryInput');
    const query = input ? input.value.trim() : '';
    if (!query) return;

    if (currentNavSection !== 'chat') {
        switchNavSection('chat');
    }

    appendUserMessage(query);
    if (input) input.value = '';

    const loadingId = appendLoadingMessage();
    const startTime = Date.now();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, agent: currentChatAgent })
        });

        const data = await res.json();
        
        // Garantizar un mínimo de 500ms (0.5 segundos) de procesamiento para una respuesta fluida
        const elapsedTime = Date.now() - startTime;
        if (elapsedTime < 500) {
            await new Promise(resolve => setTimeout(resolve, 500 - elapsedTime));
        }

        removeMessage(loadingId);
        appendAgentResponse(data);
    } catch (e) {
        const elapsedTime = Date.now() - startTime;
        if (elapsedTime < 500) {
            await new Promise(resolve => setTimeout(resolve, 500 - elapsedTime));
        }

        removeMessage(loadingId);
        appendAgentResponse({
            agent: 'Sistema',
            answer: '❌ Error de comunicación con el Agente Híbrido.',
            security_view: 'Error'
        });
    }
}

function appendUserMessage(text) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user-msg';
    msgDiv.innerHTML = `
        <div class="msg-avatar">👤</div>
        <div class="msg-content">
            <p>${escapeHTML(text)}</p>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendLoadingMessage() {
    const chatContainer = document.getElementById('chatMessages');
    const id = 'msg_load_' + Date.now();
    if (!chatContainer) return id;

    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = 'message agent-msg';
    msgDiv.innerHTML = `
        <div class="msg-avatar">🤖</div>
        <div class="msg-content">
            <p><em>Procesando consulta con Gemma OKF Engine...</em></p>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function appendAgentResponse(data) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message agent-msg';

    const formattedAnswer = formatMarkdownText(data.answer);
    
    let citationsHTML = '';
    if (data.citations && data.citations.length > 0) {
        citationsHTML = data.citations.map(c => `<span class="citation-tag">📄 ${c}</span>`).join(' ');
    }

    const secView = data.security_view || '';
    const avatarSymbol = secView.includes('PRIVADA') ? '🔒' : (secView.includes('HÍBRIDA') ? '⚡' : '🌐');

    msgDiv.innerHTML = `
        <div class="msg-avatar">${avatarSymbol}</div>
        <div class="msg-content">
            <div>${formattedAnswer}</div>
            <div class="msg-meta">
                <span>🤖 ${data.agent || 'Agente Gemma'}</span>
                <span>• Visibilidad: <strong>${secView}</strong></span>
                ${citationsHTML ? '• Fuentes: ' + citationsHTML : ''}
            </div>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendSystemMessage(text) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message agent-msg';
    msgDiv.innerHTML = `
        <div class="msg-avatar">🔍</div>
        <div class="msg-content">
            ${formatMarkdownText(text)}
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHTML(str) {
    return (str || '').replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function formatMarkdownText(text) {
    if (!text) return '';
    return text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^\* (.*$)/gim, '<li>$1</li>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br/>');
}
