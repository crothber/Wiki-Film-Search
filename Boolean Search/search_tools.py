from indexing_tools import get_stem

def combine(l1, l2):
    if type(l1[0]) == list:
        return l1+[l2]
    else:
        return [l1,l2]

def intersect(postings1, postings2, positional):
    ind1 = 0
    ind2 = 0
    intersection = []
    while ind1 < len(postings1) and ind2 < len(postings2):
        if postings1[ind1][0] == postings2[ind2][0]:
            if positional:
                intersection.append([postings1[ind1][0], combine(postings1[ind1][1], postings2[ind2][1])])
            elif not positional:
                intersection.append([postings1[ind1][0]])
            ind1 += 1
            ind2 += 1
        elif int(postings1[ind1][0]) < int(postings2[ind2][0]):
            ind1 += 1
        elif int(postings1[ind1][0]) > int(postings2[ind2][0]):
            ind2 += 1
    return intersection

def union(postings1, postings2, positional):
    ind1 = 0
    ind2 = 0
    if postings1 == []:
        return postings2
    if postings2 == []:
        return postings1
    union = [min(postings1[0], postings2[0], key=lambda x: int(x[0]))]
    while ind1 < len(postings1) or ind2 < len(postings2):
        if ind1 >= len(postings1) or ind2 >= len(postings2):
            if ind1 >= len(postings1):
                if postings2[ind2][0] != union[-1][0]:
                    union.append(postings2[ind2])
                ind2 += 1
            elif ind2 >= len(postings2):
                if postings1[ind1][0] != union[-1][0]:
                    union.append(postings1[ind1])
                ind1 += 1
        else:
            if postings1[ind1][0] == postings2[ind2][0]:
                if postings1[ind1][0] != union[-1][0]:
                    if positional:
                        union.append([postings1[ind1][0], [postings1[ind1][1], postings2[ind2][1]]])
                    elif not positional:
                        union.append([postings1[ind1][0]])
                ind1 += 1
                ind2 += 1
            elif int(postings1[ind1][0]) < int(postings2[ind2][0]):
                if postings1[ind1][0] != union[-1][0]:
                    union.append(postings1[ind1])
                ind1 += 1
            elif int(postings1[ind1][0]) > int(postings2[ind2][0]):
                if postings2[ind2][0] != union[-1][0]:
                    union.append(postings2[ind2])
                ind2 += 1
    return union
