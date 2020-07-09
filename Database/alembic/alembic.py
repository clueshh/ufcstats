import os
import alembic.config

os.chdir(os.pardir + '/' + os.pardir)


class Alembic:
    def __init__(self):
        pass

    @staticmethod
    def run(alembic_args):
        alembic.config.main(argv=['--raiseerr'] + alembic_args)

    def run_revision(self):
        """
        Creates an alembic revision file to the database

        :return:
        """

        self.run(['revision', '--autogenerate'])

    def run_upgrade(self):
        """
        Upgrades the head alembic revision

        :return:
        """

        self.run(['upgrade', 'head'])
