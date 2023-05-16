import datetime

from ja_timex import TimexParser
import pandas as pd
import spacy


LABEL_JP2EN = {
    'イベント名': 'Event',
    "人名": "Person",
    "組織": "Organization",
    "日付": "Datetime",
    "時刻": "Time",
    # "曜日": "Day_Of_Week",
    "場所": "Location",
#     "お金": "Money",
#     "URL": "URL",
}


LABEL_EN2JP = {
    'Event' : 'イベント名',
    "Person": "人名",
    "Organization": "組織",
    "Date": "日付",
    "Time": "時刻",
    # "Day_Of_Week": "曜日",
    "Location": "場所",
    # "Money": "お金",
    # "URL": "URL",
}
# TODO: イベント名を加えたい。
# ストックマーク社の「Wikipediaを用いた日本語の固有抽出表現データセット」を用いて学習したモデルを別で用意
# もしくは「イベント名 = メールの件名」とする

EVENT = {'N_Event', "Event_Other", "Occasion_Other", "Game", "Doctrine_Method_Other"}
LOCATION = {"Postal_Address", "Province", "City", "Station", "Facility_Part"}  # 場所系のラベルを統一
ORGANIZATION = {"School", "Organization_Other", "Company"}  # 組織系のラベルを統一
# TODO: GiNZAのLabelの定義について調べて適宜追加


# 似た系統のラベルを統一化
def put_together_label(label: str) -> str :
    if label in LOCATION:
        return "Location"
    elif label in ORGANIZATION:
        return "Organization"
    elif label in EVENT:
        return 'Event'
    else:
        return label


def ner(mail):
    outputs = {
        "event": [None],
        "startingDateTime": None,
        "endingDateTime": None,
        "location": [None],
        "person": [None]
    }

    # モデルをロード
    # 'ja_ginza_electra'は'ja_ginza'に比べて重いが高性能
    nlp = spacy.load('ja_ginza_electra')

    # 独自ルールの追加(ユーザーが手動で追加できるようにする)
    # 今回の例ではデフォルトだと「郡」が「人名」と判断されないので手動で追加
    config = {
       'overwrite_ents': True
    }
    ruler = nlp.add_pipe('entity_ruler', config=config)
    patterns = [
        {"label": "Person", "pattern": "郡"},
    ]
    ruler.add_patterns(patterns)


    # 固有表現抽出の実行
    extracted_mail_list = []
    doc = nlp(mail)

    row = dict.fromkeys(LABEL_JP2EN.keys())
    for label_en in LABEL_EN2JP.keys():
        tokens = []
        for ent in doc.ents:
            if put_together_label(ent.label_) == label_en:
                tokens.append(ent.text)
        row[LABEL_EN2JP[label_en]] = tokens

    # 重要部分を抽出
    # 参考: https://qiita.com/wf-yamaday/items/3ffdcc15a5878b279d61
    # results = []
    # for chunk in doc.noun_chunks:
    #     results.append((chunk.text, chunk.similarity(doc)))

    # row["essence"] = sorted(results,key=lambda x: x[1],reverse=True)[0][0]

    extracted_mail_list.append(row)

    extracted_mail_list = pd.DataFrame(extracted_mail_list)
    
    # 現在時刻を取得
    dt_now = datetime.datetime.now()
    # どのイベントをスケジュールに登録するかの指標（適当だけど，今は日程が複数にまたがっている長さ>メールの後ろで順位付けてる）
    date_validity = 0
    # イベントごとにitr
    date_validity = 0
    date_elems = extracted_mail_list['日付'][0]
    time_elems = extracted_mail_list['時刻'][0]
    if len(date_elems) >= date_validity:
        date_validity = len(date_elems)
        startingtime, endingtime = None, None
        year_elem, month_elem, day_elem = dt_now.year, dt_now.month, dt_now.day
        for k, date_elem in enumerate(date_elems):
            # print(date_elem)
            timex_parser = TimexParser()
            timexes = timex_parser.parse(date_elem)
            year_elem, month_elem, day_elem = dt_now.year, dt_now.month, dt_now.day
            for datetime_elem in timexes:
                # print(datetime_elem.value)
                # 年抽出
                if datetime_elem.value[0] != "X":
                    year_elem = datetime_elem.value[0:4]
                # 月抽出
                if datetime_elem.value[5] != "X":
                    month_elem = datetime_elem.value[5:7]
                # 日抽出
                if datetime_elem.value[8] != "X":
                    day_elem = datetime_elem.value[8:10]
            if k == 0:
                outputs["startingDateTime"] = f'{year_elem}/{month_elem}/{day_elem}'
                outputs["endingDateTime"] = f'{year_elem}/{month_elem}/{day_elem}'
            else:
                outputs["endingDateTime"] = f'{year_elem}/{month_elem}/{day_elem}'
            # print(f'{year_elem}/{month_elem}/{day_elem}')
        if outputs["startingDateTime"] == None:
            outputs["startingDateTime"] = f'{year_elem}/{month_elem}/{day_elem}'
            outputs["endingDateTime"] = f'{year_elem}/{month_elem}/{day_elem}'
        # 時間整形
        startingtime, endingtime = " 00:00", " 23:59"
        for k, time_elem in enumerate(time_elems):
            timex_parser = TimexParser()
            timexes = timex_parser.parse(time_elem)
            hour_elem, min_elem = "00", "00"
            for l, datetime_elem in enumerate(timexes):
                # print(datetime_elem.value)
                # 時間抽出
                if datetime_elem.value[1] != "X":
                    hour_elem = datetime_elem.value[1:3]
                # 分抽出
                if datetime_elem.value[4] != "X":
                    min_elem = datetime_elem.value[4:6]
                if hour_elem != None and outputs["startingDateTime"] != None:
                    if l == 0:
                        startingtime = f' {hour_elem}:{min_elem}'
                        endingtime = f' {hour_elem}:{min_elem}'
                    else:
                        endingtime = f' {hour_elem}:{min_elem}'
        if startingtime != None:
            outputs["startingDateTime"] = outputs["startingDateTime"] + startingtime
            outputs["endingDateTime"] = outputs["endingDateTime"] + endingtime

        # location
        if extracted_mail_list['イベント名'][0]  != None:
            outputs["event"] = extracted_mail_list['イベント名'][0]
        if extracted_mail_list['場所'][0]  != None:
            outputs["location"] = extracted_mail_list['場所'][0]
        if extracted_mail_list['人名'][0]  != None:
            outputs["person"] = extracted_mail_list['人名'][0]
        if extracted_mail_list['組織'][0] != None:
            if extracted_mail_list['人名'][0] != None:
                outputs["person"]+=extracted_mail_list['組織'][0]
            else:
                outputs["person"] = extracted_mail_list['組織'][0]
    return outputs


if __name__ == "__main__":
    outputs = ner("こんにちは！山田さん")
    print(outputs)
    