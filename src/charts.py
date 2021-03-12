import re
from abc import ABC, abstractmethod
import ast
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import fig_to_img_buf
import logging
from globals import APP_NAME
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class Chart(ABC):
    def __init__(self):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._chart_type = str
        self._title = str
        self._df = None
        self._x_axis_title = str
        self._y_axis_title = str
        self._x_category_labels = []
        self._y_category_labels = []
        self._csv_chart_data_string = str
        self._html_chart_data_table = str
        self._png_img_buffer = None

    @abstractmethod
    def select_chart_data(self):
        pass

    @property
    def csv_chart_data_string(self):
        return self._csv_chart_data_string

    @property
    def html_chart_data_table(self):
        return self._html_chart_data_table

    @property
    def png_img_buffer(self):
        return self._png_img_buffer

    def make_html_chart_data_table(self):
        self._html_chart_data_table = self._df.to_html()

    def make_csv_chart_data_string(self):
        self._csv_chart_data_string = self._df.to_csv()

    @staticmethod
    def remove_chart_frame(ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return ax

    def set_title_and_axes(self, ax):
        ax.set_title(self._x_axis_title, y=-0.15, fontdict=None)
        ax.set_ylabel(self._y_axis_title)
        ax.set_ylim(self._df.min().min() * 0.9, self._df.max().max() * 1.1)
        return ax


class NSChart(Chart):
    def __init__(self, chart_html):
        super().__init__()
        self._chart_html = chart_html
        self.select_chart_data()
        self.__select_chart_titles()
        self.__plot_chart()
        self.make_csv_chart_data_string()
        self.make_html_chart_data_table()
        pass

    def __plot_chart(self):
        if self._chart_type == 'pie':
            self.__plot_pie_chart()
            return
        if self._chart_type == 'bar':
            self.__plot_bar_chart()
            return
        self.__plot_line_chart()

    def __select_chart_titles(self):
        raw_data = self._chart_html
        raw_data = raw_data.replace('&quot;', "'")
        raw_data = re.findall('{.*}', raw_data)[0]
        raw_data = raw_data.replace('true', 'True')
        raw_data = raw_data.replace('false', 'False')
        raw_data = ast.literal_eval(raw_data)
        self._chart_type = raw_data['chartType']
        self._title = raw_data['title']
        self._x_axis_title = raw_data['xAxisTitle']
        self._y_axis_title = raw_data['yAxisTitle']

    def select_chart_data(self):
        raw_data = re.findall('\[\[.*]]', self._chart_html)[0]
        raw_data = raw_data.replace('&quot;', "'")
        raw_data = ast.literal_eval(raw_data)
        self._x_category_labels = raw_data.pop(0)[1:]
        self._y_category_labels = [item.pop(0) for item in raw_data]
        df = pd.DataFrame(raw_data, columns=self._x_category_labels, index=self._y_category_labels)
        self._df = df

    def __plot_bar_chart(self):
        self.logger.info("Creating bar chart")
        df_transposed = self._df.copy().T
        fig2, ax = plt.subplots()
        ax = self.set_title_and_axes(ax)
        ax = self.remove_chart_frame(ax)
        plot = df_transposed.plot(kind='bar', grid=True, ax=ax, rot=0, title=self._title)
        fig = plot.get_figure()
        self._png_img_buffer = fig_to_img_buf(fig)

    @staticmethod
    def __format_data_for_pie_chart(plot_df):
        plot_df["sum"] = plot_df.sum(axis=1)
        plot_df["percent"] = plot_df["sum"] / plot_df["sum"].sum() * 100
        return plot_df

    def __plot_pie_chart(self):
        self.logger.info("Creating pie chart")
        plot_df = self.__format_data_for_pie_chart(self._df.copy())
        explode = [0.02 for x in range(len(plot_df.index))]
        fig, ax = plt.subplots()
        plt.title(self._title)
        plt.gca().axis("equal")
        pie = plt.pie(plot_df['sum'], autopct='%1.2f%%', pctdistance=1.2, explode=explode)
        labels = self._y_category_labels
        plt.legend(pie[0], labels, bbox_to_anchor=(1, 1), loc="upper right",
                   bbox_transform=plt.gcf().transFigure)
        self._png_img_buffer = fig_to_img_buf(fig)

    def __plot_line_chart(self):
        self.logger.info("Creating line chart")
        df_transposed = self._df.copy().T
        fig2, ax = plt.subplots()
        ax = self.set_title_and_axes(ax)
        ax = self.remove_chart_frame(ax)
        x_ticks = [x for x in range(len(df_transposed.index))]
        plot = df_transposed.plot(kind='line', grid=True, ax=ax, rot=0, xticks=x_ticks, title=self._title)
        fig = plot.get_figure()
        self._png_img_buffer = fig_to_img_buf(fig)
