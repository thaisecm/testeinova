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
    
    # ... (mantenha o resto da função generate_pdf_report igual) ...
    
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
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <!-- ... (mantenha todo o estilo CSS existente) ... -->
</head>
<body>
    {clear_storage_script}
    <div class="container">
        <!-- ... (mantenha o resto do HTML existente) ... -->
    </div>

    <script>
        // Inicializa variáveis
        const totalItems = {len(test_items)};
        let testState = {json.dumps(initial_checks)};
        let logEntries = ['Documento carregado'];

        // ... (mantenha todas as outras funções JavaScript existentes) ...

        // Modifique a função loadProgress para sempre começar com campos limpos
        function loadProgress() {{
            // SEMPRE COMEÇA COM LOG LIMPO
            logEntries = ['Documento carregado'];
            const logContainer = document.getElementById('logEntries');
            logContainer.innerHTML = '';
            const entryElement = document.createElement('div');
            entryElement.className = 'log-entry';
            entryElement.textContent = logEntries[0];
            logContainer.appendChild(entryElement);
            
            // Limpa todos os checks
            testState = Array(totalItems).fill(false);
            document.querySelectorAll('#testItemsContainer input[type="checkbox"]').forEach((cb, i) => {{
                cb.checked = false;
            }});
            
            // Limpa todos os campos do formulário
            document.getElementById('responsavel').value = '';
            document.getElementById('cliente').value = '';
            document.getElementById('numero-historia').value = '';
            document.getElementById('base-testes').value = '';
            document.getElementById('arquivos-utilizados').value = '';
            document.getElementById('data-teste').value = '{datetime.now().strftime('%Y-%m-%d')}';
            
            updateStatusBar();
        }}

        // ... (mantenha o resto do JavaScript existente) ...
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
                reset_user_data()
                
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
                                data_teste = st.date_input(
                                    "Data do Teste:",
                                    value=datetime.strptime(st.session_state.user_data['data_teste'], '%Y-%m-%d') if st.session_state.user_data['data_teste'] else datetime.now()
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
                            test_items, 
                            uploaded_file.name, 
                            user_data=st.session_state.user_data
                        )
                        
                        st.success("✅ Relatório interativo gerado com sucesso!")
                        
                        # Botão para download do HTML
                        st.download_button(
                            label="⬇️ Baixar Controle de Testes (HTML)",
                            data=html_report,
                            file_name=f"controle_testes_{uploaded_file.name.split('.')[0]}.html",
                            mime="text/html"
                        )
                        
                        # Botões para gerar PDFs diretamente
                        st.markdown("### Gerar Relatórios em PDF")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📄 Relatório Completo (Testes Validados)", 
                                       help="Gera PDF com todos os itens marcados como validados"):
                                completed_items = [
                                    item.replace("[ ]", "").replace("[x]", "") 
                                    for item in test_items 
                                ]
                                pdf_report = generate_pdf_report(
                                    completed_items,
                                    uploaded_file.name,
                                    st.session_state.user_data,
                                    completed_items=True
                                )
                                st.download_button(
                                    label="⬇️ Baixar Relatório Completo",
                                    data=pdf_report,
                                    file_name=f"relatorio_testes_{uploaded_file.name.split('.')[0]}.pdf",
                                    mime="application/pdf"
                                )
                        
                        with col2:
                            if st.button("⚠️ Ajustes Pendentes", 
                                       help="Gera PDF com itens não marcados (pendentes)"):
                                pending_items = [
                                    item.replace("[ ]", "").replace("[x]", "") 
                                    for item in test_items 
                                ]
                                pdf_report = generate_pdf_report(
                                    pending_items,
                                    uploaded_file.name,
                                    st.session_state.user_data,
                                    completed_items=False
                                )
                                st.download_button(
                                    label="⬇️ Baixar Ajustes Pendentes",
                                    data=pdf_report,
                                    file_name=f"ajustes_pendentes_{uploaded_file.name.split('.')[0]}.pdf",
                                    mime="application/pdf"
                                )
                            
                    else:
                        st.warning("Não foram identificados itens de teste no documento.")
                else:
                    st.error("Não foi possível extrair conteúdo do arquivo")
            
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main()