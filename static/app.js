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

function createCustomNodeTooltip(n) {
    const tooltip = document.createElement('div');
    tooltip.style.padding = '10px 14px';
    tooltip.style.background = '#FFFFFF';
    tooltip.style.border = '1px solid #CBD5E1';
    tooltip.style.borderRadius = '8px';
    tooltip.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
    tooltip.style.fontFamily = 'Inter, sans-serif';
    tooltip.style.fontSize = '12px';
    tooltip.style.color = '#0F172A';
    tooltip.style.lineHeight = '1.5';
    tooltip.style.maxWidth = '280px';
    tooltip.style.wordBreak = 'break-word';
    tooltip.style.overflowWrap = 'break-word';
    tooltip.style.whiteSpace = 'normal';

    const isPriv = n.security_level === 'PRIVATE';
    const badgeText = isPriv ? '🔒 PRIVADO' : '🌐 PÚBLICO';
    const badgeColor = isPriv ? '#DC2626' : '#16A34A';
    const badgeBg = isPriv ? '#FEE2E2' : '#DCFCE7';

    tooltip.innerHTML = `
        <div style="font-weight: 700; font-size: 13px; color: #0F172A; margin-bottom: 6px; display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; word-break: break-word;">
            <span style="flex: 1; word-break: break-word;">${n.label}</span>
            <span style="font-size: 10px; background: ${badgeBg}; color: ${badgeColor}; padding: 2px 7px; border-radius: 99px; font-weight: 700; white-space: nowrap; flex-shrink: 0;">${badgeText}</span>
        </div>
        <div style="color: #475569; font-size: 11px; word-break: break-word;">
            <div><strong>Tipo:</strong> ${n.type || 'Entidad'}</div>
            <div><strong>Cluster Graphify:</strong> Grupo ${n.community || 0}</div>
            <div style="word-break: break-word; margin-top: 2px;"><strong>Origen:</strong> 📄 ${n.source_doc || 'General'}</div>
        </div>
    `;

    return tooltip;
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
        const displayLabel = n.label.length > 24 ? n.label.substring(0, 22) + '…' : n.label;

        return {
            id: n.id,
            label: iconSymbol + displayLabel,
            shape: isOrg ? 'diamond' : (isDoc ? 'ellipse' : 'box'),
            margin: nodeMargin,
            widthConstraint: { maximum: 160 },
            color: {
                background: baseBg,
                border: borderColor,
                highlight: { background: '#1E293B', border: '#2563EB' }
            },
            font: { color: fontColor, face: 'Inter', size: 11, bold: true },
            borderWidth: 1.5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.12)', size: 4, x: 1, y: 2 },
            title: createCustomNodeTooltip(n)
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

let selectedNodeData = null;
let isSubgraphFocused = false;

function showNodeDetailsModal(node) {
    selectedNodeData = node;
    const overlay = document.getElementById('nodeModalOverlay');
    const badgeEl = document.getElementById('nodeModalBadge');
    const titleEl = document.getElementById('nodeModalTitle');
    const bodyEl = document.getElementById('nodeModalBody');
    const focusBtn = document.getElementById('btnFocusSubgraph');

    if (!overlay || !bodyEl) return;

    const isPrivate = node.security_level === 'PRIVATE';
    const secClass = isPrivate ? 'private' : 'public';
    const secLabel = isPrivate ? '🔒 PRIVADO CONFIDENCIAL' : '🌐 PÚBLICO';

    if (badgeEl) {
        badgeEl.className = `doc-badge ${secClass}`;
        badgeEl.innerText = secLabel;
    }

    if (titleEl) {
        titleEl.innerText = `📌 ${node.label} (${node.type || 'ENTIDAD'})`;
    }

    // Contar conexiones reales en el grafo actual
    const rawLinks = graphifyData ? (graphifyData.links || graphifyData.edges || []) : [];
    const connectedCount = rawLinks.filter(e => e.source === node.id || e.target === node.id).length;
    const hasEnoughData = connectedCount > 1 && !isSubgraphFocused;

    if (focusBtn) {
        if (hasEnoughData) {
            focusBtn.style.display = 'inline-flex';
            focusBtn.innerText = `🕸️ Ver Subgrafo Conectado (${connectedCount})`;
        } else {
            focusBtn.style.display = 'none';
        }
    }

    let propsHTML = '';
    for (const [k, v] of Object.entries(node.properties || {})) {
        propsHTML += `<div class="node-info-row"><span class="node-info-label">${k}:</span><span class="node-info-val">${v}</span></div>`;
    }

    bodyEl.innerHTML = `
        <div class="node-info-grid">
            <div class="node-info-row">
                <span class="node-info-label">Clasificación OKF:</span>
                <span class="node-info-val">${secLabel}</span>
            </div>
            <div class="node-info-row">
                <span class="node-info-label">Comunidad Graphify:</span>
                <span class="node-info-val">Cluster ${node.community || 0}</span>
            </div>
            <div class="node-info-row">
                <span class="node-info-label">Relaciones Conectadas:</span>
                <span class="node-info-val">${connectedCount} aristas activas</span>
            </div>
            <div class="node-info-row">
                <span class="node-info-label">Documento Origen:</span>
                <span class="node-info-val">📄 ${node.source_doc || 'General'}</span>
            </div>
        </div>

        <div class="node-properties-box">
            <h4>📝 Resumen y Atributos Estructurados:</h4>
            <p style="margin-bottom: 8px;">${node.summary || 'Sin resumen disponible'}</p>
            ${propsHTML ? `<div class="node-info-grid">${propsHTML}</div>` : ''}
            ${!hasEnoughData && !isSubgraphFocused ? `<p style="color: #64748B; font-size: 0.72rem; margin-top: 8px; font-style: italic;">⚠️ Información escasa: El nodo posee conexiones aisladas (${connectedCount}). Se desactiva la generación de subgrafo secundario.</p>` : ''}
        </div>
    `;

    overlay.classList.add('active');
}

function closeNodeModal() {
    const overlay = document.getElementById('nodeModalOverlay');
    if (overlay) overlay.classList.remove('active');
}

function handleModalOverlayClick(e) {
    if (e.target.id === 'nodeModalOverlay') {
        closeNodeModal();
    }
}

function triggerFocusSubgraph() {
    if (!selectedNodeData) return;
    closeNodeModal();
    focusNodeSubgraph(selectedNodeData.id);
}

function focusNodeSubgraph(targetNodeId) {
    if (!graphifyData) return;

    const rawNodes = graphifyData.nodes || [];
    const rawLinks = graphifyData.links || graphifyData.edges || [];

    const connectedEdges = rawLinks.filter(e => e.source === targetNodeId || e.target === targetNodeId);
    
    const neighborNodeIds = new Set([targetNodeId]);
    connectedEdges.forEach(e => {
        neighborNodeIds.add(e.source);
        neighborNodeIds.add(e.target);
    });

    const subNodes = rawNodes.filter(n => neighborNodeIds.has(n.id));

    // Control de información escasa o excesiva recursividad
    if (connectedEdges.length <= 1 || subNodes.length <= 1) {
        alert(`⚠️ Información escasa: El nodo '${selectedNodeData ? selectedNodeData.label : targetNodeId}' no posee suficientes conexiones para aislar un subgrafo.`);
        return;
    }

    isSubgraphFocused = true;

    // Renderizar subgrafo directo sin recursión
    renderVisNetwork({ nodes: subNodes, links: connectedEdges });

    const resetBtn = document.getElementById('btnResetSubgraph');
    if (resetBtn) resetBtn.style.display = 'inline-flex';

    const subtitle = document.getElementById('graphSubtitle');
    if (subtitle) {
        subtitle.innerText = `🎯 Subgrafo enfocado en '${selectedNodeData.label}' (${subNodes.length} nodos relacionados)`;
        subtitle.style.color = 'var(--primary-blue)';
    }
}

function resetNodeSubgraphFilter() {
    isSubgraphFocused = false;
    const resetBtn = document.getElementById('btnResetSubgraph');
    if (resetBtn) resetBtn.style.display = 'none';
    loadKnowledgeGraph(currentView);
}

function triggerAskAgentAboutNode() {
    if (!selectedNodeData) return;
    const label = selectedNodeData.label;
    closeNodeModal();
    switchNavSection('chat');
    sendQuickQuery(`¿Qué información de Recursos Humanos existe sobre ${label}?`);
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
