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

def generate_html_report(test_items, filename, initial_checks=None):
    """Gera um relatório HTML interativo"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Testes - {filename}</title>
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
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Relatório de Testes</h1>
        <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p>Arquivo original: {filename}</p>
    </div>

    <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>
    <div style="text-align: center; margin-bottom: 20px;">
        <span id="progressText">0% Concluído (0/{len(test_items)})</span>
    </div>

    <h2>Itens de Teste</h2>
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
        <button class="button" onclick="saveProgress()">Salvar Progresso</button>
        <button class="button" onclick="exportReport()">Exportar Relatório</button>
        <button class="button" onclick="clearLog()">Limpar Log</button>
        <button class="button" onclick="resetTests()">Reiniciar Testes</button>
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
            localStorage.setItem('testProgress', JSON.stringify(testState));
            localStorage.setItem('testLog', JSON.stringify(logEntries));
            addLogEntry('Progresso salvo');
            alert('Progresso salvo com sucesso!');
        }}

        // Exporta relatório
        function exportReport() {{
            const report = {{
                metadata: {{
                    title: 'Relatório de Testes',
                    date: new Date().toLocaleString('pt-BR'),
                    originalFile: '{filename}',
                    progress: (testState.filter(x => x).length / totalItems * 100).toFixed(2) + '%'
                }},
                testItems: testItems,
                log: logEntries
            }};
            
            const blob = new Blob([JSON.stringify(report, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'relatorio_testes_{filename.split('.')[0]}.json';
            a.click();
            addLogEntry('Relatório exportado');
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
            
            if (savedProgress) {{
                testState = JSON.parse(savedProgress);
                document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                    cb.checked = testState[i];
                }});
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
    st.set_page_config(page_title="Gerador de Testes Interativo", layout="centered")
    
    st.title("📋 Gerador de Testes Interativo")
    st.markdown("""
    ### Como usar:
    1. Faça upload de um arquivo DOCX ou PDF
    2. Aguarde o processamento
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
                        html_report = generate_html_report(test_items, uploaded_file.name)
                        
                        st.success("✅ Relatório interativo gerado com sucesso!")
                        st.balloons()
                        
                        st.download_button(
                            label="⬇️ Baixar Relatório HTML Interativo",
                            data=html_report,
                            file_name=f"relatorio_interativo_{uploaded_file.name.split('.')[0]}.html",
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