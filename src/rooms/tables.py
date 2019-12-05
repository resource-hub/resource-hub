import django_tables2 as tables


class RoomsTable(tables.Table):
    name = tables.Column()

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }
