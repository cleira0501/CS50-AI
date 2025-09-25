import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution(dictionary format) over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transit_prob = dict() #initialize a dict
    total_pages= len(corpus.keys())# total number of pages
    num_linked = len(corpus[page])#total pages linked to in this page

    if num_linked == 0:#If there are no outgoing links to this page
        for linked_page in corpus.keys():#loop through all pages
            transit_prob[linked_page] =  1/total_pages
    else:
        for linked_page in corpus.keys():#loop through all pages
            if linked_page in corpus[page]:#if a page is linked to the given page
                transit_prob[linked_page] = damping_factor*1/num_linked + (1-damping_factor)*1/total_pages
            else:# if this page is not linked to page
                transit_prob[linked_page] = (1-damping_factor)*1/total_pages
    return transit_prob


    # print(page)
    # if not corpus[page] or (page not in corpus):# if there are no outgoing links
    #     # print("no outgoing links")
    #     for key in corpus.keys():# loop through all pages 
    #         transit_prob[key] = (1 / len(corpus.keys()))# all pages have equal probablity
    #     return transit_prob

    # pages_to_visit = corpus[page] #all linked pages to current page
    # print(f"linked pages{pages_to_visit}")
    # for linked_page in pages_to_visit:# loop through all linked pages
    #     #first assign all probability to the linked pages
    #     transit_prob[linked_page] = damping_factor * (1 / len(pages_to_visit))
    # print(transit_prob)
    # for key in list(corpus.keys()):# loop through all pages 
    #         if key == page:#skip over the current page
    #             continue
    #         if key in list(transit_prob.keys()):
    #             curr_prob = transit_prob[key]
    #             transit_prob[key] = curr_prob + (1 - damping_factor) * (1 / (len(list(corpus.keys())) - 1 ))
    #         else:
    #             transit_prob[key] = (1 - damping_factor) * (1 / (len(list(corpus.keys())) - 1 ))
    # return transit_prob

                                              


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
  
    page_rank = {key : 0 for key in corpus.keys()}#initialize a dict key = page value = 0
    curr_page = random.choice(list(corpus.keys()))#initialize the first page
    page_rank[curr_page] += 1/n
    for _ in range(n-2):
        next_candidates = list(transition_model(corpus, curr_page, damping_factor).keys())
        next_prob = list(transition_model(corpus, curr_page, damping_factor).values())
        next_page = random.choices(next_candidates, next_prob, k=1)#choose a next page randomly
        page_rank[next_page[0]] += 1/n
        curr_page = next_page[0]# move pointer
    #test
    if abs(sum(list(page_rank.values())) - 1) <= 0.001:
        print("passed test")
    return page_rank






    #for i in range(n-2):
    #     curr_transit = transition_model(corpus, curr_page, damping_factor)
    #     curr_page = random.choices(list(curr_transit.keys()), weights = list(curr_transit.values()), k = 1)[0]# choose the next random page
    #     print(f"curr page: {curr_page}")
    #     print(f"curr dict: {page_occur}")
    #     if curr_page in page_occur.keys():
    #         page_occur[curr_page] += 1 # update the occurence of that page
    #         print(f"curr dict: {page_occur}")
    #     else:
    #         page_occur[curr_page] = 1 
    #         print(f"curr dict: {page_occur}")
 
    
    # for key in page_occur:
    #     page_occur[key] = page_occur[key] / n #normalization

    # return page_occur


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    num_pages = len(list(corpus.keys()))
    page_rank = {page: 1/num_pages for page in corpus}  #initialize
    incoming_links = {page: [] for page in corpus} #initialize a reverse dictionary
    for key in list(corpus.keys()):
        for value in list(corpus[key]):
            incoming_links[value].append(key)
        

    converged = False

    while not converged:
        converged = True
        new_dict = {}
        for key in page_rank:#loop over each page
            val_1 = (1-damping_factor)/num_pages
            sum_pages = 0 
            for page_linked in incoming_links[key]:#pages that links to this page
                num_links = len(list(corpus[page_linked]))
                sum_pages += page_rank[page_linked]/num_links
            new_pr = val_1+ damping_factor* sum_pages
            new_dict[key] = new_pr
            if abs(new_pr - page_rank[key])>=0.001:
                converged = False
        page_rank = new_dict
    return page_rank



    # for key in corpus:# for all pages
    #     page_rank[key] = 1 / len(corpus) # initialize all pages to have page rank of 1/n
    # while not converged:
    #     converged = True
    #     new_pr = {key: None for key in corpus}#initialize a new dict to store new pr values

    #     for curr_page in corpus.keys():# for all pages
    #         summation = 0
    #         for page in corpus.keys():#loop through all linked pages of a page
    #             # if curr_page is page:# skip over itself
    #             #     continue
    #             if not corpus[page]:# if there are no outbound links
    #                 summation += page_rank[page] / n
    #             elif curr_page in corpus[page]:
    #                 summation += page_rank[page] / len(corpus[page])
    #         new_pr[curr_page] = (1-damping_factor) / n + (damping_factor * summation)
                    
    #         if not new_pr[curr_page]:# if there are no links to this page
    #             new_pr[curr_page] = (1-damping_factor) / n
     
    #         if abs(new_pr[curr_page] - page_rank[curr_page]) >=  0.001:#condition to stop the reucursion
    #             converged = False
    #     page_rank = new_pr.copy()
    # return page_rank
            

 



if __name__ == "__main__":
    main()
