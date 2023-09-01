# TODO

Implementer des logs au niveau des parties sensibles

Faire des tests sur les nouvelles parties de l'app : faire ça avec un bdd vierge

Essayer de recupérer les modifs faites sur le github (voir avec nicolas)

## Essayer de voir ces modifs la : 

/home/josue/.local/lib/python3.10/site-packages/django/db/models/fields/__init__.py:1474: RuntimeWarning: DateTimeField Sale.datetime received a naive datetime (2023-09-01 00:00:00) while time zone support is active.

Le message d'avertissement que vous voyez, "DateTimeField BillsEntry.datetime received a naive datetime while time zone support is active," indique que vous utilisez des objets datetime "naïfs" (sans informations de fuseau horaire) dans vos modèles Django alors que le support des fuseaux horaires est activé dans votre application Django.

L'activation du support des fuseaux horaires est une bonne pratique pour gérer correctement les dates et heures, en particulier lorsque vous avez des utilisateurs ou des serveurs situés dans différents fuseaux horaires. Cela garantit que les informations sur les dates et heures sont stockées et manipulées de manière cohérente.

Pour résoudre ces avertissements, vous devez vous assurer que les objets datetime utilisés dans vos modèles sont dotés d'informations de fuseau horaire. Vous pouvez le faire en utilisant la classe timezone de Django pour créer des objets datetime avec le fuseau horaire approprié.

Voici un exemple de modification de votre modèle BillsEntry pour utiliser des objets datetime avec des fuseaux horaires :

python
Copy code
from django.db import models
from django.utils import timezone

class BillsEntry(models.Model):
    # ...

    datetime = models.DateTimeField("Date", default=timezone.now)
    # Utilisez timezone.now au lieu de now pour obtenir la date et l'heure actuelles avec le fuseau horaire actif.

    # ...
Faites de même pour tout autre modèle où vous utilisez des champs DateTimeField. En utilisant timezone.now au lieu de now, vous vous assurez que les objets datetime sont créés avec le fuseau horaire actif, ce qui évitera les avertissements liés aux objets "naïfs".