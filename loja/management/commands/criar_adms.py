from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from loja.models import Perfil

class Command(BaseCommand):
    help = 'Cria usuários ADM para teste do sistema de chat'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=3,
            help='Número de ADMs a criar (padrão: 3)',
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        
        self.stdout.write(
            self.style.SUCCESS(f'Criando {quantidade} usuários ADM...')
        )
        
        for i in range(1, quantidade + 1):
            username = f'adm{i}'
            email = f'adm{i}@atelier.com'
            
            # Criar usuário ADM
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                user.set_password('123456')  # Senha simples para teste
                user.save()
                
                # Criar perfil
                Perfil.objects.get_or_create(
                    user=user,
                    defaults={
                        'cpf': f'000.000.000-0{i}',
                        'telefone': f'(81) 99999-000{i}',
                        'endereco': f'Endereço ADM {i}',
                        'cep': '50000-000'  # Campo obrigatório
                    }
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criado ADM: {username} (senha: 123456)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✗ ADM {username} já existe')
                )
        
        total_adms = User.objects.filter(is_staff=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de ADMs no sistema: {total_adms}')
        )
        self.stdout.write(
            self.style.SUCCESS('Para logar como ADM, use: username=adm1, senha=123456')
        )