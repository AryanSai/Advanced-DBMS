import math
from Node import Node

class BPlusTree:
    def __init__(self, order):
        self.root = Node(order) #creating an empty root node
    
    def search(self, key):
        current = self.root #start from the root
        while not current.check_leaf: #cotinue search until u find a leaf node
            curr_values = current.values
            #search in that leaf node
            for i in curr_values:#when key equal to current value in the node, move right
                if key == i:
                    current = current.pointers[curr_values.index(i) + 1]
                    break
                elif key < i:#when key less than current value in the node, move left
                    current = current.pointers[curr_values.index(i)]
                    break
                #if key > curr_values[i], then we just continue
                elif curr_values.index(i) + 1 == len(current.values):#when reached the end
                    current = current.pointers[curr_values.index(i) + 1]
                    break
        return current
    
    # insert operation
    def insert(self, value, file_offset):
        # find the location where the value fits
        leaf_node = self.search(value)
        # insert the value in the node
        leaf_node.insert_at_leaf(value, file_offset)
        # splitting the node when size exceeds the order
        if len(leaf_node.values) == leaf_node.order:
            self.split_node(leaf_node)

    # used for updating the parent after a split operation
    def split_node(self, node):
        new_node = Node(node.order, is_leaf=True)  # create a new leaf node
        new_node.parent = node.parent  # Set the parent
        mid = math.ceil(node.order / 2) - 1
        # move the second half of data to the new node
        new_node.values = node.values[mid + 1:]
        new_node.file_offsets = node.file_offsets[mid + 1:]
        # let the first half of data remain with the old node
        node.values = node.values[:mid + 1]
        node.file_offsets = node.file_offsets[:mid + 1]
        # connect the old node to the new node
        node.next_leaf_node = new_node
        # update the parent with the new node
        self.update_parent(node, new_node.values[0], new_node)


    #used for updating the parent after a split operation
    def update_parent(self, old_node, value, new_node):
        #if root is the node that got split, create a new root
        if self.root == old_node:
            #create a new node
            root_node = Node(old_node.order, is_leaf=False)
            #give the values to the new root
            root_node.values = [value]
            #old and new_nodes now become children of the new root
            root_node.pointers = [old_node, new_node]
            #set the root of the tree to be the new root_node and also change parents to the root
            self.root = root_node
            old_node.parent = root_node
            new_node.parent = root_node
            return
        #when root is the node that is split, find the parent of the node that got split
        parent_node = old_node.parent
        temp = parent_node.pointers
        for i in range(len(temp)):
            if temp[i] == old_node:
                #put it in the correct place
                parent_node.values = parent_node.values[:i] + [value] + parent_node.values[i:]
                parent_node.pointers = parent_node.pointers[:i + 1] + [new_node] + parent_node.pointers[i + 1:]
                #check if the parent is full, if so then split it also
                if len(parent_node.pointers) > parent_node.order:
                    #create a new parent
                    # self.split_node(leaf_node)
                    new_parent = Node(parent_node.order, is_leaf=False)
                    new_parent.parent = parent_node.parent
                    mid = int(math.ceil(parent_node.order / 2)) - 1
                    new_parent.values = parent_node.values[mid + 1:]
                    new_parent.pointers = parent_node.pointers[mid + 1:]
                    value_ = parent_node.values[mid]
                    if mid == 0:
                         #if mid is 0, update values in the parent node
                        parent_node.values = parent_node.values[:mid + 1]
                    else:
                        #update values in the parent node
                        parent_node.values = parent_node.values[:mid]
                    #update pointers in the parent node    
                    parent_node.pointers = parent_node.pointers[:mid + 1]
                    #update parent pointers for the pointers in both the nodes
                    for j in parent_node.pointers:
                        j.parent = parent_node
                    for j in new_parent.pointers:
                        j.parent = new_parent
                    #recursively call for balancing    
                    self.update_parent(parent_node, value_, new_parent)

    # print the tree(BFS)
    def print_tree(self):
        explored = [self.root]
        levels = [0]
        while len(explored) != 0:
            current = explored.pop(0) #bfs
            level = levels.pop(0)
            if not current.check_leaf:
                for item in current.pointers:
                    # print("internal: ",current.file_offsets, item.values, current.pointers)
                    explored.append(item)
                    levels.append(level + 1)
            else:
                print(current.file_offsets, current.values)
    
    #lookup for a key in the data file 
    def lookup(self, key, file_path):
        key = (key[:25] + ' ' * (25 - len(key)))[:25] #for equating
        leaf_node = self.search(key)
        # finding the offset corresponding to the key
        for value in leaf_node.values:
            if value == key:
                offset = leaf_node.file_offsets[leaf_node.values.index(value)]
                break
        else:
            return None
        
        #get the line from the data file
        with open(file_path, 'rb') as file:
            file.seek(offset[0])
            line = file.readline().decode('utf-8').strip()
        return line
    
    #delete a key from the index tree
    def delete(self,key):
        key = (key[:25] + ' ' * (25 - len(key)))[:25]
        leaf_node = self.search(key)
        for value in leaf_node.values:
            if value == key:
                index = leaf_node.values.index(value) #the index where the key is present
        
        #delete the word from the index tree  
        offset = leaf_node.file_offsets[index] 
        print(f'\n{key} is present at the offsets: {offset}') 
        leaf_node.values.pop(index) 
        leaf_node.file_offsets.pop(index)    