import os
import pandas as pd
from django.core.management.base import BaseCommand
from orders.models import Dish

class Command(BaseCommand):
    help = 'Importa platos desde un archivo .csv o .xlsx a la tabla Dish'

    def add_arguments(self, parser):
        parser.add_argument('file_path',
            help='Ruta al archivo .csv o .xlsx con columnas: id, nombre, categoria, descripcion, precio, imagen')

    def handle(self, *args, **options):
        path = options['file_path']
        ext  = os.path.splitext(path)[1].lower()

        if ext == '.csv':
            df = pd.read_csv(path)
        elif ext in ('.xls', '.xlsx'):
            df = pd.read_excel(path)
        else:
            self.stderr.write(self.style.ERROR("Formato no soportado. Usa .csv, .xls o .xlsx"))
            return

        created = updated = 0

        for _, row in df.iterrows():
            obj, was_created = Dish.objects.update_or_create(
                name=row['nombre'],
                defaults={
                    'category':    row.get('categoria',''),
                    'description': row.get('descripcion',''),
                    'price':       row['precio'],
                    'image_url':   row.get('imagen',''),
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Importación completada: {created} creados, {updated} actualizados.'
        ))
