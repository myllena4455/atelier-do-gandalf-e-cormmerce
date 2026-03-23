import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import mercadopago # Importação do Mercado Pago

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configurações de Segurança
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

# 3. Aplicações Instaladas
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'loja', # Sua aplicação
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 4. Banco de Dados Neon
# DATABASES = {
#     'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. API Mercado Pago
MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_TOKEN = os.getenv('MERCADO_PAGO_TOKEN')

# O SDK usa apenas o TOKEN (a secreta)
# sdk = mercadopago.SDK(MERCADO_PAGO_TOKEN)

# 6. API Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET')
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# 7. Configuração Melhor Envio (Salvamos o Token para usar nas views)
MELHOR_ENVIO_TOKEN = os.getenv('MELHOR_ENVIO_TOKEN')
MELHOR_ENVIO_URL = "https://sandbox.melhorenvio.com.br" # Use sandbox para testes

# Para o Django entender onde ficam as fotos de produtos e perfis
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')