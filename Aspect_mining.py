## These functions are the ones used for implementing SYNTAX PARSING within the project. 

#################| Fuction to explore further and deeper the tree syntax

def explore(text,children=None,level=None):
    if children is None:
        children = []
    if level is None:
        level=0
    for child in text.children:
        stats=(child,child.pos_,child.dep_,level)
        if child.pos_ not in ['PUNCT','SPACE','SYM','NUM']: 
            children.append(stats)
            explore(child,children=children,level=level+1)

    return children


#################| Function to retrieve those possible aspects that are NOUNS


def noun_mapping(text,explore=explore):
    nouns_map = {}
    nouns=[]
    for sent in text.sents:
        for token in sent:
            if (token.pos_ in ['NOUN','PROPN']) & (token.dep_!='compound'):
                nouns.append((token,str(sent)))     # Retrieve only the nouns from a comment
                
                
    for noun,sent in nouns:
        children=explore(noun,children=None)
        children= [(a,p,d,l) for a,p,d,l in children if (d!='compound')]  # Obtain the children of these nouns
        comp_noun=[comp for comp in noun.children if (comp.pos_=='NOUN') & (comp.dep_=='compound')] # The compound nouns
        
        if len(comp_noun) > 0:
            nouns_map[(noun,comp_noun[0])]=(sent,children)
        else:                                               # Populate the dictionary keys with the nouns (or comp-Nouns)
            nouns_map[(noun,)]=(sent,children)              #    and the values with the children 
   
    sents={noun:sent for noun,(sent,children) in nouns_map.items()}       # Store the sentences belonging to the aspects
    
    return nouns_map,sents


##################| Function to create a dictionary of aspects and associate those adjectives that are directly             ######                connected to them


def search_adjectives(asp_map,a_dict=None):
    if a_dict== None:
        a_dict={}
    for noun,(sentence,children) in asp_map.items():
        subnouns = [(x, lev) for x, pos, dep, lev in children if pos in ['NOUN', 'PROPN']]
        a_dict[noun]=[]
        for child  in children:
            if child[1] == 'ADJ' and len([(n, l) for n, l in subnouns if l < child[3]]) == 0:  
                try:                                   
                    a_dict[noun].append(child[0])
                except KeyError:
                    pass
                
    for noun,children in a_dict.items():           # This part deal with the negations and the possible adverbs
        for i, child in enumerate(children):
            advs=[ adv for adv in child.children if adv.pos_=='ADV']
            neg=[ negation for negation in child.children if negation.lemma_=='not' and negation.idx < child.idx]
            if len(neg) > 0:
                if len(advs)>0:
                    a_dict[noun][i] = 'not' + ' ' + str(advs[0]) + ' ' + str(a_dict[noun][i]) 
                else:
                    a_dict[noun][i] = 'not' + ' ' + str(a_dict[noun][i]) 
            if len(neg)==0:
                if len(advs)>0:
                    a_dict[noun][i] =  str(advs[0]) + ' ' + str(a_dict[noun][i]) 
                    
                    
    return a_dict

#################| Fuctions to associate those adjectives that are connected to their nouns through a verb 

def verb_adjectives(text, a_dict, be_only):  #This first part of the code store the subject and the possible negations/compounds
    if be_only:
        verbs = [x for x in text if x.lemma_ == 'be']
    else:
        verbs = [x for x in text if x.pos_ in {'AUX', 'VERB'}]
    for verb in verbs:
        subtokens = explore(verb)
        neg = [(neg,pos,con,level) for neg,pos,con,level  in subtokens if neg.lemma_=='not' and level==0] #Find negations
        subject = [(x) for x, pos, dep, level, in subtokens if x.idx<verb.idx and dep == 'nsubj']
        if len(subject) > 0:
            subj = subject[0]
            comp_subj=[subj for subj in subj.children if (subj.pos_=='NOUN') and (subj.dep_=='compound')] #Set compound subjects
    
            if len(comp_subj)>0:
                subj= (subj,comp_subj[0])
            else:
                subj=(subj,)
                
              
            for candidate, pos, dep, level in subtokens: #This part is about identifying the adjectives and deal with negations
                if not candidate.idx<verb.idx:
                    if pos == 'ADJ' and level == 0:
                        try:
                            if len(neg) > 0:
                                a_dict[subj].append('not'+ ' ' + str(candidate))
                            elif len(neg)==0:
                                a_dict[subj].append(str(candidate))
                        except KeyError:
                            pass
                        conjadjs=[adj for adj in candidate.children if adj.pos_=='ADJ' and adj.dep_=='conj']
                        alteraction= [but for but in candidate.children if but.lemma_=='but']
                        for conjadj in conjadjs :
                            try:
                                if len(alteraction)==0:
                                    if len(neg) > 0:
                                        a_dict[subj].append('not'+ ' ' + str(conjadj))
                                    elif len(neg)==0:
                                        a_dict[subj].append(str(conjadj))     
                                elif len(alteraction)>0:
                                    a_dict[subj].append(str(conjadj))
                            except KeyError:
                                pass
                    elif dep in ['dobj', 'attr', 'conj']:
                        subadjs = [adj for adj in candidate.children if adj.pos_=='ADJ']
                        for subadj in subadjs:
                            try:
                                if len(neg) > 0: 
                                    a_dict[subj].append(str('not' + ' ' + str(subadj)))
                                elif len(neg)==0:
                                    a_dict[subj].append(str(subadj))
                            except KeyError:
                                pass
                    else:
                        pass
    return a_dict

############| Fuction that finds and adjusts opinions (adjectives) in a way that allow adjectives where the connection between    ############   noun and adjective pass through 'of' 

def comp_adjectives(a_dict):

    for noun in list(a_dict.keys()):
        children= noun[0].children
        for child in children:
            if str(child) == 'of':
                of_children=[(of_child,) for of_child in child.children if of_child.pos_=='NOUN']  #Set the 'of' children
                
                if len(of_children)>0:
                    comp_of_child= [comp for comp in of_children[0][0].children 
                                        if (comp.pos_=='NOUN') and (comp.dep_=='compound')]     #Set compunds nouns
                    and_children=[(and_child,) for and_child in of_children[0][0].children 
                                      if (and_child.pos_=='NOUN') and (and_child.dep_=='conj')] # Deal with conjunctions
                    comp_adj=[adj for adj in a_dict[noun]]
                    
                    #Set the 'of' noun child in a way that take into consideration also compound nouns
                    if len(comp_of_child)>0:                                                   
                        of_child= (of_children[0][0],comp_of_child[0])
                    else:
                        of_child= of_children[0]    
                    
                    
                    #Associate the previous adjectives to the nouns coming from the 'of' structure
                    for adj in comp_adj:
                        a_dict[of_child].append(str(adj)+' '+str(noun[0]))
                        if len(and_children)>0:
                            comp_and_child= [comp for comp in and_children[0][0].children 
                                                if (comp.pos_=='NOUN') and (comp.dep_=='compound')]
                            if len(comp_and_child)>0:
                                and_child=(and_children[0][0],comp_and_child[0])
                            else: 
                                and_child=and_children[0]
                            a_dict[and_child].append(str(adj)+' '+str(noun[0]))

    
    return a_dict

######################| Fuction to clean the dictionary of aspect-opinions and associate the pair with the corresponding sentece

def clean_dict(a_dict,sentences):
    
    for noun in list(a_dict.keys()):
        if len(a_dict[noun])==0:
            
            del a_dict[noun]
            del sentences[noun]
            
    sentences=[sentence for key,sentence in sentences.items()]
            
    return a_dict,sentences
