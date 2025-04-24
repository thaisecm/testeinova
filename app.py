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
    <!-- ... (código anterior mantido igual) ... -->
</head>
<body>
    <!-- ... (código anterior mantido igual) ... -->
</body>
</html>
    """
    return html_content

@st.cache_resource(experimental_allow_widgets=True)
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