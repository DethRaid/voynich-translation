"""Generates a table in LaTeX for a set of data
"""
import json


def make_table(data):
    """Generates a table from the given data
    
    :param data: The data to generate the table from. The data should be a dictionary of dictionaries, where the keys in
     each dictionary are the headings for the table
    :return: The table as a string
    """

    table_str = '\\begin{table}[h]\n\\begin{center}\n\\begin{tabular}{|l|'

    for i in range(len(data)):
        table_str += 'l|'

    table_str += '}\n\\hline \\bf Language'

    for key, _ in sorted(data.items()):
        table_str += ' & {}'.format(key)

    table_str += '\\\\ \\hline\n'

    for language1, data1 in sorted(data.items()):
        table_str += language1 + '\t'
        for _, data2 in sorted(data1.items()):
            # If [0] is small or [1] is high, we cannot reject the hypothesis that both distributions are two samples
            # of the same distribution
            # If the p-value is below 1%, we can reject the hull hypothesis (there is no significant difference between
            # distribution B and distribution B
            # If the p-value is higher than 10%, we cannot reject the null hypothesis with 10% or lower alpha
            # Given alpha a, we cannot reject the null hypothesis if the p-value is higher than a (I think?)
            if data2[1] > 0.1 and data2[1] < 1.0:
                table_str += ' & \\bf{:1.3f}'.format(data2[1])
            else:
                table_str += '\t & {:1.3f}'.format(data2[1])
        table_str += ' \\\\\n'

    table_str += '\\hline\n\\end{tabular}\n\\end{center}\n\\caption{\label{table:grams-ks} KS-similarity for the different character statistics }\n\\end{table}\n'

    return table_str


if __name__ == '__main__':
    with open('similarities.json', 'r') as jsonfile:
        all_data = json.load(jsonfile)

        for stat, data in all_data.items():
            print('Data for language ' + stat)
            print(make_table(data))