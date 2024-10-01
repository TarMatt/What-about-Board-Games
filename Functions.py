## These are the functions that are used in the second and the third part of the project

import math
from nltk.corpus import sentiwordnet as swn
import pandas as pd


from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

def compute_pmi(adj, noun, pair_count, adj_counts, noun_counts, total_docs):
    p_adj_noun = pair_count / total_docs
    p_adj = adj_counts[adj] / total_docs
    p_noun = noun_counts[noun] / total_docs
    pmi = math.log2(p_adj_noun / (p_adj * p_noun))
    return pmi

def sentiwn_score(word):
    synsets = list(swn.senti_synsets(word))
    score = 0.0
    if len(synsets) > 0:
        polarity = pd.DataFrame([{'pos': sw.pos_score(), 
                                  'neg': sw.neg_score(), 
                                  'obj': sw.obj_score()} for sw in synsets])
        avg_polarity = polarity.mean()
        score = (avg_polarity['pos'] + avg_polarity['obj']) - (avg_polarity['neg'] + avg_polarity['obj'])
    return score

#________________________________________________________________________________________________________________________________#________________________________________________________________________________________________________________________________


## These functions are utilized within the fourth part of the project to filter and summarize the insights regarding the 
##.   board game aspects that are object of the project.



from scipy import stats
import numpy as np

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from sklearn.feature_extraction.text import CountVectorizer

import spacy
nlp = spacy.load('en_core_web_lg') 


#______________________________________________________________________________________________________

##Set the summary dataframe 

def get_df(frame,similarity_nouns,similarity_adjs,categories):
    
    final_df=frame[(np.isin(frame['noun'],similarity_nouns) | np.isin(frame['adj'],similarity_adjs))]
    
    if len(categories)>0:
        final_df= final_df[np.isin(final_df['category'],categories)] #Filtering for categories
        
    final_df=final_df[['doc','category','noun','adj','count','pmi_an',
                       'Synset_pol','Sent_neg','Sent_neu','Sent_pos','stars','sentence']]
    

    return final_df

####________________________

##Set the Born explanation

def get_born(frame,similarity):
    final_borne=frame[np.isin(frame['noun'],similarity)]
    final_borne=final_borne[['Positive','Neutral','Negative']]
    return final_borne

####________________________

## Set the final dataframe for visualizing the information. This dataframe contains sentiment polarity, reviews and all the other     statistics associated with particular noun-adj pair, summarizing the use of that pair within the comments through the mean.
   
        
def get_info(similarity_nouns,similarity_adjs,frame,born_frame):
    
    Final=[]

    for noun in similarity_nouns:
        for adj in set(frame[frame['noun']==noun].adj.values):
            Final.append({
                'Object':noun,
                'Adj': adj,
                'Count':    frame[(frame['noun']==noun) & (frame['adj']==adj)]['count'].values[0],
                'Synset_pol': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Synset_pol.values),4),
                'Sentence_neg': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_neg.values),4),
                'Sentence_neu': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_neu.values),4),
                'Sentence_pos': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_pos.values),4),
                'Mean_Stars': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].stars.values),3),

            })
            
            
    for adj in similarity_adjs:
        for noun in set(frame[frame['adj']==adj].noun.values):
            Final.append({
                'Object':noun,
                'Adj': adj,
                'Count':    frame[(frame['noun']==noun) & (frame['adj']==adj)]['count'].values[0],
                'Synset_pol': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Synset_pol.values),4),
                'Sentence_neg': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_neg.values),4),
                'Sentence_neu': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_neu.values),4),
                'Sentence_pos': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].Sent_pos.values),4),
                'Mean_Stars': round(np.mean(frame[(frame['noun']==noun) & (frame['adj']==adj)].stars.values),3),

            })
    Final = pd.DataFrame(Final)
    Final = Final[['Object','Adj','Count','Synset_pol','Sentence_neg','Sentence_neu','Sentence_pos','Mean_Stars']]
    return Final

####______________________

## Prints the words cloud graph

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

def get_cloud(frame,cloud=None):
    
    if cloud is None:
        cloud = []
  
    for noun in frame.noun.values:
        cloud.append(noun)
    for adj in frame.adj.values:
        cloud.append(adj)
    cloud_fr=Counter(cloud)
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(cloud_fr)

    # Display
    plt.figure(figsize=(10,8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off') 
    plt.show()
    
    
    
#####___________________

def mean_int(data, confidence=0.95):
 
    mean = round(np.mean(data),1)
    sem = stats.sem(data)
    
    # Compute the confidence interval using the t-distribution
    margin_of_error = stats.t.ppf((1 + confidence) / 2., len(data) - 1) * sem
    
    return mean, round(mean - margin_of_error,3), round(mean + margin_of_error,3)















