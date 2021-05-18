import os
import typing

import click
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt

VelocityData = typing.List[typing.List[float]]


class VelocityChart:
    car: pd.DataFrame
    autonomous: pd.DataFrame
    conventional: pd.DataFrame
    emergency: pd.DataFrame

    def __init__(self, car: VelocityData, autonomous: VelocityData, conventional: VelocityData, emergency: VelocityData):
        self.car = pd.DataFrame(car)
        self.autonomous = pd.DataFrame(autonomous)
        self.conventional = pd.DataFrame(conventional)
        self.emergency = pd.DataFrame(emergency)

    def show(self, only_data: bool) -> None:
        click.secho('Average speed', fg='yellow')
        print(self.car.to_csv())
        click.secho('Autonomous speed', fg='yellow')
        print(self.autonomous.to_csv())
        click.secho('Conventional speed', fg='yellow')
        print(self.conventional.to_csv())
        click.secho('Emergency speed', fg='yellow')
        print(self.emergency.to_csv())
        if not only_data:
            self._prepareChart()
            plt.show()

    def save(self, path: str, prefix: str, only_data: bool) -> None:
        car_path = os.path.join(path, f'{prefix}_car.csv')
        self.car.to_csv(car_path)
        autonomous_path = os.path.join(path, f'{prefix}_autonomous.csv')
        self.autonomous.to_csv(autonomous_path)
        conventional_path = os.path.join(path, f'{prefix}_conventional.csv')
        self.conventional.to_csv(conventional_path)
        emergency_path = os.path.join(path, f'{prefix}_emergency.csv')
        self.emergency.to_csv(emergency_path)
        if not only_data:
            self._prepareChart()
            plt_path = os.path.join(path, f'{prefix}.png')
            plt.savefig(plt_path, bbox_inches='tight')

    def _prepareChart(self) -> None:
        plt.figure(figsize=(6, 4))
        sns.set_style('darkgrid')
        data = pd.DataFrame({
            'All': self.car.sum(axis=0) / self.car.shape[0],
            'Autonomous': self.autonomous.sum(axis=0) / self.autonomous.shape[0],
            'Conventional': self.conventional.sum(axis=0) / self.conventional.shape[0],
            'Emergency': self.emergency.sum(axis=0) / 1 })

        ax = sns.lineplot(data=data)
        ax.set(ylabel='Speed', xlabel='Position', title='Average speed on the road\n')
