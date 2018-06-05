import textrank

def get_article(file):
    text = ""
    with open(file) as f:
        for line in f:
            text = text +'\n'+ line
    return text


article = get_article('article');
summary = textrank.summarize_text(news[4])
print(summary)