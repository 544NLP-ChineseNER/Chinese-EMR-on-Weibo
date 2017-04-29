# Chinese-NER-on-Weibo
--------------------------
Recognizing Chinese names from Weibo data

## Introduction
 Chinese Morph Entity Resolution System

 Internet users commonly create many information morphs for different kinds of reasons. Some of the morphs are created for fun while some of them are created to avoid censorships. Almost every area use morphs for communication, including sports area, entertainment area and political area.
Based on this situation, our project proposes a model to relate morph entities with their real targets. The existing works relate to our projects include model that resolve morph entities in censored data and model that automatically encode morphs. Our project basically tries to combine the two models together and implement methods related.

 II.	Method

 The project’s procedure includes two steps. First, we perform semantic annotation and target identification on our data set and generate a list of entities and its morphs. Then, we perform surface features and semantic features analysis to figure out the real entities and targets.
In the first step, we use Jieba Chinese text segmentation and Stanford POS tagger (Toutanova et al., 2003) to filter out name entities. Name entities will be annotated as Morph, Entity, Event, and Other Noun Phrases. In the second step, we further adopt features discussed in “Be Appropriate and funny” (Boliang Zhang et al., 2015). These features include phonetic similarity, spelling decomposition, translation and transliteration. For semantic features analysis, we build a model that includes personal characteristics and historical information. We then construct Information Network (Hongzhao et al., 2015) and use Nearest Common Neighbors to measure the similarity between entities and morphs based on these features. The model will be trained with tweets and related news articles, and generate weight vectors of every surface and semantic feature, and will be used for final evaluation.

## Deployment

 ### Environment:
 Python3

 ### Tools to install:
 jieba, ntlk, gensim, pypinyin, pyenchant, jellyfish, bs4, selenium

 ### Usage
   <code>
   $ python3
 
   from src.core import EMRecognition
 
   emr_instance = EMRecognition()
 
   emr_instance.recognize_tweet("我是一条咸鱼")
 
   </code>

 ### Test:
   Locate to the root directory of this project.

   <code>
  
   $ export PYTHONPATH=OLD_${PYTHONPATH}
 
   $ export PYTHONPATH=${PWD}
 
   $ cd test
 
   $ python3 evaluation.py
 
   </code>
 
