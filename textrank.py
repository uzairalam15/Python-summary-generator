
import io
import itertools
import os

import click
import networkx as nx
import nltk

# POS tags
def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]

def unique_everseen(iterable, key=None):

    seen = set()
    seen_add = seen.add
    if key is None:
        for element in [x for x in iterable if x not in seen]:
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def lDistance(firstString, secondString):

    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]


def buildGraph(nodes):

    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr


def extractKeyphrases(text):
    # tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    # assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]

    tagged = filter_for_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

    # this will be used to determine adjacent words in order to construct
    # keyphrases with two words

    graph = buildGraph(word_set_list)

    # pageRank - initial value of 1.0, error tolerance of 0,0001,
    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get,
                        reverse=True)

   # aThird = len(word_set_list) // 5
    keyphrases = keyphrases[0:9]

    modifiedKeyphrases = set([])

    dealtWith = set([])
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            # if this is the last word in the text, and it is a keyword, it
            # definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and secondWord in keyphrases and \
                    secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)

        i = i + 1
        j = j + 1

    return modifiedKeyphrases


def extractSentences(text):
    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
    text = ' '.join(text.strip().split('\n'))
    sentenceTokens = tokenizer.tokenize(text)
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get,
                       reverse=True)
    # return a 100 word summary
    summary = ' '.join(sentences[0:1])
    summaryWords = summary.split()
    summaryWords = summaryWords[0:100]
    summary = ' '.join(summaryWords)
    # print(summary)
    return summary


def writeFiles(summary, keyphrases, fileName):
    "outputs the keyphrases and summaries to appropriate files"
    print("Generating output to " + 'keywords/' + fileName)
    keyphraseFile = io.open('keywords/' + fileName, 'w')
    for keyphrase in keyphrases:
        keyphraseFile.write(keyphrase + '\n')
    keyphraseFile.close()

    print("Generating output to " + 'summaries/' + fileName)
    summaryFile = io.open('summaries/' + fileName, 'w')
    summaryFile.write(summary)
    summaryFile.close()

    print("-")

#
# def summarize_all():
#     # retrieve each of the articles
#     articles = os.listdir("articles")
#     for article in articles:
#         print('Reading articles/' + article)
#         articleFile = io.open('articles/' + article, 'r')
#         text = articleFile.read()
#         keyphrases = extractKeyphrases(text)
#         summary = extractSentences(text)
#         writeFiles(summary, keyphrases, article)


def summarize_text(text):
    summary = extractSentences(text)
    return summary

def get_keywords(text):
    keywords = extractKeyphrases(text)
    return keywords

@click.command()
@click.option("--filename",prompt="Filename ")
def summarize(filename):
    with open(filename,"rt",encoding="utf-8") as fin:
        text = fin.read()
        summary = extractSentences(text)
        print(summary)


if __name__ == "__main__":
    summarize()