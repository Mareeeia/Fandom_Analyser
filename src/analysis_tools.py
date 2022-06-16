import json
import pandas as pd
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import networkx as nx
from pathlib import Path


class FandomAnalysisTools:

    logger_analysis = logging.getLogger("analysis")

    VALID_CATEGORIES = []
    VALID_CHARACTERS = []
    VALID_TIME = []
    VALID_RATING = []

    def __init__(self, fandom_name):
        self.fandom = fandom_name
        self.logger_analysis.info('Init analyzer.')

    def plot_bars_time(self, data, character='all', category='all', time='month', rating='all'):
        self.logger_analysis.info('Plotting data vs time ' + time)
        df = pd.DataFrame.from_dict(data, orient='index')

        df = self.select_for_character(df, character)

        df = self.select_for_category(df, category)

        df = self.select_for_rating(df, rating)

        df = self.aggregate_for_time(df, time)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.bar(df.index, df['count'], width=25, align='center')

        plt.axhline(y=df['count'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_new_works_count_by_' + time + '.png')
        plt.show()

    def aggregate_for_time(self, df, time='month'):
        if time == 'month':
            df['date_updated'] = pd.to_datetime(df['date_updated'])
            df['month_updated'] = df['date_updated'].apply(lambda x: '%d-%d' % (x.month, x.year))
            df['month_updated'] = pd.to_datetime(df['month_updated'], infer_datetime_format=True)
            df = df['title'].groupby(df['month_updated']).agg(["count"])
            df.columns = ["".join(x) for x in df.columns.ravel()]
        if time == 'day':
            df['date_updated'] = pd.to_datetime(df['date_updated'])
            df = df['title'].groupby(df['date_updated']).agg(["count"])
            df.columns = ["".join(x) for x in df.columns.ravel()]
        if time == 'year':
            df['date_updated'] = pd.to_datetime(df['date_updated'])
            df['year_updated'] = df['date_updated'].apply(lambda x: '%d' % (x.year))
            df['year_updated'] = pd.to_datetime(df['year_updated'], infer_datetime_format=True)
            df = df['title'].groupby(df['year_updated']).agg(["count"])
            df.columns = ["".join(x) for x in df.columns.ravel()]
        return df

    def plot_bars_tag(self, data):
        self.logger_analysis.info('Plotting data versus a single tag')

    def plot_stacked_bars(self, array_of_data, normalized=True):
        self.logger_analysis.info('Plotting stacked bar from data array')

    def plot_pie_chart(self, data, colors):
        self.logger_analysis.info('Plotting pie chart')

    def plot_star_graph(self, data, labels):
        self.logger_analysis.info('Plotting star graph')

    def plot_network(self, data, edge_count=3):
        self.logger_analysis.info('Plotting full network')

    def prepare_analytics_folders(self):
        ppath = Path('./fandom_extracted_data/' + self.fandom + '/plots')
        ppath.mkdir(exist_ok=True)

    def get_top_characters(self, d, count=0):
        df = pd.DataFrame.from_dict(d, orient='index')
        df = df['characters'].explode().value_counts().rename_axis('Characters').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        if count > 0:
            df = df.head(count)
        else:
            df = df[is_large]
        return df['Characters'].values

    def get_top_tags(self, d, count=0):
        df = pd.DataFrame.from_dict(d, orient='index')
        df = df['tags'].explode().value_counts().rename_axis('Tags').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        if count > 0:
            df = df.head(count)
        else:
            df = df[is_large]
        return df['Tags'].values

    def get_top_ships(self, d, count=0):
        df = pd.DataFrame.from_dict(d, orient='index')
        df = df['relationships'].explode().value_counts().rename_axis('Ships').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        if count > 0:
            df = df.head(count)
        else:
            df = df[is_large]
        return df['Ships'].values

    def plot_new_works_count_by_month(self, d):
        df = pd.DataFrame.from_dict(d, orient='index')
        df['date_updated'] = pd.to_datetime(df['date_updated'])
        df['month_updated'] = df['date_updated'].apply(lambda x: '%d-%d' % (x.month, x.year))
        df['month_updated'] = pd.to_datetime(df['month_updated'], infer_datetime_format=True)
        df = df['title'].groupby(df['month_updated']).agg(["count"])
        df.columns = ["".join(x) for x in df.columns.ravel()]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.bar(df.index, df['count'], width=25, align='center')

        plt.axhline(y=df['count'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_new_works_count_by_month.png')
        plt.show()

    def plot_new_works_count_by_month_ratings(self, d):
        df = pd.DataFrame.from_dict(d, orient='index')
        df['date_updated'] = pd.to_datetime(df['date_updated'])
        df['month_updated'] = df['date_updated'].apply(lambda x: '%d-%d' % (x.month, x.year))
        df['month_updated'] = pd.to_datetime(df['month_updated'], infer_datetime_format=True)
        df_segmented = df['title'].groupby([df['rating'], df['month_updated']]).agg(["count"])
        df = df['title'].groupby(df['month_updated']).agg(["count"])
        df.columns = ["".join(x) for x in df.columns.ravel()]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        pd.set_option('display.max_rows', None)

        ds = []
        cols = ["Explicit", "Not Rated", "Mature", "Teen And Up Audiences", "General Audiences"]
        categories = []
        for col in cols:
            if col in df_segmented.T:
                d = df_segmented.loc[col]['count']
                d = df.merge(d, how='outer', left_index=True, right_index=True).fillna(0)
                d['count_y'] = d['count_y'] / df['count']
                ds.append(d)
                categories.append(col)

        fig, ax = plt.subplots(figsize=(40, 9))
        fig.subplots_adjust(bottom=0.3)

        ps = []
        compound_sum = None
        colours = ['tab:green', 'tab:blue', 'tab:orange', 'tab:red', 'tab:purple']
        for i in range(len(ds)):
            if compound_sum is not None:
                ps.append(ax.bar(ds[i].index, ds[i]['count_y'], width=25, bottom=compound_sum, align='center', color=colours[i]))
                compound_sum += ds[i]['count_y']
            else:
                ps.append(ax.bar(ds[i].index, ds[i]['count_y'], width=25, align='center', color=colours[i]))
                compound_sum = ds[i]['count_y']
        plt.legend(ps, categories)
        # plt.axhline(y=df['count'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('../src/fandom_extracted_data/' + self.fandom + '/plots/plot_new_works_count_by_month.png')
        plt.show()

    def plot_chars_ratings(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df.explode('characters')
        df_segmented = df['title'].groupby([df['rating'], df['characters']]).agg(["count"])
        df = df['title'].groupby(df['characters']).agg(["count"])
        is_small = df['count'] < 3
        df.columns = ["".join(x) for x in df.columns.ravel()]
        de_exc = df[is_small]

        self.logger_analysis.info(de_exc.index)

        pd.set_option('display.max_rows', None)
        d1 = df_segmented.loc["Explicit"]['count']
        d1 = df.merge(d1, how='outer', left_index=True, right_index=True).fillna(0)
        d1['count_y'] = d1['count_y'] / df['count']
        d1 = d1.drop(de_exc.index)

        d2 = df_segmented.loc["Not Rated"]['count']
        d2 = df.merge(d2, how='outer', left_index=True, right_index=True).fillna(0)
        d2['count_y'] = d2['count_y'] / df['count']
        d2 = d2.drop(de_exc.index)

        d3 = df_segmented.loc["Mature"]['count']
        d3 = df.merge(d3, how='outer', left_index=True, right_index=True).fillna(0)
        d3['count_y'] = d3['count_y'] / df['count']
        d3 = d3.drop(de_exc.index)

        d4 = df_segmented.loc["Teen And Up Audiences"]['count']
        d4 = df.merge(d4, how='outer', left_index=True, right_index=True).fillna(0)
        d4['count_y'] = d4['count_y'] / df['count']
        d4 = d4.drop(de_exc.index)

        d5 = df_segmented.loc["General Audiences"]['count']
        d5 = df.merge(d5, how='outer', left_index=True, right_index=True).fillna(0)
        d5['count_y'] = d5['count_y'] / df['count']
        d5 = d5.drop(de_exc.index)

        self.logger_analysis.debug(df)
        # ax.bar(ind, d1, color='g')
        fig, ax = plt.subplots(figsize=(40, 9))
        fig.subplots_adjust(bottom=0.3)
        plt.xticks(rotation='vertical')
        p5 = ax.bar(d5.index, d5['count_y'], align='center', color='tab:green')
        p4 = ax.bar(d4.index, d4['count_y'], bottom=d5['count_y'], align='center', color='tab:blue')
        p3 = ax.bar(d3.index, d3['count_y'], bottom=d5['count_y'] + d4['count_y'], align='center', color='tab:orange')
        p1 = ax.bar(d1.index, d1['count_y'], bottom=d5['count_y'] + d4['count_y'] + d3['count_y'], align='center',
                    color='tab:red')
        p2 = ax.bar(d2.index, d2['count_y'], bottom=d5['count_y'] + d4['count_y'] + d3['count_y'] + d1['count_y'],
                    align='center', color='tab:purple')
        plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0]),
                   ('Explicit', 'Not Rated', 'Mature', 'Teen And Up', 'General Audiences'))
        # plt.axhline(y=df['count'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_chars_rating.png')
        plt.show()

    def plot_works_count_by_character(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df['characters'].explode().value_counts().rename_axis('Characters').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df.plot(x='Characters', kind='bar', figsize=(20, 8))
        plt.axhline(y=df[is_large]['Fanfic Counts'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_character.png')
        plt.show()

    def plot_works_count_by_ship(self, d):
        df = pd.DataFrame.from_dict(d).T
        df['relationships'] = df['relationships'].apply(lambda x: self.remdup(x))
        df = df['relationships'].explode().value_counts().rename_axis('Ships').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 1
        pd.set_option('display.max_rows', None)
        df = df[is_large]
        self.logger_analysis.debug(df)
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df.plot(x='Ships', kind='bar', figsize=(20, 9))
        plt.subplots_adjust(bottom=0.3)
        plt.axhline(y=df['Fanfic Counts'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_ship.png')
        plt.show()

    def plot_works_count_by_main_character(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df['main_characters'].explode().value_counts().rename_axis('Main Characters').reset_index(
            name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 3
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df[is_large].plot(x='Main Characters', kind='bar', figsize=(20, 8))
        plt.axhline(y=df[is_large]['Fanfic Counts'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_main_character.png')
        plt.show()

    def plot_average_hits_character(self, data):
        df = pd.DataFrame.from_dict(data).T
        df['hits'] = df['hits'].astype(float)
        df = df.explode("characters")[["characters", "hits"]].groupby("characters").agg(["count", "mean"])
        df = df['hits'].sort_values(by='mean')
        is_large = df['count'] > 3
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df[is_large]['mean'].plot(kind='bar')
        plt.axhline(y=df[is_large]['mean'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_average_hits_character.png')
        plt.show()

    def plot_average_hits_ships_character(self, d, char):
        df = pd.DataFrame.from_dict(d).T
        df['relationships'] = df['relationships'].apply(lambda x: self.remdup(x))
        df = df.explode('relationships').fillna(0)
        has_ship = df['relationships'] != 0
        df = df[has_ship]
        contains_char = df['relationships'].apply(lambda x: char in x)
        df = df[contains_char]
        df['hits'] = df['hits'].astype(float)
        df = df.explode("relationships")[["relationships", "hits"]].groupby("relationships").agg(["count", "mean"])
        df = df.drop(char)
        df = df['hits'].sort_values(by='mean')
        is_large = df['count'] > 1
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df = df[is_large]
        df['mean'].plot(kind='bar', figsize=(12, 8))
        plt.axhline(y=df['mean'].mean(), color='r', linestyle='-')
        plt.subplots_adjust(bottom=0.3)
        plt.draw()
        plt.savefig(
            'fandom_extracted_data/' + self.fandom + '/plots/plot_average_hits_ships_character_' + char + '.png')
        plt.show()

    def plot_average_likes_character(self, data):
        df = pd.DataFrame.from_dict(data).T
        df['kudos'] = df['kudos'].astype(float)
        df['hits'] = df['hits'].astype(float)
        df = df.explode("characters")[["characters", "hits", "kudos"]].groupby("characters").agg(["count", "mean"])
        df['ratio'] = df['kudos']['mean'] / df['hits']['mean']
        df = df.sort_values('ratio')
        is_large = df['hits']['count'] > 3
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df[is_large]['ratio'].plot(kind='bar')
        plt.axhline(y=df[is_large]['ratio'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_average_likes_character.png')
        plt.show()

    def make_autopct(self, values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return '{p:.2f}%'.format(p=pct, v=val) if pct > 4 else ''

        return my_autopct

    def plot_works_count_by_rating(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df['rating'].value_counts().rename_axis('Rating').reset_index(name='Fanfic Counts')
        df = df.sort_values(by=['Rating'])
        df['Colours'] = ['tab:red', 'tab:green', 'tab:orange', 'tab:purple', 'tab:blue']
        df = df.sort_values(by=['Fanfic Counts'], ascending=False)
        df.plot(labels=df['Rating'], y='Fanfic Counts', kind='pie', autopct=self.make_autopct(df['Fanfic Counts']),
                figsize=(12, 12), colors=df['Colours'])
        plt.legend(bbox_to_anchor=(1, 1),
                   bbox_transform=plt.gcf().transFigure)
        plt.axis('off')
        plt.title(self.fandom + " Fanfic Rating Split", bbox={'facecolor': '0.8', 'pad': 5})
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_rating.png')
        plt.show()

    def plot_works_count_by_category(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df['categories'].value_counts().rename_axis('Categories').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        df[is_large].plot(labels=df['Categories'], y='Fanfic Counts', kind='pie',
                          autopct=self.make_autopct(df['Fanfic Counts']), figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1, 1),
                   bbox_transform=plt.gcf().transFigure)
        plt.axis('off')
        plt.draw()
        plt.savefig('../src/fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_category.png')
        plt.show()

    def plot_works_count_by_tag(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df["tags"].explode().value_counts().rename_axis('Tags').reset_index(name='Fanfic Counts')
        df = df.drop(0)
        df.head(100).plot(x='Tags', kind='bar', figsize=(24, 8))
        plt.subplots_adjust(bottom=0.55)
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_tag.png')
        plt.show()

    def plot_new_char_works_count_by_month(self, d, char, show=True):
        dates_work_count = {}
        df = pd.DataFrame.from_dict(d, orient='index')

        df = df.explode("characters")
        is_char = df['characters'] == char
        df = df[is_char]

        df['date_updated'] = pd.to_datetime(df['date_updated'])
        df['month_updated'] = df['date_updated'].apply(lambda x: '%d-%d' % (x.month, x.year))
        df['month_updated'] = pd.to_datetime(df['month_updated'], infer_datetime_format=True)
        df = df['title'].groupby(df['month_updated']).agg(["count"])
        df.columns = ["".join(x) for x in df.columns.ravel()]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        p1 = ax.bar(df.index, df['count'], width=25, align='center', label=char + " fanfics")
        plt.legend()
        plt.axhline(y=df['count'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig(
            'fandom_extracted_data/' + self.fandom + '/plots/chars_bars_count/plot_new_works_count_by_month_' + char + '.png')
        if (show):
            plt.show()
        plt.close(fig)

    def plot_average_words_character(self, d):
        df = pd.DataFrame.from_dict(d).T
        df['words'] = df['words'].astype(float)
        df = df.explode("characters")[["characters", "words"]].groupby("characters").agg(["count", "mean"])
        df = df['words'].sort_values(by='mean')
        is_large = df['count'] > 0
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df[is_large]['mean'].plot(kind='bar')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_average_words_character.png')
        plt.show()

    # def percentage_containing_ship(self, d):
    #     df = pd.DataFrame.from_dict(d).T
    #     df = df['rating'].value_counts().rename_axis('Rating').reset_index(name='Fanfic Counts')
    #     is_large = df['Fanfic Counts'] > 10
    #     df[is_large].plot(labels=df['Rating'], y='Fanfic Counts', kind='pie')
    #     plt.legend(bbox_to_anchor=(1, 1),
    #                bbox_transform=plt.gcf().transFigure)
    #     plt.axis('off')
    #     plt.show()

    def plot_author_variety(self, d, char):
        df = pd.DataFrame.from_dict(d).T
        df = df.explode("characters")
        is_char = df['characters'] == char
        df = df[is_char]
        df = df['authors'].explode().value_counts().rename_axis('Authors').reset_index(name='Fanfic Counts')
        df.plot(x='Authors', kind='bar')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_author_variety' + char + '.png')
        plt.show()

    def author_champ_dedication_score(self, d, char):
        df = pd.DataFrame.from_dict(d).T
        df = df.explode("characters")
        is_char = df['characters'] == char
        df = df[is_char]
        df = df.explode("authors")[["authors", "words"]].groupby("authors").agg(["count", "sum"])
        df = df['words']
        df = df.sort_values('sum')
        df['sum'].plot(kind='bar')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/author_champ_dedication_score' + char + '.png')
        plt.show()

    def plot_champs_by_dedication_score(self, d):
        df = pd.DataFrame.from_dict(d).T
        df['words'] = df['words'].astype(float)
        df_avg = df.explode("authors").explode("characters")[["title", "characters", "authors"]].groupby(
            ["characters", "authors"])["title"].agg(["count"])
        # fanfics per author per character
        df_avg = df_avg.groupby("characters")["count"].mean()

        # fanfics per character
        df_char = df['characters'].explode().value_counts().rename_axis('Characters')

        df = df.explode("characters")[["characters", "words"]].groupby("characters").agg(["count", "mean"])
        df.columns = df.columns.get_level_values(1)

        df["product"] = df_avg
        df["score"] = df["product"]
        df = df.sort_values(by='score')
        is_large = df['count'] > 0
        df = df[is_large]
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df.plot(kind='bar', y='score', figsize=(20, 8))
        plt.subplots_adjust(bottom=0.3)

        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_dedication_character.png')
        plt.show()

    def main_character_ratio(self, d):
        df = pd.DataFrame.from_dict(d).T

        # fanfics per character
        df_char = df['characters'].explode().value_counts().rename_axis('Characters')

        # fanfics where character is main character
        df_main = df['main_characters'].explode().value_counts().rename_axis('Main Characters')

        df = df.explode("characters").groupby("characters").agg(["count"])
        df.columns = df.columns.get_level_values(1)

        df_combined = pd.concat([df_char, df_main], axis=1).fillna(0)
        is_large = df_combined['characters'] > 0
        df_combined = df_combined[is_large]
        df_combined['char_difference'] = df_combined['characters'] - df_combined['main_characters']
        df_combined['main_characters'] = df_combined['main_characters'] / df_combined['characters']
        df_combined['char_difference'] = df_combined['char_difference'] / df_combined['characters']
        df_combined = df_combined.sort_values('main_characters', ascending=False)
        df_combined[['main_characters', 'char_difference']].plot(kind='bar', stacked=True, figsize=(24, 8))
        plt.subplots_adjust(bottom=0.3)
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_main_character_ratio.png')
        plt.show()

    def get_main_characters(self, chars, text):
        max = 0
        main = ""
        main2 = ""
        for char in chars:
            mentions = text.count(char)
            if mentions > max:
                main2 = main
                max = mentions
                main = char
        res = [main, main2]
        if main == "":
            return []
        if main2 == "":
            return [main]
        return res

    def detect_main_characters(self):
        with open('works.json') as json_file:
            d = json.load(json_file)
            for val in d.values():
                val["main_characters"] = get_main_characters(val['characters'], val["first_page"] + val['title'])
                self.logger_analysis.debug(val['title'] + "------" + str(val['main_characters']))
            with open('works.json', 'w') as json_file:
                json.dump(d, json_file)

    def plot_char_common_appearances(self, d, char, show=True):
        df = pd.DataFrame.from_dict(d).T
        contains_char = df['characters'].apply(lambda x: char in x)
        df_filtered = df[contains_char]
        char_df = df_filtered['characters'].explode().value_counts().rename_axis('Characters').reset_index(
            name='Fanfic Counts')
        char_df = char_df.head(min(12, char_df.shape[0] - 1))
        G = nx.star_graph(char_df.shape[0] - 1)
        pos = nx.spring_layout(G)
        colors = range(20)
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, node_color='#A0CBE2', with_labels=False, node_size=5000)
        char_df['labels'] = char_df['Characters'] + '\n' + char_df['Fanfic Counts'].apply(str)
        labels = char_df['labels']
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        plt.draw()
        plt.savefig(
            'fandom_extracted_data/' + self.fandom + '/plots/chars_appearances/plot_character_appear_' + char + '.png')
        if (show):
            plt.show()
        for entry in char_df:
            G.add_node(entry)
        plt.close()

    def remdup(self, l):
        new = []
        for elem in l:
            if elem not in new:
                new.append(elem)
        return new

    def plot_char_shipping(self, d, char, show=True):
        df = pd.DataFrame.from_dict(d).T
        df['relationships'] = df['relationships'].apply(lambda x: self.remdup(x))
        df = df.explode('relationships').fillna(0)
        has_ship = df['relationships'] != 0
        df = df[has_ship]
        contains_char = df['relationships'].apply(lambda x: char in x)
        df_filtered = df[contains_char]
        df_filtered = df_filtered[['title', 'relationships', 'characters']]
        char_df = df_filtered['relationships'].explode().value_counts().rename_axis('Characters').reset_index(
            name='Fanfic Counts')
        if char_df.shape[0] > 0:
            char_df = char_df.head(min(12, char_df.shape[0]))
            G = nx.star_graph(char_df.shape[0] - 1)
            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, node_color='#ff2ea4', with_labels=False, node_size=5000)
            char_df['labels'] = char_df['Characters'] + '\n' + char_df['Fanfic Counts'].apply(str)
            labels = char_df['labels']
            nx.draw_networkx_labels(G, pos, labels, font_size=10)
            plt.draw()
            plt.savefig(
                'fandom_extracted_data/' + self.fandom + '/plots/chars_ships/plot_character_ships_' + char + '.png')
            if (show):
                plt.show()
            for entry in char_df:
                G.add_node(entry)
            plt.close()
        else:
            G = nx.star_graph(0)
            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, node_color='#ff2ea4', with_labels=False, node_size=5000)
            labels = {}
            labels[0] = char
            nx.draw_networkx_labels(G, pos, labels, font_size=10)
            if (show):
                plt.show()
            for entry in char_df:
                G.add_node(entry)
            plt.close()

    def plot_char_tags(self, d, char, show=True):
        df = pd.DataFrame.from_dict(d).T
        contains_char = df['characters'].apply(lambda x: char in x)
        df_filtered = df[contains_char]
        char_df = df_filtered['tags'].explode().value_counts().rename_axis('Tags').reset_index(
            name='Fanfic Counts')
        char_df = char_df.head(min(20, round((char_df.shape[0]) * 0.5)))
        G = nx.star_graph(char_df.shape[0] - 1)
        pos = nx.spring_layout(G)
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, node_color='#32CD32', with_labels=False, node_size=5000)
        char_df['labels'] = char_df['Tags'] + '\n' + char_df['Fanfic Counts'].apply(str)
        extra = char + '\n' + str(df_filtered.shape[0])
        labels = char_df['labels']
        labels[0] = extra
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/chars_tags/plot_character_tags_' + char + '.png')
        if (show):
            plt.show()
        for entry in char_df:
            G.add_node(entry)
        plt.close()

    def charrel_entry(self, char, d, ficcount):
        df = pd.DataFrame.from_dict(d).T
        contains_char = df['characters'].apply(lambda x: char in x)
        df_filtered = df[contains_char]
        char_df = df_filtered['characters'].explode().value_counts().rename_axis('Characters').reset_index(
            name='Fanfic Counts')
        links = 4
        # if ficcount > 150:
        #     links = 2
        # if ficcount < 150:
        #     links = 3
        # if ficcount < 100:
        #     links = 4
        # if ficcount < 70:
        #     links = 5
        # if ficcount < 40:
        #     links = 3
        # if ficcount < 20:
        #     links = 2
        char_df = char_df.head(min(links, char_df.shape[0] - 1))
        chars = list(char_df['Characters'].values)
        chars.remove(char)
        return chars

    def build_rel_dictionary(self, d):
        df = pd.DataFrame.from_dict(d).T
        df['hits'] = df['hits'].astype(float)
        df = df.explode("characters")[["characters", "hits"]].groupby("characters").agg(["count", "mean"])
        df = df['hits'].sort_values(by='mean')
        is_large = df['count'] > 0
        df = df[is_large]
        charlist = list(df.index)
        char_dict = {}
        for char in charlist:
            char_dict[char] = self.charrel_entry(char, d, df.loc[char]['count'])
        G = nx.Graph(char_dict)
        fig, ax = plt.subplots(figsize=(80, 80))
        colors = [plt.cm.rainbow(x) for x in range(1, 256)]
        nx.draw_networkx(G, with_labels=True, node_size=np.log(df['count'].values) * 1500, edge_color=colors, width=4)
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_char_network.png')
        plt.show()

    def plot_ffnet_and_ao3(ao3, ff):
        dates_work_count = {}
        df_ao3 = pd.DataFrame.from_dict(ao3, orient='index')
        df_ao3['date_updated'] = pd.to_datetime(df_ao3['date_updated'])
        df_ao3['month_updated'] = df_ao3['date_updated'].apply(lambda x: '%d-%d' % (x.month, x.year))
        df_ao3['month_updated'] = pd.to_datetime(df_ao3['month_updated'], infer_datetime_format=True)
        df_ao3 = df_ao3['title'].groupby(df_ao3['month_updated']).agg(["count"])
        df_ao3.columns = ["".join(x) for x in df_ao3.columns.ravel()]

        df_ff = pd.DataFrame.from_dict(ff, orient='index')
        df_ff['published'] = pd.to_datetime(df_ff['published'])
        df_ff['month_updated'] = df_ff['published'].apply(lambda x: '%d-%d' % (x.month, x.year))
        df_ff['month_updated'] = pd.to_datetime(df_ff['month_updated'], infer_datetime_format=True)
        df_ff = df_ff['title'].groupby(df_ff['month_updated']).agg(["count"])
        df_ff.columns = ["".join(x) for x in df_ff.columns.ravel()]

        df = df_ao3.merge(df_ff, how='outer', left_index=True, right_index=True).fillna(0)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        pf = ax.bar(df.index, df['count_y'], width=25, align='center', label='Works in FanFiction.net')
        pa = ax.bar(df.index, df['count_x'], bottom=df['count_y'], width=25, align='center', label='Works in Archive')
        plt.legend()
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_new_works_count_by_month_sites.png')
        plt.show()

    def plot_chars_everything(self, d):
        df = pd.DataFrame.from_dict(d).T
        df = df['characters'].explode().value_counts().rename_axis('Characters').reset_index(name='Fanfic Counts')
        is_large = df['Fanfic Counts'] > 0
        df = df[is_large]
        charlist = df['Characters'].values
        for char in charlist:
            self.logger_analysis.info('Plotting all for ' + char)
            self.plot_new_char_works_count_by_month(d, char, False)
            self.plot_char_shipping(d, char, False)
            self.plot_char_common_appearances(d, char, False)
            self.plot_char_tags(d, char, False)

    def champs_without_explicit(self, d):
        df = pd.DataFrame.from_dict(d).T
        no_lewd = df['rating'] != 'Explicit'
        df = df[no_lewd]
        df = df['characters'].explode().value_counts().rename_axis('Characters').reset_index(
            name='Fanfic Counts Without Explicit')
        is_large = df['Fanfic Counts Without Explicit'] > 0
        plt.rc('font', size=8)
        plt.rc('axes', titlesize=8)
        df[is_large].plot(x='Characters', kind='bar', figsize=(20, 8))
        plt.axhline(y=df[is_large]['Fanfic Counts Without Explicit'].mean(), color='r', linestyle='-')
        plt.draw()
        plt.savefig('fandom_extracted_data/' + self.fandom + '/plots/plot_works_count_by_character_no_lewd.png')
        plt.show()

    def do_analysis(self, d):
        self.plot_new_works_count_by_month(d)
        self.plot_new_works_count_by_month_ratings(d)
        self.plot_works_count_by_character(d)
        self.plot_works_count_by_ship(d)
        self.plot_average_hits_character(d)
        self.plot_average_likes_character(d)
        self.plot_works_count_by_rating(d)
        self.plot_chars_ratings(d)
        self.plot_works_count_by_tag(d)
        # plot_new_char_works_count_by_month(d, "Evelynn")
        self.plot_average_words_character(d)
        # author_champ_dedication_score(d, "Qiyana")
        self.plot_works_count_by_category(d)
        self.plot_champs_by_dedication_score(d)
        # self.main_character_ratio(d)
        # self.detect_main_characters()
        # plot_char_common_appearances(d, 'Vladimir')
        # plot_char_tags(d, 'Jhin')
        self.build_rel_dictionary(d)
        # plot_char_shipping(d, "Fiddlesticks")
        # self.plot_chars_everything(d)
        # self.champs_without_explicit(d)
        # plot_average_hits_ships_character(d, 'Evelynn')

    # def plot_character_relations(data):
    #
    # most_dedication_year(data)

    # count_mentions(data)
    # def ships_by_type(data):
    #
    # def
    #
    # https://stackoverflow.com/questions/60007858/questions-on-how-to-count-frequency-of-keyword-in-pandas-dataframes
