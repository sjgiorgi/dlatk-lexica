# dlatk-lexica
Simple interface for extracting lexica scores from text.


## Installation



## Getting started

Get a lexical estimate from a single piece of text:

```
> from dlatk_lexica.workers import LexiconExtractor as lex

> le = lex("stress")
> text = "He'll find you that's what he does, that's all he does!"
> le.get_scores(text)
[{'stress': 1.9407162885529994}]
```

Get estimates from a list of text:
```
> text_list = ["What day is it?  The date...", "Thursday...uh...May twelfth.", "What year?!"]
> le.get_scores(text_list)
[{'stress': -0.11333633586700004}, {'stress': 2.4685546792629998}, {'stress': -0.23413304501233334}]
```

Use more than one lexica:
```
> le.combine_lexica("affect")
> le.get_scores(text)
[{'affect': 5.4081104751889, 'stress': 1.9407162885529994}]
```



## Available Lexica

To see available lexica run the following:

```
> le.available_lexica
['affect', 'age_gender', 'happiness', 'life_satisfaction', 'loneliness', 'politeness', 'stress']
```

By default, this plugin can produce scores for happiness, life satisfaction, stress, loneliness, affect, politness, and age/gender. Please use the following citations if you use these measures in your work:

```
Affect
------
Preoţiuc-Pietro, D., Schwartz, H. A., Park, G., Eichstaedt, J., Kern, M., Ungar, L., & Shulman, E. (2016, June). Modelling valence and arousal in facebook posts. In Proceedings of the 7th workshop on computational approaches to subjectivity, sentiment and social media analysis (pp. 9-15).

Age and Gender
--------------
Sap, M., Park, G., Eichstaedt, J., Kern, M., Stillwell, D., Kosinski, M., ... & Schwartz, H. A. (2014, October). Developing age and gender predictive lexica over social media. In Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP) (pp. 1146-1151).

Happiness
---------
Giorgi, S., Guntuku, S. C., Eichstaedt, J. C., Pajot, C., Schwartz, H. A., & Ungar, L. H. (2021, May). Well-Being Depends on Social Comparison: Hierarchical Models of Twitter Language Suggest That Richer Neighbors Make You Less Happy. In Proceedings of the International AAAI Conference on Web and Social Media (Vol. 15, pp. 1069-1074).

Life Satisfaction
-----------------
Jaidka, K., Giorgi, S., Schwartz, H. A., Kern, M. L., Ungar, L. H., & Eichstaedt, J. C. (2020). Estimating geographic subjective well-being from Twitter: A comparison of dictionary and data-driven language methods. Proceedings of the National Academy of Sciences, 117(19), 10165-10171.

Loneliness
----------
Guntuku, S. C., Schneider, R., Pelullo, A., Young, J., Wong, V., Ungar, L., ... & Merchant, R. (2019). Studying expressions of loneliness in individuals using twitter: an observational study. BMJ open, 9(11), e030355.

Politeness
----------
Li, M., Hickman, L., Tay, L., Ungar, L., & Guntuku, S. C. (2020). Studying Politeness across Cultures Using English Twitter and Mandarin Weibo. Proceedings of the ACM on Human-Computer Interaction, 4(CSCW2), 1-15.

Stress
------
Guntuku, S. C., Buffone, A., Jaidka, K., Eichstaedt, J. C., & Ungar, L. H. (2019, July). Understanding and measuring psychological stress using social media. In Proceedings of the International AAAI Conference on Web and Social Media (Vol. 13, pp. 214-225).

```

## Adding Custom Lexica

We assume lexica are of the form `category`, `word`, `weight` where weighted words are contained in categories. Words can belong to multiple categories. New lexica must be in json form:
```
{"word_1": {"category1": score1, "category2": score2, ...}}
```

For example, the age/gender lexica is of the form:
```
{"pick": {"age": 22.9491861985, "gender": 20.9684355463}, "revise": {"age": 25.972110829, "gender": 29.0244389707}, ...}
```

To upload a json file simply run:
```
le.upload_lexicon("/path/to/file/lexicon.json")
```