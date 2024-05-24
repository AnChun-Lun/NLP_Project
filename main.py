#CODE NOT TESTED SINCE I DON'T HAVE ARTICLES TO TEST IT ON, TAKE THIS AS A GRAIN OF SALT
import thehackernewsscraper
import bleepingcomputerscraper
import spacy
import bisect

nlp = spacy.load("en_core_web_lg")

articles = thehackernewsscraper.scrape_hackernews().append(bleepingcomputerscraper.scrape_bleepingcomputer()) #combines all articles into a single list

#user input
print(f"Total number of articles scraped: " + len(articles))
print(f"Cluster articles by:")
keyword = str(input())
print(f"How many articles:")
number = int(input())

#scores the article v1
def scorev1(article):
    si = nlp(keyword).similarity(nlp(article['title'])) + nlp(keyword).similarity(nlp(article['text'])) + nlp(keyword).similarity(nlp(article['keywords']))
    return (si / 3)

new_articles = []
new_articles.append({'article': articles[0], 'si': scorev1(articles[0])}) #add first article to list for comparison

#modify new_articles to point to original articles array
for article in articles:
    if(article.index(articles) == 0): #skip first element
        continue
    elif(article.index(articles) < number): #when new_articles length < number, insorts with "si" as parameter to check for order
        bisect.insort(new_articles, {'article':article, 'si': scorev1(article)}, key=lambda x: x['si'])
    elif(scorev1(article) < new_articles['si'][0]): #when si < first element's si, skips the article (less relevant than the least relevant article)
        continue
    else: #when si is within the list, bisorts first then pop the lowest value
        bisect.insort(new_articles, {'article':article, 'si': scorev1(article)}, key=lambda x: x['si'])
        new_articles.pop(0)

#output
print("Top " + number + " articles most relevant to " + keyword + "are:")
print("="*80)

#prints every article
for article in new_articles:
    print(f"Title: {article['article']['title']}")
    print(f"Link: {article['article']['link']}")
    print(f"SI: {article['si']}")
    print("="*80)



        
        

