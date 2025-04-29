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
    """Gera um relatório HTML interativo com todos os recursos"""
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
    
    # Gera os itens do checklist com ações
    test_items_html = []
    for i, item in enumerate(test_items):
        item_text = item.replace("[ ]", "").replace("[x]", "").strip()
        checked_attr = "checked" if initial_checks[i] else ""
        item_html = f'''
        <div class="checklist-item" data-index="{i}">
            <input type="checkbox" id="item{i}" {checked_attr}>
            <label for="item{i}">{item_text}</label>
            <div class="item-actions">
                <button class="btn-edit" onclick="editItem({i})">✏️</button>
                <button class="btn-delete" onclick="deleteItem({i})">🗑️</button>
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
            border-bottom: none;
        }}
        
        .checklist-item {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background-color: white;
            transition: all 0.2s ease;
        }}
        
        .checklist-item:hover {{
            background-color: #f8f9fa;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .checklist-item input[type="checkbox"] {{
            margin-right: 12px;
            min-width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .checklist-item label {{
            font-weight: normal;
            cursor: pointer;
            flex-grow: 1;
            margin: 0;
            line-height: 1.5;
        }}

        .item-actions {{
            display: flex;
            gap: 8px;
            margin-left: 10px;
        }}

        .btn-edit, .btn-delete {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            padding: 5px;
            line-height: 1;
            border-radius: 4px;
            transition: all 0.2s;
        }}

        .btn-edit {{
            color: var(--warning-color);
        }}

        .btn-edit:hover {{
            background-color: rgba(255, 193, 7, 0.1);
        }}

        .btn-delete {{
            color: var(--danger-color);
        }}

        .btn-delete:hover {{
            background-color: rgba(220, 53, 69, 0.1);
        }}

        .btn-add-item {{
            background-color: var(--success-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }}

        .btn-add-item:hover {{
            background-color: #218838;
            transform: translateY(-1px);
        }}
        
        .status-bar {{
            margin: 20px 0;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            font-size: 1.1rem;
        }}
        
        .status-incomplete {{
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        
        .status-complete {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .buttons {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 25px 0;
        }}
        
        button {{
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            flex: 1;
            min-width: 180px;
        }}
        
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .btn-primary:hover {{
            background-color: #004494;
        }}
        
        .btn-success {{
            background-color: var(--success-color);
            color: white;
        }}
        
        .btn-success:hover {{
            background-color: #218838;
        }}
        
        .btn-danger {{
            background-color: var(--danger-color);
            color: white;
        }}
        
        .btn-danger:hover {{
            background-color: #c82333;
        }}
        
        .btn-warning {{
            background-color: var(--warning-color);
            color: #212529;
        }}
        
        .btn-warning:hover {{
            background-color: #e0a800;
        }}
        
        .btn-secondary {{
            background-color: var(--dark-color);
            color: white;
        }}
        
        .btn-secondary:hover {{
            background-color: #23272b;
        }}
        
        .log-container {{
            margin-top: 30px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            background-color: #f8f9fa;
        }}
        
        .log-entry {{
            margin-bottom: 8px;
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
            background-color: white;
            border-radius: 4px;
        }}
        
        footer {{
            margin-top: 40px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .form-row {{
                flex-direction: column;
                gap: 12px;
            }}
            
            .form-group, .form-group-small, .form-group-medium {{
                flex: 1;
                min-width: 100%;
            }}
            
            .buttons {{
                flex-direction: column;
                gap: 10px;
            }}
            
            button {{
                width: 100%;
                min-width: auto;
            }}
            
            .checklist-item {{
                padding: 10px 12px;
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
            <button class="btn-add-item"