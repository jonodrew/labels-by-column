import json
import csv
from typing import List, Dict


class Card(object):
    def __init__(self, **data):
        self.labels: list = [label.get('id') for label in data.get('labels')]
        self.column_id = data.get('idList')


class Board(object):
    def __init__(self, trello_json_file_path: str):
        with open(trello_json_file_path, 'r') as trello_file:
            self.trello_content = json.load(trello_file)
        self.labels = {label.get('id'): label for label in self.trello_content.get('labels')}
        self.columns = {column.get('id'): column for column in self.trello_content.get('lists') if '/' in column.get('name')}  # all the columns we care about
        self.cards = filter(lambda x: x.column_id in self.columns.keys(), [Card(**card) for card in self.trello_content.get('cards')])


class Processor(object):
    def __init__(self, board: Board):
        self.board_to_process = board

    def labels_by_week(self):
        labels_by_week = {column_id: None for column_id in self.board_to_process.columns.keys()}
        for column_id in labels_by_week.keys():
            new_dict = {label_id: 0 for label_id in self.board_to_process.labels.keys()}
            labels_by_week[column_id] = new_dict
        for card in self.board_to_process.cards:
            for label in card.labels:
                labels_by_week[card.column_id][label] += 1
        return labels_by_week

    def convert_label_id_to_name(self, label_id):
        return self.board_to_process.labels.get(label_id).get('name')

    def convert_column_id_to_name(self, column_id):
        return self.board_to_process.columns.get(column_id).get('name')

    def process_labels_per_week(self) -> List[Dict]:
        machine_readable = self.labels_by_week()
        human_readable = []
        for column_id, label_count_by_id in machine_readable.items():
            new_dict = dict(
                week=self.convert_column_id_to_name(column_id=column_id),
                total=len([card for card in self.board_to_process.cards if card.column_id == column_id])
            )
            for label_id, count in label_count_by_id.items():
                new_dict[self.convert_label_id_to_name(label_id)] = count
            human_readable.append(new_dict)
        return human_readable

    def convert_to_csv(self):
        labels_per_week = self.process_labels_per_week()
        with open('sams-reading-analysis.csv', 'w') as csv_file:
            w = csv.DictWriter(csv_file, fieldnames=labels_per_week[0].keys())
            w.writeheader()
            w.writerows(labels_per_week)


def main():
    board = Board('sam-reading-board.json')
    processor = Processor(board)
    processor.convert_to_csv()


if __name__ == '__main__':
    main()
