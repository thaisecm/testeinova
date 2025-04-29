# app.py
import streamlit as st
from docx import Document
import PyPDF2
from io import BytesIO
import json
from datetime import datetime
from fpdf import FPDF

# Inicializa as variáveis de sessão se não existirem
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'responsavel': '',
        'cliente': '',
        'numero_historia': '',
        'base_testes': '',
        'arquivos_utilizados': '',
        'data_teste': datetime.now().strftime('%Y-%m-%d')
    }

def reset_user_data():
    """Reseta os dados do usuário para valores padrão"""
    st.session_state.user_data = {
        'responsavel': '',
        'cliente': '',
        'numero_historia': '',
        'base_testes': '',
        'arquivos_utilizados': '',
        'data_teste': datetime.now().strftime('%Y-%m-%d')
    }
    # Flag para limpar o localStorage no HTML
    st.session_state.clear_local_storage = True

def extract_text(uploaded_file):
    """Extrai texto de arquivos DOCX ou PDF"""
    try:
        if uploaded_file.name.endswith('.docx'):
            doc = Document(BytesIO(uploaded_file.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        elif uploaded_file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        return None
    except Exception as e:
        st.error(f"Erro na extração: {str(e)}")
        return None

def generate_pdf_report(test_items, filename, user_data, completed_items=True):
    """Gera um relatório PDF com os itens marcados ou pendentes"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatório de Testes" if completed_items else "Ajustes Pendentes", ln=1, align='C')
    pdf.set_font("Arial", size=12)
    pdf.line(10, 20, 200, 20)
    pdf.ln(10)
    
    # Informações do teste (em duas colunas)
    col_width = 90
    x_pos = pdf.get_x()
    y_pos = pdf.get_y()
    
    # Coluna 1
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Arquivo original:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=filename, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Responsável:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['responsavel'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Cliente:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['cliente'], ln=1)
    
    # Coluna 2
    pdf.set_xy(x_pos + col_width + 10, y_pos)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Nº História:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['numero_historia'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Data do Teste:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['data_teste'], ln=1)
    
    # Volta para a coluna 1 para continuar
    pdf.set_xy(x_pos, pdf.get_y())
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Base de Testes:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['base_testes'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(col_width, 10, txt="Arquivos Utilizados:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=user_data['arquivos_utilizados'])
    
    pdf.ln(15)
    
    # Título da seção
    pdf.set_font("Arial", 'B', 14)
    title = "TESTES VALIDADOS" if completed_items else "AJUSTES PENDENTES"
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    
    # Itens do relatório com numeração e formatação melhorada
    for idx, item in enumerate(test_items, 1):
        # Remove marcadores [ ] ou [x] se existirem
        clean_item = item.replace("[ ]", "").replace("[x]", "").strip()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(10, 8, txt=f"{idx}.", ln=0)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, txt=clean_item)
        pdf.ln(5)
    
    # Rodapé com borda superior
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt=f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin1')

def generate_html_report(test_items, filename, initial_checks=None, user_data=None):
    """Gera um relatório HTML interativo com o layout do arquivo fornecido"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    if user_data is None:
        user_data = st.session_state.user_data
    
    # Script para limpar o localStorage se necessário
    clear_storage_script = ""
    if hasattr(st.session_state, 'clear_local_storage') and st.session_state.clear_local_storage:
        clear_storage_script = """
        <script>
            // Limpa o localStorage completamente
            localStorage.clear();
        </script>
        """
        del st.session_state.clear_local_storage
    
    # Gera a lista de itens HTML inicial
    # Modificado para incluir botões de editar e excluir
    test_items_html = []
    for i, item in enumerate(test_items):
        item_text = item.replace("[ ]", "").replace("[x]", "")
        checked_attr = "checked" if initial_checks[i] else ""
        item_html = f'''
        <div class="checklist-item" data-index="{i}">
            <input type="checkbox" id="item{i}" {checked_attr} onchange="handleCheckboxChange(this, {i})">
            <label for="item{i}">{item_text}</label>
            <div class="item-buttons">
                <button class="btn-edit-item" onclick="editItem({i})">✏️</button>
                <button class="btn-delete-item" onclick="deleteItem({i})">🗑️</button>
            </div>
        </div>
        '''
        test_items_html.append(item_html)

    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Testes - {filename}</title>
    <style>
        :root {{
            --primary-color: #0054a6;
            --secondary-color: #00a0e3;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --warning-color: #ffc107;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --border-color: #dee2e6;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 25px;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        h1 {{
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 10px;
        }}
        
        .info-section {{
            margin-bottom: 25px;
            padding: 20px;
            background-color: var(--light-color);
            border-radius: 5px;
        }}
        
        .form-row {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .form-group {{
            flex: 1 1 200px;
            min-width: 0;
            margin-bottom: 10px;
        }}
        
        .form-group-small {{
            flex: 0 1 150px;
            min-width: 0;
        }}
        
        .form-group-medium {{
            flex: 0 1 250px;
            min-width: 0;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            color: #555;
        }}
        
        input[type="text"], 
        input[type="date"] {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.95rem;
            box-sizing: border-box;
        }}
        
        .section-title-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 25px 0 15px;
            border-bottom: 2px solid var(--secondary-color);
            padding-bottom: 5px;
        }}

        .section-title {{
            color: var(--primary-color);
            margin: 0;
            border-bottom: none; /* Remove a borda individual */
        }}
        
        .checklist-item {{
            display: flex;
            align-items: center; /* Alinha verticalmente */
            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background-color: white;
        }}
        
        .checklist-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .checklist-item input[type="checkbox"] {{
            margin-right: 10px;
            margin-top: 0; /* Ajuste para alinhar com o texto */
            min-width: 18px;
            height: 18px;
            flex-shrink: 0; /* Impede que o checkbox encolha */
        }}
        
        .checklist-item label {{
            font-weight: normal;
            cursor: pointer;
            flex-grow: 1;
            margin-right: 10px; /* Espaço entre o texto e os botões */
        }}

        .item-buttons {{
            display: flex;
            gap: 5px;
            flex-shrink: 0; /* Impede que os botões encolham */
        }}

        .btn-edit-item, .btn-delete-item {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            padding: 2px 5px;
            line-height: 1;
            color: #6c757d;
            transition: color 0.2s;
        }}

        .btn-edit-item:hover {{
            color: var(--primary-color);
        }}

        .btn-delete-item:hover {{
            color: var(--danger-color);
        }}
        
        .status-bar {{
            margin: 20px 0;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
            font-weight: 600;
        }}
        
        .status-incomplete {{
            background-color: #fff3cd;
            color: #856404;
        }}
        
        .status-complete {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        button {{
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s;
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .btn-success {{
            background-color: var(--success-color);
            color: white;
        }}
        
        .btn-danger {{
            background-color: var(--danger-color);
            color: white;
        }}
        
        .btn-warning {{
            background-color: var(--warning-color);
            color: #212529;
        }}
        
        .btn-secondary {{
            background-color: var(--dark-color);
            color: white;
        }}

        .btn-add-item {{
            background-color: var(--success-color);
            color: white;
            padding: 5px 10px;
            font-size: 0.9rem;
        }}
        
        .log-container {{
            margin-top: 30px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 10px;
            background-color: #f8f9fa;
        }}
        
        .log-entry {{
            margin-bottom: 5px;
            padding: 5px;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
        }}
        
        footer {{
            margin-top: 30px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .form-row {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .form-group, .form-group-small, .form-group-medium {{
                flex: 1;
                min-width: 100%;
            }}
            
            .buttons {{
                flex-direction: column;
            }}
            
            button {{
                width: 100%;
            }}

            .item-buttons button {{
                width: auto; /* Restaura largura automática para botões de item */
            }}

            .btn-add-item {{
                 width: auto; /* Restaura largura automática para botão de adicionar */
                 margin-left: 10px; /* Adiciona espaço em telas menores */
            }}

            .section-title-container {{
                flex-wrap: wrap; /* Permite que o botão quebre a linha */
            }}
        }}
    </style>
</head>
<body>
    {clear_storage_script}
    <div class="container">
        <header>
            <h1>Controle de Testes</h1>
            <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>Arquivo original: {filename}</p>
        </header>
        
        <div class="info-section">
            <div class="form-row">
                <div class="form-group-small">
                    <label for="responsavel">Responsável:</label>
                    <input type="text" id="responsavel" value="{user_data['responsavel']}" maxlength="15">
                </div>
                <div class="form-group-small">
                    <label for="data-teste">Data do Teste:</label>
                    <input type="date" id="data-teste" value="{user_data['data_teste']}">
                </div>
                <div class="form-group-medium">
                    <label for="cliente">Cliente:</label>
                    <input type="text" id="cliente" value="{user_data['cliente']}" maxlength="20">
                </div>
                <div class="form-group-small">
                    <label for="numero-historia">Nº História:</label>
                    <input type="text" id="numero-historia" value="{user_data['numero_historia']}">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="base-testes">Base de Testes:</label>
                    <input type="text" id="base-testes" value="{user_data['base_testes']}">
                </div>
                <div class="form-group">
                    <label for="arquivos-utilizados">Arquivos Utilizados:</label>
                    <input type="text" id="arquivos-utilizados" value="{user_data['arquivos_utilizados']}">
                </div>
            </div>
        </div>
        
        <div class="section-title-container">
             <h2 class="section-title">Checklist de Validação</h2>
             <button class="btn-add-item" onclick="addItem()">+ Adicionar Item</button>
        </div>
        
        <div id="testItemsContainer">
            {''.join(test_items_html)}
        </div>
        
        <div class="status-bar status-incomplete" id="status-bar">
            Calculando...
        </div>
        
        <div class="buttons">
            <button class="btn-primary" onclick="saveProgress()">Salvar Progresso</button>
            <button class="btn-success" onclick="selectAllTests()">Marcar Todos</button>
            <button class="btn-danger" onclick="resetTests()">Reiniciar Testes</button>
            <button class="btn-warning" onclick="exportReport()">Relatório de Testes</button>
            <button class="btn-secondary" onclick="exportPending()">Ajustes Pendentes</button>
        </div>
        
        <h3 class="section-title">Log de Alterações</h3>
        <div class="log-container" id="logEntries"></div>
        
        <footer>
            <p>© {datetime.now().strftime('%Y')} - Relatório gerado automaticamente</p>
        </footer>
    </div>

    <script>
        // Inicializa variáveis globais
        let testItemsData = {json.dumps(test_items)}; // Array com os textos dos itens
        let testState = {json.dumps(initial_checks)}; // Array com os estados (marcado/desmarcado)
        let logEntries = ['Documento carregado'];
        const testItemsContainer = document.getElementById('testItemsContainer');
        const statusBar = document.getElementById('status-bar');
        const logContainer = document.getElementById('logEntries');

        // Atualiza a barra de status
        function updateStatusBar() {
            const totalItems = testState.length;
            if (totalItems === 0) {
                 statusBar.textContent = 'Nenhum item no checklist';
                 statusBar.className = 'status-bar status-incomplete'; // Ou outra classe apropriada
                 return;
            }
            const checkedCount = testState.filter(x => x).length;
            const percentage = Math.round((checkedCount / totalItems) * 100);
            
            statusBar.textContent = `${checkedCount} de ${totalItems} itens verificados (${percentage}%)`;
            
            if (checkedCount === totalItems) {
                statusBar.className = 'status-bar status-complete';
            } else {
                statusBar.className = 'status-bar status-incomplete';
            }
        }

        // Adiciona entrada no log
        function addLogEntry(action) {
            const now = new Date();
            const timestamp = now.toLocaleString('pt-BR');
            const logMessage = `[${timestamp}] ${action}`;
            logEntries.push(logMessage);
            
            const entryElement = document.createElement('div');
            entryElement.className = 'log-entry';
            entryElement.textContent = logMessage;
            logContainer.appendChild(entryElement);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // Salva progresso no localStorage
        function saveProgress() {
            const userData = {
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            };
            
            // Valida campos obrigatórios
            if (!userData.responsavel || !userData.cliente || !userData.numero_historia || 
                !userData.base_testes || !userData.arquivos_utilizados) {
                alert('Por favor, preencha todos os campos antes de salvar!');
                return;
            }
            
            // Salva o estado atual dos itens e seus textos
            localStorage.setItem('testProgress', JSON.stringify(testState));
            localStorage.setItem('testItemsData', JSON.stringify(testItemsData)); 
            localStorage.setItem('userData', JSON.stringify(userData));
            localStorage.setItem('logEntries', JSON.stringify(logEntries));
            
            addLogEntry('Progresso salvo com sucesso');
            alert('Progresso salvo com sucesso!');
        }

        // Marca todos os itens
        function selectAllTests() {
            testState = Array(testItemsData.length).fill(true);
            renderChecklist(); // Re-renderiza para atualizar checkboxes
            updateStatusBar();
            addLogEntry('Todos os itens foram marcados');
        }

        // Exporta relatório completo em PDF
        function exportReport() {
            const userData = {
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            };
            
            const completedItems = testItemsData.filter((item, i) => testState[i]);
            
            if (completedItems.length === 0) {
                alert('Não há itens verificados para exportar!');
                return;
            }
            
            // Cria um link para download do PDF (simulado, pois a geração é no backend)
            // No Streamlit, você precisaria enviar esses dados de volta para gerar o PDF
            const pdfData = {
                items: completedItems,
                filename: '{filename}',
                user_data: userData,
                report_type: 'completed'
            };
            
            // Simulação de download (idealmente, isso chamaria uma função do Streamlit)
            console.log("Exportar Relatório PDF (simulado):", pdfData);
            alert("Funcionalidade de exportação PDF precisa ser integrada com o backend (Streamlit).");
            addLogEntry('Tentativa de exportar relatório de testes em PDF');
        }

        // Exporta itens pendentes em PDF
        function exportPending() {
            const userData = {
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            };
            
            const pendingItems = testItemsData.filter((item, i) => !testState[i]);
            
            if (pendingItems.length === 0) {
                alert('Não há itens pendentes para exportar!');
                return;
            }
            
            // Simulação de download
            const pdfData = {
                items: pendingItems,
                filename: '{filename}',
                user_data: userData,
                report_type: 'pending'
            };
            console.log("Exportar Pendentes PDF (simulado):", pdfData);
            alert("Funcionalidade de exportação PDF precisa ser integrada com o backend (Streamlit).");
            addLogEntry('Tentativa de exportar ajustes pendentes em PDF');
        }

        // Reinicia todos os testes
        function resetTests() {
            if (confirm('Tem certeza que deseja reiniciar todos os testes? Isso limpará as marcações e o log.')) {
                testState = Array(testItemsData.length).fill(false);
                logEntries = ['Testes reiniciados'];
                renderChecklist();
                renderLog();
                updateStatusBar();
                // Limpa o localStorage também
                localStorage.removeItem('testProgress');
                localStorage.removeItem('testItemsData');
                localStorage.removeItem('logEntries');
                // Não limpa userData intencionalmente
            }
        }

        // Carrega progresso salvo do localStorage
        function loadProgress() {
            const savedState = localStorage.getItem('testProgress');
            const savedItems = localStorage.getItem('testItemsData');
            const savedUserData = localStorage.getItem('userData');
            const savedLog = localStorage.getItem('logEntries');

            if (savedItems) {
                testItemsData = JSON.parse(savedItems);
            }
            if (savedState) {
                testState = JSON.parse(savedState);
                // Garante que testState tenha o mesmo tamanho de testItemsData
                if (testState.length !== testItemsData.length) {
                     testState = Array(testItemsData.length).fill(false);
                     console.warn('Inconsistência entre itens salvos e estados. Resetando estados.');
                }
            } else {
                 testState = Array(testItemsData.length).fill(false);
            }
            
            if (savedUserData) {
                const userData = JSON.parse(savedUserData);
                document.getElementById('responsavel').value = userData.responsavel || '';
                document.getElementById('data-teste').value = userData.data_teste || '{datetime.now().strftime('%Y-%m-%d')}';
                document.getElementById('cliente').value = userData.cliente || '';
                document.getElementById('numero-historia').value = userData.numero_historia || '';
                document.getElementById('base-testes').value = userData.base_testes || '';
                document.getElementById('arquivos-utilizados').value = userData.arquivos_utilizados || '';
            } else {
                 // Limpa campos se não houver dados salvos
                 document.getElementById('responsavel').value = '{user_data['responsavel']}';
                 document.getElementById('data-teste').value = '{user_data['data_teste']}';
                 document.getElementById('cliente').value = '{user_data['cliente']}';
                 document.getElementById('numero-historia').value = '{user_data['numero_historia']}';
                 document.getElementById('base-testes').value = '{user_data['base_testes']}';
                 document.getElementById('arquivos-utilizados').value = '{user_data['arquivos_utilizados']}';
            }

            if (savedLog) {
                logEntries = JSON.parse(savedLog);
            } else {
                logEntries = ['Documento carregado / Progresso não encontrado'];
            }

            renderChecklist();
            renderLog();
            updateStatusBar();
        }

        // Renderiza o checklist completo no HTML
        function renderChecklist() {
            testItemsContainer.innerHTML = ''; // Limpa o container
            testItemsData.forEach((itemText, i) => {
                const checked_attr = testState[i] ? "checked" : "";
                // Remove marcadores antigos se existirem no texto
                const cleanItemText = itemText.replace(/^-\s*\[[ x]\]\s*/, '').trim(); 
                const itemElement = document.createElement('div');
                itemElement.className = 'checklist-item';
                itemElement.setAttribute('data-index', i);
                itemElement.innerHTML = `
                    <input type="checkbox" id="item${i}" ${checked_attr} onchange="handleCheckboxChange(this, ${i})">
                    <label for="item${i}">${cleanItemText}</label>
                    <div class="item-buttons">
                        <button class="btn-edit-item" onclick="editItem(${i})">✏️</button>
                        <button class="btn-delete-item" onclick="deleteItem(${i})">🗑️</button>
                    </div>
                `;
                testItemsContainer.appendChild(itemElement);
            });
            updateStatusBar(); // Atualiza status após renderizar
        }

        // Renderiza o log
        function renderLog() {
            logContainer.innerHTML = '';
            logEntries.forEach(logMessage => {
                 const entryElement = document.createElement('div');
                 entryElement.className = 'log-entry';
                 entryElement.textContent = logMessage;
                 logContainer.appendChild(entryElement);
            });
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // Manipula mudança no checkbox
        function handleCheckboxChange(checkbox, index) {
            testState[index] = checkbox.checked;
            updateStatusBar();
            const action = checkbox.checked ? 'marcou' : 'desmarcou';
            const itemText = testItemsData[index].replace(/^-\s*\[[ x]\]\s*/, '').trim();
            addLogEntry(`${action} o item: ${itemText}`);
        }

        // Função para DELETAR um item
        function deleteItem(index) {
            const itemText = testItemsData[index].replace(/^-\s*\[[ x]\]\s*/, '').trim();
            if (confirm(`Tem certeza que deseja excluir o item: "${itemText}"?`)) {
                testItemsData.splice(index, 1);
                testState.splice(index, 1);
                renderChecklist(); // Re-renderiza a lista com índices atualizados
                addLogEntry(`Excluiu o item: ${itemText}`);
            }
        }

        // Função para EDITAR um item (placeholder)
        function editItem(index) {
            const currentText = testItemsData[index].replace(/^-\s*\[[ x]\]\s*/, '').trim();
            const newText = prompt("Editar item:", currentText);
            if (newText !== null && newText.trim() !== '') {
                testItemsData[index] = newText.trim();
                renderChecklist();
                addLogEntry(`Editou o item ${index + 1}: ${newText.trim()}`);
            } else if (newText !== null) { // Se clicou OK mas deixou em branco
                 alert("O texto do item não pode ficar em branco.");
            }
        }

        // Função para ADICIONAR um item
        function addItem() {
            const newItemText = prompt("Digite o texto do novo item:");
            if (newItemText !== null && newItemText.trim() !== '') {
                testItemsData.push(newItemText.trim());
                testState.push(false); // Novo item começa desmarcado
                renderChecklist();
                addLogEntry(`Adicionou novo item: ${newItemText.trim()}`);
            } else if (newItemText !== null) {
                 alert("O texto do item não pode ficar em branco.");
            }
        }

        // Inicializa ao carregar a página
        window.onload = function() {
            loadProgress();
        };
    </script>
</body>
</html>
    """
    return html_content

def main():
    st.set_page_config(page_title="Controle de Testes", layout="centered")
    
    st.title("📋 Controle de Testes")
    st.markdown("""
    ### Como usar:
    1. Faça upload de um arquivo DOCX ou PDF
    2. Preencha as informações do teste
    3. Baixe o relatório HTML interativo
    4. Abra o HTML em qualquer navegador para usar as funcionalidades
    """)
    
    uploaded_file = st.file_uploader(
        "Arraste e solte seu arquivo aqui (DOCX ou PDF)",
        type=['docx', 'pdf'],
        accept_multiple_files=False,
        help="Tamanho máximo: 200MB"
    )
    
    if uploaded_file:
        with st.spinner("Processando arquivo..."):
            try:
                # Reseta os dados do usuário quando um novo arquivo é carregado
                # Não reseta mais aqui, pois o loadProgress no HTML cuidará disso
                # reset_user_data() 
                
                text_content = extract_text(uploaded_file)
                
                if text_content:
                    # Processa linhas relevantes
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    # Remove marcadores como '- [ ] ' ou similares do início das linhas extraídas
                    test_items_raw = [line.replace("- [ ]", "").replace("- [x]", "").strip() for line in lines if len(line.split()) > 3][:50]
                    # Garante que não haja itens vazios
                    test_items = [item for item in test_items_raw if item]

                    if test_items:
                        # Coleta informações adicionais do usuário
                        with st.expander("Informações do Teste", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.session_state.user_data['responsavel'] = st.text_input(
                                    "Responsável:", 
                                    value=st.session_state.user_data['responsavel'],
                                    max_chars=15
                                )
                                st.session_state.user_data['cliente'] = st.text_input(
                                    "Cliente:", 
                                    value=st.session_state.user_data['cliente'],
                                    max_chars=20
                                )
                                st.session_state.user_data['numero_historia'] = st.text_input(
                                    "Nº História:",
                                    value=st.session_state.user_data['numero_historia']
                                )
                            with col2:
                                data_teste_default = datetime.strptime(st.session_state.user_data['data_teste'], '%Y-%m-%d') if st.session_state.user_data['data_teste'] else datetime.now()
                                data_teste = st.date_input(
                                    "Data do Teste:",
                                    value=data_teste_default
                                )
                                st.session_state.user_data['data_teste'] = data_teste.strftime('%Y-%m-%d')
                                st.session_state.user_data['base_testes'] = st.text_input(
                                    "Base de Testes:",
                                    value=st.session_state.user_data['base_testes']
                                )
                                st.session_state.user_data['arquivos_utilizados'] = st.text_input(
                                    "Arquivos Utilizados:",
                                    value=st.session_state.user_data['arquivos_utilizados']
                                )
                        
                        # Gera o HTML com os itens extraídos e dados do usuário
                        html_report = generate_html_report(
                            test_items=test_items, 
                            filename=uploaded_file.name,
                            initial_checks=[False] * len(test_items), # Sempre começa desmarcado
                            user_data=st.session_state.user_data
                        )
                        
                        # Botão para baixar o HTML
                        st.download_button(
                            label="Baixar Relatório Interativo HTML",
                            data=html_report,
                            file_name=f"relatorio_interativo_{uploaded_file.name.split('.')[0]}.html",
                            mime="text/html",
                            help="Abra este arquivo em seu navegador para usar o checklist interativo."
                        )
                        
                        st.success("Relatório HTML gerado com sucesso! Clique no botão acima para baixar.")
                        
                    else:
                        st.warning("Não foram encontrados itens de checklist válidos no arquivo.")
                else:
                    st.error("Não foi possível extrair texto do arquivo.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {str(e)}")
                st.exception(e) # Mostra o traceback completo para depuração

if __name__ == "__main__":
    main()

