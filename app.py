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
    """Gera um relatório HTML interativo com o novo design"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    if user_data is None:
        user_data = {
            'responsavel': '',
            'cliente': '',
            'numero_historia': '',
            'base_testes': '',
            'arquivos_utilizados': ''
        }
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Testes - {filename}</title>
    <style>
        /* ... (mantenha todos os estilos existentes) ... */
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Controle de Testes</h1>
            <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>Arquivo original: {filename}</p>
        </header>
        
        <div class="info-section">
            <div class="form-row">
                <div class="form-group">
                    <label for="responsavel">Responsável pelo Teste:</label>
                    <input type="text" id="responsavel" value="{user_data['responsavel']}" placeholder="Digite seu nome">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="base-testes">Base de Testes:</label>
                    <input type="text" id="base-testes" value="{user_data['base_testes']}" placeholder="Digite a base de testes">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="cliente">Cliente:</label>
                    <input type="text" id="cliente" value="{user_data['cliente']}" placeholder="Digite o nome do cliente">
                </div>
                <div class="form-group">
                    <label for="numero-historia">Número da História:</label>
                    <input type="text" id="numero-historia" value="{user_data['numero_historia']}" placeholder="Digite o número da história">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="arquivos-utilizados">Arquivos Utilizados:</label>
                    <input type="text" id="arquivos-utilizados" value="{user_data['arquivos_utilizados']}" placeholder="Digite os arquivos utilizados">
                </div>
            </div>
        </div>
        
        <!-- ... (restante do conteúdo permanece igual) ... -->
    </div>

    <script>
        // ... (mantenha todo o JavaScript existente) ...
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
                    test_items = [f"- [ ] {line[:250]}" for line in lines if len(line.split()) > 3][:50]
                    
                    if test_items:
                        with st.expander("Informações do Teste", expanded=True):
                            st.text_input("Responsável pelo Teste:", key="responsavel", placeholder="Digite seu nome", max_chars=15)
                            st.text_input("Base de Testes:", key="base_testes", placeholder="Digite a base de testes")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.text_input("Cliente:", key="cliente", placeholder="Digite o nome do cliente", max_chars=20)
                            with col2:
                                st.text_input("Número da História:", key="numero_historia", placeholder="Digite o número da história")
                            st.text_input("Arquivos Utilizados:", key="arquivos_utilizados", placeholder="Digite os arquivos utilizados")
                        
                        user_data = {
                            'responsavel': st.session_state.responsavel,
                            'cliente': st.session_state.cliente,
                            'numero_historia': st.session_state.numero_historia,
                            'base_testes': st.session_state.base_testes,
                            'arquivos_utilizados': st.session_state.arquivos_utilizados
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