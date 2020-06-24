from textblob import TextBlob

text = '''The main issue is that relugolix was not tested in combination with NHTs or docetaxel, which are standard of care now for patients with metastatic prostate cancer. These data only apply to those patients who are receiving ADR monotherapy. #ASCO20'''

analyzer = TextBlob(text)

print(analyzer.sentiment)


