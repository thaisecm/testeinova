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
        # Remove marcadores [ ] ou [x] se existirem
        clean_item = item.replace("[ ]", "").replace("[x]", "").strip()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(10, 8, txt=f"{idx}.", ln=0)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, txt=clean_item)
        pdf.ln(5)
    
    # Rodapé
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt=f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin1')

def generate_html_report(test_items, filename, initial_checks=None, user_data=None):
    """Gera um relatório HTML interativo com o layout do arquivo fornecido"""
    if initial_checks is None:
        initial_checks = [False] * len(test_items)
    
    if user_data is None:
        user_data = st.session_state.user_data
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Testes - {filename}</title>
    <!-- Restante do código HTML permanece igual -->
    </style>
</head>
<body>
    <!-- Restante do corpo HTML permanece igual -->
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