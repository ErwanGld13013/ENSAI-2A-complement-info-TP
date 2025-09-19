from typing import List, Optional
from dao.type_attack_dao import TypeAttackDAO
from utils.singleton import Singleton
from dao.db_connection import DBConnection
from business_object.attack.abstract_attack import AbstractAttack
from business_object.attack.attack_factory import AttackFactory


class AttackDao(metaclass=Singleton):
    def add_attack(self, attack: AbstractAttack) -> bool:
        """
        Add an attack to the database
        """
        created = False

        # Get the id type
        id_attack_type = TypeAttackDAO().find_id_by_label(attack.type)
        if id_attack_type is None:
            return created

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tp.attack (id_attack_type, attack_name,        "
                    " power, accuracy, element, attack_description)             "
                    "VALUES                                                     "
                    "(%(id_attack_type)s, %(name)s, %(power)s, %(accuracy)s,    "
                    " %(element)s, %(description)s)                             "
                    "RETURNING id_attack;",
                    {
                        "id_attack_type": id_attack_type,
                        "name": attack.name,
                        "power": attack.power,
                        "accuracy": attack.accuracy,
                        "element": attack.element,
                        "description": attack.description,
                    },
                )
                res = cursor.fetchone()
        if res:
            attack.id = res["id_attack"]
            created = True

        return created
    
    
    def find_attack_by_id(self, id_attaque: int) -> AbstractAttack:
        """
        Retourne l'attaque correspondante à son id
        """
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM tp.attack a2
                    INNER JOIN tp.attack_type at2 USING (id_attack_type)
                    WHERE a2.id_attack = %(id_attaque)s ;""",
                    {"id_attaque": id_attaque}
                )
                #Retourner le resultat
                result = cursor.fetchone()
            
            attack = None
            if result:
                attack = AttackFactory().instantiate_attack(
                    type = result["attack_type_name"],
                    id = result["id_attack"],
                    power = result["power"],
                    name = result["attack_name"],
                    description = result["attack_description"],
                    accuracy = result["accuracy"],
                    element = result["element"]
                )
            return attack

    def find_all_attack(self) -> List[AbstractAttack]:
        """
        Retourne l'attaque correspondante à son id
        """
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT * FROM tp.attack a2
                    INNER JOIN tp.attack_type at2 USING (id_attack_type);"""
                )
                #Retourner le resultat
                result = cursor.fetchall()
            
            all_attack = []
            if result:
                for attaq in result:

                    val = AttackFactory().instantiate_attack(
                        type = attaq["attack_type_name"],
                        id = attaq["id_attack"],
                        power = attaq["power"],
                        name = attaq["attack_name"],
                        description = attaq["attack_description"],
                        accuracy = attaq["accuracy"],
                        element = attaq["element"]
                    )
                    all_attack.append(val)

            return all_attack


if __name__ == "__main__":
    # Pour charger les variables d'environnement contenues dans le fichier .env
    import dotenv
    from business_object.attack.physical_attack import PhysicalFormulaAttack

    dotenv.load_dotenv(override=True)

    # Création d'une attaque et ajout en BDD
    mon_attaque = PhysicalFormulaAttack(
        power=50,
        name="chatouille",
        description="guili-guilis",
        accuracy=90,
        element="Normal",
    )

    #succes = AttackDao().add_attack(mon_attaque)
    #print("Attack created in database : " + str(succes))
    dao = AttackDao()
    test = dao.find_attack_by_id(3)
    print(test.power)
    test2 = dao.find_all_attack()
    print(test2[0].power)


