from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def criar_evento_google(token_info, agendamento):
    # token_info contém os tokens salvos no seu banco
    creds = Credentials(
        token=token_info.access_token,
        refresh_token=token_info.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="SEU_CLIENT_ID_DO_GOOGLE",
        client_secret="SEU_CLIENT_SECRET_DO_GOOGLE"
    )
    
    service = build('calendar', 'v3', credentials=creds)
    
    evento = {
        'summary': f'Barbearia: {agendamento.servico}',
        'description': f'Cliente: {agendamento.cliente_nome}',
        'start': {'dateTime': agendamento.data_hora.isoformat()},
        'end': {'dateTime': (agendamento.data_hora + timedelta(minutes=30)).isoformat()},
    }
    
    return service.events().insert(calendarId='primary', body=evento).execute()
    
def get_valid_creds(token_entry):
    creds = Credentials(
        token=token_entry.access_token,
        refresh_token=token_entry.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id="SEU_CLIENT_ID",
        client_secret="SEU_CLIENT_SECRET"
    )
    
    # Se o token expirou, renova automaticamente
    if creds.expired:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        # Opcional: Atualizar o banco com os novos tokens aqui
    return creds