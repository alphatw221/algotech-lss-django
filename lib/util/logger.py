from prettytable import PrettyTable


def print_table(columns, rows):
    tab = PrettyTable(columns)
    tab.add_rows(rows)
    print(tab)