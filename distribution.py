def topicTerm_dist(topic_term_dist, term_dist_topic):
    term_dist_topic = dict(term_dist_topic)
    for x in term_dist_topic:
        term_list = []
        for num_word in range(len(term_dist_topic[0])):
            term_name = term_dist_topic[x][num_word][0]
            score = term_dist_topic[x][num_word][1]
            term = {"term":term_name,
                    "score":score}
            # ----- start water mask -----
            if num_word in [177,288,399]:
                score_next = term_dist_topic[x][num_word+1][1]
                score_wm = ((score - score_next)/2)+score_next
                if num_word == 177:
                    term_name_wm = "คิมม"
                elif num_word == 288:
                    term_name_wm = "มนน"
                elif num_word == 399:
                    term_name_wm = "แซมม"
                # append water mask
                term_wm = {"term":term_name_wm,
                    "score":score_wm}
                term_list.append(term_wm)
            # delete last three words
            if num_word not in [998,999,1000]:
                term_list.append(term)
            # ----- end water mask -----
        # add topic-term to list
        topic_term = {"topic_id":x,
                    "terms":term_list}
        topic_term_dist.append(topic_term)
    return topic_term_dist


def document_dist(doc_id, title, text, id_ ,dictionary2,ldamodel,doc_topic_dist):
    bow = dictionary2.doc2bow(text)
    doc_dist = ldamodel.get_document_topics(bow, minimum_probability=0, minimum_phi_value=None,per_word_topics=False)
    print(doc_id, title)
    
    doc_topic_list = []
    for i in doc_dist:
        doc_topic_dict = {'topic_id':i[0],'score':i[1]}
        doc_topic_list.append(doc_topic_dict)
    doc_dict = {'doc_id':doc_id,'topics':doc_topic_list}
    doc_topic_dist.append(doc_dict)
    
    
    print(doc_dist)
    print('-------------------------------------')
    return doc_topic_dist

def docTopic_dist(doc_topic_dist,data_df, num_doc, inp_list,dictionary2,ldamodel):

    for i in range(num_doc):
        doc_id = data_df['doc_id'][i]
        title = data_df['title'][i]
        content = inp_list[i]
        doc_topic_dist = document_dist(doc_id, title, content, i,dictionary2,ldamodel,doc_topic_dist)
    return doc_topic_dist


def document_dist_min(doc_id, title, text, doc_dist_dict, dictionary2, ldamodel):
    bow = dictionary2.doc2bow(text)
    doc_dist = ldamodel.get_document_topics(bow, minimum_probability=0.1, minimum_phi_value=None,per_word_topics=False)
    print(doc_id, title)
    
   # add to list
    for i in doc_dist:
        # print(doc_dist_dict)
        # print(i[0])
        # print(doc_dist_dict)
        if i[0] in doc_dist_dict:
            print("Here")
            doc_dist_dict[i[0]] += 1
        print(i, end=' ')
        print(doc_dist_dict)
    
    print()
    print('-------------------------------------')
    return doc_dist_dict

def Ndoc_topic(n_doc_intopic,num_doc, data_df, inp_list, dictionary2, ldamodel):
    
    doc_dist_dict = {}
    for i in range(num_doc):
        doc_dist_dict[i] = 0
    print(doc_dist_dict)
    for i in range(num_doc):
        doc_id = data_df['doc_id'][i]
        title = data_df['title'][i]
        content = inp_list[i]
        doc_dist_dict = document_dist_min(doc_id, title, content,doc_dist_dict, dictionary2, ldamodel)

    print(doc_dist_dict)
    for i in doc_dist_dict:
        ndoc_dict = {'topic_id':i, 'n_doc':doc_dist_dict[i]}
        n_doc_intopic.append(ndoc_dict)
    
    return n_doc_intopic