import nltk

neg=[]
pos=[]


class Analyzer():
    """Implements sentiment analysis."""
    
    
    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        self.positives = []
        with open("positive-words.txt") as positive:
            for line in positive:
                if line.startswith(';') or line.startswith(" "):
                    pass
                else:
                    pos.append(line.strip('\n'))
            
        self.negatives = []
        with open("negative-words.txt") as negative:
            for line in negative:
                if line.startswith(';'):
                    pass
                else:
                    neg.append(line.strip('\n'))
            
       

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        score=0
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        for token in tokens:
           
            if token in pos:
                score+=1
                
            elif token in neg:
                score-=1
                
       
        return score
        