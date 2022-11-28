from typing import List

from src.bot_replica.entity.announcement import Announcement
from src.common.logger import Logger
from src.scraper.scraper import Scraper
 

class AnnouncementState:
    __last_announcement: Announcement = Announcement(announcement=-1)

    def __init__(self) -> None:
        self.migrate()
        Logger.info("init state: announcement => %s", self.__last_announcement)

    def set_last_announcement(self, last_announcement: int) -> bool:
        announcement = Announcement(announcement=last_announcement)
        if last_announcement == self.__last_announcement.announcement:
            return True

        if not self.__set_announcement_to_db(announcement):
            return False

        Logger.info("new announcement set before => {}, after = {}".format(self.__last_announcement, announcement))
        self.__last_announcement = announcement
        return True

    def get_last_announcement(self) -> Announcement:
        return self.__last_announcement

    def get_last_announcement_as_id(self):
        return self.__last_announcement.announcement

    def migrate_last_announcement(self):
        try:
            row = (Announcement
                   .select()
                   .order_by(Announcement.id.desc())
                   .limit(1)
                   )

            if len(row) == 0:
                last_announcement = Scraper.get_last_announcement_id()
                announcement = Announcement(announcement=last_announcement)
                if last_announcement == -1:
                    pass

                if self.__set_announcement_to_db(announcement):
                    self.__last_announcement = announcement
                else:
                    self.__last_announcement = Announcement(announcement=-1)
            else:
                self.__last_announcement = row[0]

        except Exception as e:
            Logger.error(
                "there is an issue with the DB while migrating announcement state", e)

    def __set_announcement_to_db(self, last_announcement: Announcement) -> bool:
        try:
            count = (Announcement
                     .select()
                     .count()
                     )
            if count == 0:
                _ = (Announcement
                      .create(announcement=last_announcement.announcement)
                      )
            else:
                _ = (Announcement
                        .update(announcement=last_announcement.announcement)
                        .order_by(Announcement.id.desc())
                        .limit(1)
                        .execute()
                        )

        except Exception as e:
            Logger.error(
                "there is an issue with the DB while setting new announcement", e)
            return False

        return True

    # lib
    def migrate(self):
        try:

            self.migrate_last_announcement()

        except Exception as e:
            Logger.error(
                "there is an issue with the DB while migrating states", e)
