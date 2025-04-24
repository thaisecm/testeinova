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
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        h1 {{
            color: var(--primary-color);
            font-size: 1.8rem;
        }}
        
        .info-section {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: var(--light-color);
            border-radius: 5px;
        }}
        
        .form-row {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .form-group {{
            flex: 1;
            min-width: 200px;
        }}
        
        .form-group-small {{
            flex: 0.5;
            min-width: 150px;
        }}
        
        .form-group-medium {{
            flex: 0.75;
            min-width: 180px;
        }}
        
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }}
        
        input[type="text"] {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 1rem;
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
                flex: 1