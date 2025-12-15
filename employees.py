"""
Módulo de Gerenciamento de Dados de Funcionários
=================================================

Responsável por carregar e validar dados da planilha de funcionários.

Autor: Núcleo Digital MG
Data: 2025-12-12
"""

import pandas as pd
import os

# Caminho para a planilha de funcionários
EMPLOYEES_FILE = os.path.join(os.path.dirname(__file__), 'FUNCIONARIO - Copia (1).xlsx')

# Domínio de email válido
VALID_EMAIL_DOMAIN = '@mendoncagalvao.com.br'


def load_employees_dataframe():
    """
    Carrega a planilha de funcionários e retorna um DataFrame.
    
    A planilha deve conter:
    - Coluna A: Nome dos funcionários
    - Coluna B: Email dos funcionários (com domínio completo)
    
    Returns:
        pd.DataFrame: DataFrame com colunas 'nome' e 'email'
        None: Se houver erro ao carregar a planilha
    """
    try:
        # Carregar planilha Excel
        df = pd.read_excel(
            EMPLOYEES_FILE,
            usecols=[0, 1],  # Colunas A e B
            names=['nome', 'email']  # Nomear as colunas
        )
        
        # Remover linhas com valores nulos
        df = df.dropna()
        
        # Converter emails para lowercase para comparação case-insensitive
        df['email'] = df['email'].str.lower().str.strip()
        
        # Remover duplicatas baseado no email
        df = df.drop_duplicates(subset=['email'])
        
        return df
    
    except FileNotFoundError:
        print(f"ERRO: Arquivo {EMPLOYEES_FILE} não encontrado.")
        return None
    except Exception as e:
        print(f"ERRO ao carregar planilha: {str(e)}")
        return None


def is_valid_email_domain(email):
    """
    Verifica se o email possui o domínio válido da empresa.
    
    Args:
        email (str): Email a ser validado
        
    Returns:
        bool: True se o email termina com @mendoncagalvao.com.br
    """
    if not email:
        return False
    
    email = email.lower().strip()
    return email.endswith(VALID_EMAIL_DOMAIN)


def is_employee_registered(email):
    """
    Verifica se o email está registrado na base de dados de funcionários.
    
    Args:
        email (str): Email a ser verificado
        
    Returns:
        bool: True se o email está na base de dados
    """
    df = load_employees_dataframe()
    
    if df is None:
        return False
    
    email = email.lower().strip()
    return email in df['email'].values


def get_employee_info(email):
    """
    Retorna informações do funcionário baseado no email.
    
    Args:
        email (str): Email do funcionário
        
    Returns:
        dict: Dicionário com 'nome' e 'email' do funcionário
        None: Se o funcionário não for encontrado
    """
    df = load_employees_dataframe()
    
    if df is None:
        return None
    
    email = email.lower().strip()
    employee = df[df['email'] == email]
    
    if employee.empty:
        return None
    
    return {
        'nome': employee.iloc[0]['nome'],
        'email': employee.iloc[0]['email']
    }


def get_all_employees():
    """
    Retorna lista de todos os funcionários cadastrados.
    
    Returns:
        list: Lista de dicionários com informações dos funcionários
        None: Se houver erro ao carregar
    """
    df = load_employees_dataframe()
    
    if df is None:
        return None
    
    return df.to_dict('records')
