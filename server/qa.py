from datetime import datetime as dt
from datetime import timedelta
import json
import re
import urllib

from ja_timex import TimexParser
import requests
from transformers import pipeline


class QaEn:
    def ja2en(self, input_ja):
        s_quote = urllib.parse.quote(input_ja)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = f'auth_key=67455475-43de-d413-f5ee-847da2d11d17:fx&text={s_quote}&target_lang=EN'
        response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, data=data)
        input_en = json.loads(response.text)["translations"][0]["text"]
        return  input_en.replace("\n","")
    
    def qa(self, input_en):
        # questions
        questions = [
            "What do they?",
            "What is the year when the meeting holds?",
            "What is the month when the meeting holds?",
            "What is the date the meetiing holds?",
            "What is the starting time?",
            "What is the ending time?",
            "Where the meeting holds",
            "What is his name"
            ]
        
         # Instatiate the model from checkpoint
        model_checkpoint = "bert-large-uncased-whole-word-masking-finetuned-squad"
        model = pipeline(
            'question-answering',
            model=model_checkpoint,
            tokenizer=model_checkpoint
        )

        answers = model(
                context=input_en,
                question=questions,
                top_k=1 # Gives 1 answers per question
            )
        
        answer = [answers[i]["answer"] for i, _ in enumerate(answers)]
        return answer

    #post processing function
    def output(self, answer):
        event = [answer[0]]

        try:
            year = dt.strptime(answer[1], '%y').strftime('%Y')
        except:
            year = dt.now().date().strftime("%Y")
        try:
            month = dt.strptime(answer[2], '%b').strftime('%m')
        except:
            month = dt.now().date().strftime("%m")
        try:
            date = re.sub(r"\D", "", answer[3])
            if 1<= int(date) <= 31:
                date = dt.strptime(date, '%d').strftime('%d')
            else:
                raise(TypeError)
        except:
            date = dt.now().date().strftime("%d")
        try:
            stime = TimexParser().parse(answer[4])[0].text
            stime = dt.strptime(stime, '%H:%M')
            if "p.m." in answer[4] or "pm" in answer[4]:
                stime += timedelta(hours=12)
            else:
                pass
            stime = stime.strftime('%H:%M')
        except:
            stime = ""
        try:
            etime = TimexParser().parse(answer[5])[0].text
            etime = dt.strptime(etime, '%H:%M')
            if "p.m." in answer[5] or "pm" in answer[5] or "p.m" in answer[5] or "pm." in answer[5]:
                etime += timedelta(hours=12)
            else:
                pass
            etime = etime.strftime('%H:%M')
        except:
            etime = ""
        startingtime = year+"/"+month+"/"+date+" "+stime
        endingtime  = year+"/"+month+"/"+date+" "+etime

        place = [answer[6]]
        person = [answer[7]]

        return event, startingtime, endingtime, place, person

    def main(self, input_ja):
        input_en = self.ja2en(input_ja)
        answer = self.qa(input_en)
        list_outputs = self.output(answer)
        outputs = {
            'event': list_outputs[0],
            'startingDateTime': list_outputs[1],
            'endingDateTime': list_outputs[2],
            'location': list_outputs[3],
            'person': list_outputs[4],
        }
        return outputs


def qa(mail: str):
    qa_model = QaEn()
    return qa_model.main(mail)


if __name__ == "__main__":
    outputs = qa("こんにちは！山田さん")
    print(outputs)
