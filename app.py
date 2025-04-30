# app.py (versão atualizada)
import streamlit as st
from docx import Document
import PyPDF2
from io import BytesIO
import json
from datetime import datetime
from fpdf import FPDF

# =============================================
# 1. CONSTANTES E CONFIGURAÇÕES
# =============================================

# Cenários de teste para cálculo de consumo
TEST_CASES = {
    "positive": [
        "Impedimento de envio online antes da finalização",
        "Cálculo automático ao finalizar carga",
        "Envio correto dos dados para Reader Web",
        "Integridade dos dados"
    ],
    "negative": [
        "Tentativa de envio online antes da finalização",
        "Finalização sem cálculo",
        "Dados incorretos no Reader Web",
        "Falha na comunicação"
    ]
}

# =============================================
# 2. FUNÇÕES EXISTENTES (MANTIDAS)
# =============================================

# [Todas as suas funções existentes permanecem aqui...]
# extract_text(), generate_pdf_report(), generate_html_report(), reset_user_data(), etc.

# =============================================
# 3. NOVAS FUNÇÕES PARA OS TESTES ESPECÍFICOS
# =============================================

def generate_test_cases_section():
    """Gera a seção de casos de teste específicos"""
    st.header("🧪 Testes Específicos - Cálculo de Consumo Mestre")
    
    with st.expander("📌 Critérios de Aceitação", expanded=False):
        st.markdown("""
        1. Sistema deve impedir envio online de ligações mestre antes da finalização
        2. Cálculo automático ao finalizar carga no Reader Android
        3. Reader Web deve receber dados corretamente calculados (sem valor -1)
        """)
    
    tab1, tab2 = st.tabs(["✅ Cenários Positivos", "❌ Cenários Negativos"])
    
    with tab1:
        st.markdown("#### Validação de Comportamentos Esperados")
        for i, case in enumerate(TEST_CASES["positive"], 1):
            with st.container(border=True):
                st.checkbox(f"{i}. {case}", key=f"pos_case_{i}")
                if st.session_state.get(f"pos_case_{i}"):
                    st.success("✅ Comportamento validado")
    
    with tab2:
        st.markdown("#### Validação de Tratamento de Erros")
        for i, case in enumerate(TEST_CASES["negative"], 1):
            with st.container(border=True):
                st.checkbox(f"{i}. {case}", key=f"neg_case_{i}")
                if st.session_state.get(f"neg_case_{i}"):
                    st.error("❌ Comportamento de erro tratado corretamente")

# =============================================
# 4. ATUALIZAÇÃO DA FUNÇÃO PRINCIPAL
# =============================================

def main():
    st.set_page_config(
        page_title="Controle de Testes Ampliado",
        layout="wide",
        page_icon="🧪"
    )
    
    # Sidebar com informações do projeto
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Quality+Control", width=150)
        st.title("Configurações")
        st.selectbox("Ambiente", ["DEV", "HOMOL", "PROD"])
        st.radio("Tipo de Teste", ["Funcional", "Regressão", "Integração"])
    
    # Área principal
    st.title("📋 Controle de Testes Ampliado")
    
    # Seção original (mantida)
    uploaded_file = st.file_uploader(
        "Arraste e solte seu arquivo de requisitos (DOCX/PDF)",
        type=['docx', 'pdf']
    )
    
    if uploaded_file:
        with st.spinner("Processando arquivo..."):
            try:
                text_content = extract_text(uploaded_file)
                
                if text_content:
                    # Seção original de processamento
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    test_items = [f"- [ ] {line[:250]}" for line in lines if len(line.split()) > 3][:50]
                    
                    # Layout em abas
                    tab_main, tab_specific = st.tabs(["📄 Testes Gerais", "🔍 Testes Específicos"])
                    
                    with tab_main:
                        # Conteúdo original da aplicação
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
                            with col2:
                                st.session_state.user_data['numero_historia'] = st.text_input(
                                    "Nº História:",
                                    value=st.session_state.user_data['numero_historia']
                                )
                                st.session_state.user_data['data_teste'] = st.date_input(
                                    "Data do Teste:",
                                    value=datetime.strptime(st.session_state.user_data['data_teste'], '%Y-%m-%d') if st.session_state.user_data['data_teste'] else datetime.now()
                                ).strftime('%Y-%m-%d')
                        
                        # Botões de ação originais
                        if st.button("Gerar Relatório HTML"):
                            html_report = generate_html_report(
                                test_items, 
                                uploaded_file.name,
                                user_data=st.session_state.user_data
                            )
                            st.download_button(
                                label="⬇️ Baixar Relatório",
                                data=html_report,
                                file_name=f"test_report_{uploaded_file.name.split('.')[0]}.html",
                                mime="text/html"
                            )
                    
                    with tab_specific:
                        # Nova seção para os testes específicos
                        generate_test_cases_section()
                        
                        # Relatório combinado
                        if st.button("Gerar Relatório Completo (PDF)"):
                            # Combina os testes gerais com os específicos
                            combined_items = test_items + [
                                f"- [{'x' if st.session_state.get(f'pos_case_{i}') else ' '}] {case}" 
                                for i, case in enumerate(TEST_CASES["positive"], 1)
                            ] + [
                                f"- [{'x' if st.session_state.get(f'neg_case_{i}') else ' '}] {case}" 
                                for i, case in enumerate(TEST_CASES["negative"], 1)
                            ]
                            
                            pdf_report = generate_pdf_report(
                                combined_items,
                                uploaded_file.name,
                                st.session_state.user_data,
                                completed_items=True
                            )
                            st.download_button(
                                label="⬇️ Baixar Relatório Completo",
                                data=pdf_report,
                                file_name=f"full_report_{uploaded_file.name.split('.')[0]}.pdf",
                                mime="application/pdf"
                            )
                
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")
    else:
        # Página inicial melhorada
        st.markdown("""
        ## Bem-vindo ao Sistema de Controle de Testes
            
        **Funcionalidades:**
        - ✅ Geração de checklists a partir de documentos
        - 🧪 Testes específicos para cálculo de consumo
        - 📊 Relatórios completos em HTML e PDF
            
        **Como usar:**
        1. Faça upload de um arquivo DOCX/PDF com os requisitos
        2. Preencha as informações do teste
        3. Execute os testes específicos
        4. Gere relatórios completos
        """)
        
        # Mostra os casos de teste mesmo sem arquivo carregado
        generate_test_cases_section()

if __name__ == "__main__":
    main()