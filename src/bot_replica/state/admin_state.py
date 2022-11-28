from typing import List

from src.bot_replica.entity.admin import Admin
from src.common.logger import Logger
from src.scraper.scraper import Scraper
 

class AdminState:
    __admins: List[Admin] = []

    def __init__(self) -> None:
        self.migrate()
        if len(self.__admins) > 0:
            Logger.info("init state: admins => %s", self.__admins)

    def set_admins(self, admins: List[Admin]) -> None:
        self.__admins = admins

    def get_admins(self) -> List[Admin]:
        return self.__admins

    def append_admin(self, admin: Admin) -> bool:
        if not self.__add_admin_to_db(admin):
            return False

        self.__admins.append(admin)
        Logger.info("added new admin id => {}, name => {}".format(
            admin.telegram_id, admin.name))

        return True

    def remove_admin(self, admin: Admin) -> None:
        try:
            self.__admins.remove(admin)
        except:
            pass

    def clear_admin(self) -> None:
        self.__admins = []

    def migrate_admins(self):
        try:
            rows = (Admin
                    .select()
                    )

            if len(rows) == 0:
                Logger.info("There is no Telegram admin in the DB")
            else:
                self.clear_admin()
                for row in rows:
                    self.__admins.append(row)

        except Exception as e:
            Logger.error(
                "there is an issue with the DB while migrating admin state", e)

    def __add_admin_to_db(self, admin: Admin) -> bool:
        try:
            count = (Admin
                     .select()
                     .where(Admin.telegram_id == admin.telegram_id)
                     .count()
                     )
            if count == 0:
                Logger.info("admin was already inserted")
                return False

            _ = (Admin
                 .create(name=admin.name, telegram_id=admin.telegram_id)
                 )
        except Exception as e:
            Logger.error(
                "there is an issue with the DB while adding a new admin", e)
            return False

        return True

    # lib
    def migrate(self):
        try:

            self.migrate_admins()

        except Exception as e:
            Logger.error(
                "there is an issue with the DB while migrating states", e)

   

    
