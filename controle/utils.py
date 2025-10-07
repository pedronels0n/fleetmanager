import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv




def grupo_administrador(user):
    return user.groups.filter(name='Administrador').exists()

