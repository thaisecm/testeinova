# app.py
import streamlit as st
from docx import Document
import PyPDF2
from io import BytesIO
import json
from datetime import datetime

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

def generate_html_report(test_items, filename, initial_checks=None, user_data=None):
    """Gera um relatório HTML interativo"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    if user_data is None:
        user_data = {
            'tester': '',
            'client': '',
            'story_number': '',
            'test_base': '',
            'files_used': ''
        }
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Testes - {filename}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .header h1 {{
            color: #0054a6;
        }}
        .user-data {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .user-data-row {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }}
        .user-data-field {{
            flex: 1;
        }}
        .user-data label {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .user-data input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        .section-title {{
            color: #0054a6;
            border-bottom: 2px solid #0054a6;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        .test-item {{
            margin-bottom: 10px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            display: flex;
            align-items: center;
        }}
        .test-item input {{
            margin-right: 15px;
            transform: scale(1.5);
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #777;
            font-size: 0.9em;
        }}
        .progress-container {{
            margin: 20px 0;
            background-color: #f0f0f0;
            border-radius: 10px;
            height: 20px;
        }}
        .progress-bar {{
            height: 100%;
            border-radius: 10px;
            background-color: #4CAF50;
            width: 0%;
            transition: width 0.3s;
        }}
        .log-container {{
            margin-top: 30px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }}
        .log-entry {{
            margin: 5px 0;
            padding: 5px;
            font-size: 0.9em;
        }}
        .button {{
            padding: 10px 15px;
            margin: 5px;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }}
        .button-save {{
            background-color: #4CAF50;
        }}
        .button-export {{
            background-color: #ffc107;
        }}
        .button-clear {{
            background-color: #6c757d;
        }}
        .button-reset {{
            background-color: #dc3545;
        }}
        .button-select-all {{
            background-color: #28a745;
        }}
        .button-pending {{
            background-color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Controle de Testes</h1>
        <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p>Arquivo original: {filename}</p>
    </div>

    <div class="user-data">
        <div class="user-data-row">
            <div class="user-data-field">
                <label for="tester">Tester responsável:</label>
                <input type="text" id="tester" value="{user_data['tester']}">
            </div>
            <div class="user-data-field">
                <label for="client">Cliente:</label>
                <input type="text" id="client" value="{user_data['client']}">
            </div>
            <div class="user-data-field">
                <label for="story_number">Número da história:</label>
                <input type="text" id="story_number" value="{user_data['story_number']}">
            </div>
        </div>
        <div class="user-data-row">
            <div class="user-data-field">
                <label for="test_base">Base de testes:</label>
                <input type="text" id="test_base" value="{user_data['test_base']}">
            </div>
            <div class="user-data-field">
                <label for="files_used">Arquivos utilizados:</label>
                <input type="text" id="files_used" value="{user_data['files_used']}">
            </div>
        </div>
    </div>

    <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>
    <div style="text-align: center; margin-bottom: 20px;">
        <span id="progressText">0% Concluído (0/{len(test_items)})</span>
    </div>

    <h2 class="section-title">Checklist de validação</h2>
    <div id="testItemsContainer">
        {''.join([
            f'<div class="test-item"><input type="checkbox" id="item{i}" {"checked" if initial_checks[i] else ""}>'
            f'<label for="item{i}">{item.replace("[ ]", "").replace("[x]", "")}</label></div>'
            for i, item in enumerate(test_items)
        ])}
    </div>

    <div class="log-container">
        <h3>Log de Alterações</h3>
        <div id="logEntries"></div>
        <button class="button button-save" onclick="saveProgress()">Salvar Progresso</button>
        <button class="button button-export" onclick="exportReport()">Relatório de testes</button>
        <button class="button button-select-all" onclick="selectAllTests()">Marcar todos</button>
        <button class="button button-pending" onclick="exportPending()">Ajustes pendentes</button>
        <button class="button button-clear" onclick="clearLog()">Limpar Log</button>
        <button class="button button-reset" onclick="resetTests()">Reiniciar Testes</button>
    </div>

    <div class="footer">
        <p>Relatório gerado automaticamente</p>
    </div>

    <script>
        // Inicializa variáveis
        const totalItems = {len(test_items)};
        let testState = {json.dumps(initial_checks)};
        let logEntries = [];

        // Atualiza progresso
        function updateProgress() {{
            const checkedCount = testState.filter(x => x).length;
            const percentage = Math.round((checkedCount / totalItems) * 100);
            document.getElementById('progressBar').style.width = percentage + '%';
            document.getElementById('progressText').textContent = 
                percentage + '% Concluído (' + checkedCount + '/' + totalItems + ')';
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
        }}

        // Salva progresso no localStorage
        function saveProgress() {{
            const userData = {{
                tester: document.getElementById('tester').value,
                client: document.getElementById('client').value,
                story_number: document.getElementById('story_number').value,
                test_base: document.getElementById('test_base').value,
                files_used: document.getElementById('files_used').value
            }};
            
            // Valida campos obrigatórios
            if (!userData.tester || !userData.client || !userData.story_number || !userData.test_base || !userData.files_used) {{
                alert('Por favor, preencha todos os campos antes de salvar!');
                return;
            }}
            
            localStorage.setItem('testProgress', JSON.stringify(testState));
            localStorage.setItem('testLog', JSON.stringify(logEntries));
            localStorage.setItem('userData', JSON.stringify(userData));
            addLogEntry('Progresso salvo');
            alert('Progresso salvo com sucesso!');
        }}

        // Exporta relatório completo
        function exportReport() {{
            const userData = {{
                tester: document.getElementById('tester').value,
                client: document.getElementById('client').value,
                story_number: document.getElementById('story_number').value,
                test_base: document.getElementById('test_base').value,
                files_used: document.getElementById('files_used').value
            }};
            
            const report = {{
                metadata: {{
                    title: 'Controle de Testes',
                    date: new Date().toLocaleString('pt-BR'),
                    originalFile: '{filename}',
                    progress: (testState.filter(x => x).length / totalItems * 100).toFixed(2) + '%',
                    tester: userData.tester,
                    client: userData.client,
                    story_number: userData.story_number,
                    test_base: userData.test_base,
                    files_used: userData.files_used
                }},
                testItems: {json.dumps([item.replace("[ ]", "").replace("[x]", "") for item in test_items])},
                log: logEntries
            }};
            
            const blob = new Blob([JSON.stringify(report, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'controle_testes_{filename.split('.')[0]}.json';
            a.click();
            addLogEntry('Relatório completo exportado');
        }}

        // Exporta apenas itens pendentes
        function exportPending() {{
            const pendingItems = testState.map((checked, i) => !checked ? testItems[i] : null).filter(item => item !== null);
            
            if (pendingItems.length === 0) {{
                alert('Não há itens pendentes!');
                return;
            }}
            
            const report = {{
                pendingItems: pendingItems,
                totalPending: pendingItems.length,
                totalItems: totalItems
            }};
            
            const blob = new Blob([JSON.stringify(report, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ajustes_pendentes_{filename.split('.')[0]}.json';
            a.click();
            addLogEntry('Ajustes pendentes exportados');
        }}

        // Marca todos os itens
        function selectAllTests() {{
            testState = Array(totalItems).fill(true);
            document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                cb.checked = true;
            }});
            updateProgress();
            addLogEntry('Todos os itens marcados');
        }}

        // Limpa o log
        function clearLog() {{
            if (confirm('Tem certeza que deseja limpar o log?')) {{
                logEntries = [];
                document.getElementById('logEntries').innerHTML = '';
                addLogEntry('Log limpo');
            }}
        }}

        // Reinicia todos os testes
        function resetTests() {{
            if (confirm('Tem certeza que deseja reiniciar todos os testes?')) {{
                testState = Array(totalItems).fill(false);
                document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                    cb.checked = false;
                }});
                updateProgress();
                addLogEntry('Testes reiniciados');
            }}
        }}

        // Carrega progresso salvo
        function loadProgress() {{
            const savedProgress = localStorage.getItem('testProgress');
            const savedLog = localStorage.getItem('testLog');
            const savedUserData = localStorage.getItem('userData');
            
            if (savedProgress) {{
                testState = JSON.parse(savedProgress);
                document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                    cb.checked = testState[i];
                }});
            }}
            
            if (savedUserData) {{
                const userData = JSON.parse(savedUserData);
                document.getElementById('tester').value = userData.tester || '';
                document.getElementById('client').value = userData.client || '';
                document.getElementById('story_number').value = userData.story_number || '';
                document.getElementById('test_base').value = userData.test_base || '';
                document.getElementById('files_used').value = userData.files_used || '';
            }}
            
            if (savedLog) {{
                logEntries = JSON.parse(savedLog);
                const logContainer = document.getElementById('logEntries');
                logEntries.forEach(entry => {{
                    const entryElement = document.createElement('div');
                    entryElement.className = 'log-entry';
                    entryElement.textContent = entry;
                    logContainer.appendChild(entryElement);
                }});
            }}
            
            updateProgress();
        }}

        // Configura eventos
        document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
            cb.addEventListener('change', function() {{
                testState[i] = this.checked;
                updateProgress();
                addLogEntry(`Item ${{i+1}} - ${{this.checked ? 'marcado' : 'desmarcado'}}`);
            }});
        }});

        // Inicializa
        window.onload = function() {{
            loadProgress();
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
                    # Processa linhas relevantes
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    test_items = [f"- [ ] {line[:250]}" for line in lines if len(line.split()) > 3][:50]
                    
                    if test_items:
                        # Coleta informações adicionais do usuário
                        with st.expander("Informações do Teste", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                tester = st.text_input("Tester responsável:")
                                client = st.text_input("Cliente:")
                                story_number = st.text_input("Número da história:")
                            with col2:
                                test_base = st.text_input("Base de testes:")
                                files_used = st.text_input("Arquivos utilizados:")
                        
                        user_data = {
                            'tester': tester,
                            'client': client,
                            'story_number': story_number,
                            'test_base': test_base,
                            'files_used': files_used
                        }
                        
                        html_report = generate_html_report(test_items, uploaded_file.name, user_data=user_data)
                        
                        st.success("✅ Relatório interativo gerado com sucesso!")
                        st.balloons()
                        
                        st.download_button(
                            label="⬇️ Baixar Controle de Testes",
                            data=html_report,
                            file_name=f"controle_testes_{uploaded_file.name.split('.')[0]}.html",
                            mime="text/html"
                        )
                    else:
                        st.warning("Não foram identificados itens de teste no documento.")
                else:
                    st.error("Não foi possível extrair conteúdo do arquivo")
            
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main()