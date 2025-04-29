# app.py
import streamlit as st
from docx import Document
import PyPDF2
from io import BytesIO
import json
from datetime import datetime
from fpdf import FPDF

# Inicializa as variáveis de sessão
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
    
    # Informações do teste
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Arquivo original:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=filename, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Responsável:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['responsavel'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Cliente:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['cliente'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Nº História:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['numero_historia'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Data do Teste:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['data_teste'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Base de Testes:", ln=0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=user_data['base_testes'], ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, txt="Arquivos Utilizados:", ln=0)
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
    
    # Itens do relatório
    for idx, item in enumerate(test_items, 1):
        clean_item = item.replace("[ ]", "").replace("[x]", "").strip()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(10, 8, txt=f"{idx}.", ln=0)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, txt=clean_item)
        pdf.ln(5)
    
    # Rodapé
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt=f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin1')

def generate_html_report(test_items, filename, initial_checks=None, user_data=None):
    """Gera um relatório HTML com o layout especificado"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    if user_data is None:
        user_data = st.session_state.user_data
    
    # Script para limpar o localStorage
    clear_storage_script = ""
    if hasattr(st.session_state, 'clear_local_storage') and st.session_state.clear_local_storage:
        clear_storage_script = """
        <script>
            localStorage.clear();
        </script>
        """
        del st.session_state.clear_local_storage
    
    # Gera os itens do checklist
    test_items_html = []
    for i, item in enumerate(test_items):
        item_text = item.replace("[ ]", "").replace("[x]", "")
        checked_attr = "checked" if initial_checks[i] else ""
        test_items_html.append(f'''
        <div class="checklist-item">
            <input type="checkbox" id="item{i}" {checked_attr}>
            <label for="item{i}">{item_text}</label>
        </div>
        ''')

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
        
        .section-title {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--secondary-color);
            padding-bottom: 5px;
            margin: 25px 0 15px;
        }}
        
        .checklist-item {{
            display: flex;
            align-items: flex-start;
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
            margin-top: 3px;
            min-width: 18px;
            height: 18px;
        }}
        
        .checklist-item label {{
            font-weight: normal;
            cursor: pointer;
            flex-grow: 1;
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
        
        <h2 class="section-title">Checklist de Validação</h2>
        
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
        // Inicializa variáveis
        let testState = {json.dumps(initial_checks)};
        let logEntries = ['Documento carregado'];
        const totalItems = testState.length;

        // Atualiza a barra de status
        function updateStatusBar() {{
            const checkedCount = testState.filter(x => x).length;
            const percentage = Math.round((checkedCount / totalItems) * 100);
            const statusBar = document.getElementById('status-bar');
            
            statusBar.textContent = `${{checkedCount}} de ${{totalItems}} itens verificados (${{percentage}}%)`;
            
            if (checkedCount === totalItems) {{
                statusBar.classList.remove('status-incomplete');
                statusBar.classList.add('status-complete');
            }} else {{
                statusBar.classList.remove('status-complete');
                statusBar.classList.add('status-incomplete');
            }}
        }}

        // Adiciona entrada no log
        function addLogEntry(action) {{
            const now = new Date();
            const timestamp = now.toLocaleString('pt-BR');
            logEntries.push(`[${{timestamp}}] ${{action}}`);
            
            const logContainer = document.getElementById('logEntries');
            const entryElement = document.createElement('div');
            entryElement.className = 'log-entry';
            entryElement.textContent = logEntries[logEntries.length - 1];
            logContainer.appendChild(entryElement);
            logContainer.scrollTop = logContainer.scrollHeight;
        }}

        // Salva progresso no localStorage
        function saveProgress() {{
            const userData = {{
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            }};
            
            if (!userData.responsavel || !userData.cliente || !userData.numero_historia || 
                !userData.base_testes || !userData.arquivos_utilizados) {{
                alert('Por favor, preencha todos os campos antes de salvar!');
                return;
            }}
            
            localStorage.setItem('testProgress', JSON.stringify(testState));
            localStorage.setItem('userData', JSON.stringify(userData));
            
            addLogEntry('Progresso salvo com sucesso');
            alert('Progresso salvo com sucesso!');
        }}

        // Marca todos os itens
        function selectAllTests() {{
            testState = Array(totalItems).fill(true);
            document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                cb.checked = true;
            }});
            updateStatusBar();
            addLogEntry('Todos os itens foram marcados');
        }}

        // Exporta relatório completo em PDF
        function exportReport() {{
            const userData = {{
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            }};
            
            const completedItems = [];
            document.querySelectorAll('#testItemsContainer .checklist-item').forEach((item, i) => {{
                if (testState[i]) {{
                    completedItems.push(item.querySelector('label').textContent.trim());
                }}
            }});
            
            if (completedItems.length === 0) {{
                alert('Não há itens verificados para exportar!');
                return;
            }}
            
            alert("Funcionalidade de exportação PDF precisa ser integrada com o backend (Streamlit).");
            addLogEntry('Tentativa de exportar relatório de testes em PDF');
        }}

        // Exporta itens pendentes em PDF
        function exportPending() {{
            const userData = {{
                responsavel: document.getElementById('responsavel').value,
                data_teste: document.getElementById('data-teste').value,
                cliente: document.getElementById('cliente').value,
                numero_historia: document.getElementById('numero-historia').value,
                base_testes: document.getElementById('base-testes').value,
                arquivos_utilizados: document.getElementById('arquivos-utilizados').value
            }};
            
            const pendingItems = [];
            document.querySelectorAll('#testItemsContainer .checklist-item').forEach((item, i) => {{
                if (!testState[i]) {{
                    pendingItems.push(item.querySelector('label').textContent.trim());
                }}
            }});
            
            if (pendingItems.length === 0) {{
                alert('Não há itens pendentes para exportar!');
                return;
            }}
            
            alert("Funcionalidade de exportação PDF precisa ser integrada com o backend (Streamlit).");
            addLogEntry('Tentativa de exportar ajustes pendentes em PDF');
        }}

        // Reinicia todos os testes
        function resetTests() {{
            if (confirm('Tem certeza que deseja reiniciar todos os testes?')) {{
                testState = Array(totalItems).fill(false);
                document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                    cb.checked = false;
                }});
                updateStatusBar();
                addLogEntry('Todos os testes foram reiniciados');
            }}
        }}

        // Configura eventos
        document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
            cb.addEventListener('change', function() {{
                testState[i] = this.checked;
                updateStatusBar();
                const action = this.checked ? 'marcou' : 'desmarcou';
                const itemText = this.nextElementSibling.textContent.trim();
                addLogEntry(`${{action}} o item: ${{itemText}}`);
            }});
        }});

        // Inicializa
        window.onload = function() {{
            updateStatusBar();
        }};
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
                text_content = extract_text(uploaded_file)
                
                if text_content:
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    test_items_raw = [line.replace("- [ ]", "").replace("- [x]", "").strip() 
                                    for line in lines if len(line.split()) > 3][:50]
                    test_items = [item for item in test_items_raw if item]

                    if test_items:
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
                                data_teste_default = datetime.strptime(
                                    st.session_state.user_data['data_teste'], '%Y-%m-%d'
                                ) if st.session_state.user_data['data_teste'] else datetime.now()
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
                        
                        html_report = generate_html_report(
                            test_items=test_items, 
                            filename=uploaded_file.name,
                            initial_checks=[False] * len(test_items),
                            user_data=st.session_state.user_data
                        )
                        
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
                st.exception(e)

if __name__ == "__main__":
    main()