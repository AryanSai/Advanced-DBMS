# Node creation
class Node:
    def __init__(self, order, is_leaf=True):
        self.order = order
        self.pointers = []   #references for internal nodes
        self.next_leaf_node = None #reference to next node
        self.parent = None #reference to parent node
        self.check_leaf = is_leaf 
        self.values = [] #for leaf nodes
        self.file_offsets = [] #offsets of the file
    
    # Insert at the leaf   
    def insert_at_leaf(self, value, file_offset):
        if self.values:
            curr_values=self.values
            for i in range(len(curr_values)):
                if value == curr_values[i]: #duplicate values
                    #if duplicate, just append the offset to the list
                    self.file_offsets[i].append(file_offset)
                    break
                elif value < curr_values[i]:
                     #when value less than the curr_leaf value, insert in the sorting order
                    self.values=self.values[:i]+[value]+self.values[i:]
                    self.file_offsets = self.file_offsets[:i] + [[file_offset]] + self.file_offsets[i:]
                    break
                #if value > curr_values[i], then we just continue
                elif i + 1 == len(curr_values): #when greater, append to the lists
                    self.values.append(value)
                    self.file_offsets.append([file_offset])
                    break
        else: #when the leaf is empty
            self.values = [value]
            self.file_offsets = [[file_offset]]