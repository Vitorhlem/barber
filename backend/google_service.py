import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def get_valid_creds(token_entry):
    # Use variáveis de ambiente para segurança
    creds = Credentials(
        token=token_entry.access_token,
        refresh_token=token_entry.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )
    
    if creds.expired:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    return creds

def criar_evento_google(token_entry, agendamento):
    creds = get_valid_creds(token_entry)
    service = build('calendar', 'v3', credentials=creds)
    
    evento = {
        'summary': f'Atendimento: {agendamento.servico}',
        'description': f'Cliente: {agendamento.cliente_nome}',
        'start': {'dateTime': agendamento.data_hora.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': (agendamento.data_hora + timedelta(minutes=30)).isoformat(), 'timeZone': 'America/Sao_Paulo'},
    }
    
    return service.events().insert(calendarId='primary', body=evento).execute()