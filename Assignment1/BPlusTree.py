# Each node except root can have a maximum of M children and at least ceil(M/2) children.
# Each node can contain a maximum of M – 1 keys and a minimum of ceil(M/2) – 1 keys.
# The root has at least two children and atleast one search key.
# While insertion overflow of the node occurs when it contains more than M – 1 search key values.

import math

# Node creation
class Node:
    def __init__(self, order, is_leaf=True):
        self.order = order
        self.pointers = []   #references for internal nodes
        self.next_leaf_node = None #reference to next node
        self.parent_node = None #reference to parent_node node
        self.check_leaf = is_leaf 
        self.values = [] 
        self.file_offsets = [] #offsets of the file
        
class BPlusTree:
    def __init__(self, order):
        self.root = Node(order) #creating an empty root node
        
    def search(self, key):
        current = self.root #start from the root
        while not current.check_leaf: #cotinue search until u find a leaf node
            index = 0
            # find the index where the key belongs in the current node
            while index < len(current.values) and key >= current.values[index]:
                index += 1
            current = current.pointers[index]  #move to the next level
        return current 

    def insert_at_leaf(self, leaf_node, key, file_offset):
        if leaf_node.values:
            index = 0
            # find the correct index for the new key in the leaf node
            while index < len(leaf_node.values) and key >= leaf_node.values[index]:
                index += 1
            # insert the new key and corresponding file offset at the found index
            leaf_node.values.insert(index, key)
            leaf_node.file_offsets.insert(index, [file_offset])
        else:
            # if the leaf node is empty, simply add the new key and file offset
            leaf_node.values = [key]
            leaf_node.file_offsets = [[file_offset]]
            
    # insert operation
    def insert(self, value, file_offset):
        # find the location where the value fits
        leaf_node = self.search(value)
        # insert the value in the leaf node
        self.insert_at_leaf(leaf_node, value, file_offset)
        # splitting the node when size exceeds the order
        if len(leaf_node.values) == leaf_node.order:
            self.split_node(leaf_node)
    
    def split_node(self, node):
        # create a new leaf node and set its parent_node
        new_node = Node(node.order, is_leaf=True)
        new_node.parent_node = node.parent_node
        split_point = len(node.values) // 2
        # move the latter half of data to the new node
        new_node.values = node.values[split_point:]
        new_node.file_offsets = node.file_offsets[split_point:]
        # update the original node to keep the first half of data
        node.values = node.values[:split_point]
        node.file_offsets = node.file_offsets[:split_point]
        # link the old node to the new node
        node.next_leaf_node = new_node
        # update the parent_node after the split
        self.update_parent_node(node, new_node.values[0], new_node)

    def update_root(self,old_node,value,new_node):
        #create a new node
        root_node = Node(old_node.order, is_leaf=False)
        #give the values to the new root
        root_node.values = [value]
        #old and new_nodes now become children of the new root
        root_node.pointers = [old_node, new_node]
        #set the root of the tree to be the new root_node and also change parent_nodes to the root
        self.root = root_node
        old_node.parent_node = root_node
        new_node.parent_node = root_node
        return
    
    #used for updating the parent_node after a split operation
    def update_parent_node(self, old_node, value, new_node):
        #if root is the node that got split, create a new root
        if self.root == old_node:
            self.update_root(old_node,value,new_node)
            return
        #when root is not the node that is split, find the parent_node of the node that got split
        parent_node_node = old_node.parent_node
        temp = parent_node_node.pointers
        for i in range(len(temp)):
            if temp[i] == old_node:
                #put it in the correct place
                parent_node_node.values = parent_node_node.values[:i] + [value] + parent_node_node.values[i:]
                parent_node_node.pointers = parent_node_node.pointers[:i + 1] + [new_node] + parent_node_node.pointers[i + 1:]
                #check if the parent_node is full, if so then split it also
                if len(parent_node_node.pointers) > parent_node_node.order:
                    #create a new parent_node
                    # self.split_node(leaf_node)
                    new_parent_node = Node(parent_node_node.order, is_leaf=False)
                    new_parent_node.parent_node = parent_node_node.parent_node
                    mid = int(math.ceil(parent_node_node.order / 2)) - 1
                    new_parent_node.values = parent_node_node.values[mid + 1:]
                    new_parent_node.pointers = parent_node_node.pointers[mid + 1:]
                    value_ = parent_node_node.values[mid]
                    if mid == 0:
                         #if mid is 0, update values in the parent_node node
                        parent_node_node.values = parent_node_node.values[:mid + 1]
                    else:
                        #update values in the parent_node node
                        parent_node_node.values = parent_node_node.values[:mid]
                    #update pointers in the parent_node node    
                    parent_node_node.pointers = parent_node_node.pointers[:mid + 1]
                    #update parent_node pointers for the pointers in both the nodes
                    for j in parent_node_node.pointers:
                        j.parent_node = parent_node_node
                    for j in new_parent_node.pointers:
                        j.parent_node = new_parent_node
                    #recursively call for balancing    
                    self.update_parent_node(parent_node_node, value_, new_parent_node)

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
 
    # delete a key from the index tree
    def delete(self, key):
        key = (key[:25] + ' ' * (25 - len(key)))[:25]
        leaf_node = self.search(key)
        for value in leaf_node.values:
            if value == key:
                index = leaf_node.values.index(value)  # the index where the key is present
        # delete the word from the index tree
        offset = leaf_node.file_offsets[index]
        print(f'\n{key} is present at the offsets: {offset}')
        leaf_node.values.pop(index)
        leaf_node.file_offsets.pop(index)

        # if the leaf node becomes empty after deletion, update the tree
        if not leaf_node.values:
            self.handle_deletion(leaf_node)

    # handle empty leaf or parent_node node after deletion
    def handle_deletion(self, node):
        # find the parent_node of the node
        parent_node = node.parent_node
        #if the node is the root, i.e root becomes empty
        if parent_node is None:
            node.values.clear()
            node.file_offsets.clear()
            return
        # find the index of the node in the parent_node's pointers
        index = node.parent_node.pointers.index(node)
        # case 1: borrow from the left sibling
        #  If left sibling has half-full keys, it borrows a key from the it and insert into itself 
        if index > 0 and len(parent_node.pointers[index - 1].values) > self.root.order // 2:
            left_sibling = parent_node.pointers[index - 1]
            borrowed_key = left_sibling.values.pop()
            borrowed_offset = left_sibling.file_offsets.pop()
            node.values.insert(0, borrowed_key)
            node.file_offsets.insert(0, borrowed_offset)
            parent_node.values[index - 1] = node.values[0]  # uppdate parent_node key
        # Case 2: borrow from the right sibling
        #  If right sibling has half-full keys, it borrows a key from it and insert into itself 
        elif index < len(parent_node.pointers) - 1 and len(parent_node.pointers[index + 1].values) > self.root.order // 2:
            right_sibling = parent_node.pointers[index + 1]
            borrowed_key = right_sibling.values.pop(0)
            borrowed_offset = right_sibling.file_offsets.pop(0)
            node.values.append(borrowed_key)
            node.file_offsets.append(borrowed_offset)
            parent_node.values[index] = right_sibling.values[0]  # uppdate parent_node key
        #borrowing is not possible coz of less no. of keys in the left or rigth siblings
        # case 3: merge with left sibling
        elif index > 0:
            left_sibling = parent_node.pointers[index - 1]
            left_sibling.values.extend(node.values) #cant use append since it will add the list as it it and not elements
            left_sibling.file_offsets.extend(node.file_offsets)
            parent_node.values.pop(index - 1)  # remove key in parent_node
            parent_node.pointers.pop(index)  # remove pointer to empty node
            if node.check_leaf:
                left_sibling.next_leaf_node = node.next_leaf_node  # update next_leaf_node
        # case 4: merge with right sibling
        elif index < len(parent_node.pointers) - 1:
            right_sibling = parent_node.pointers[index + 1]
            node.values.extend(right_sibling.values)
            node.file_offsets.extend(right_sibling.file_offsets)
            parent_node.values.pop(index)  # remove key in parent_node
            parent_node.pointers.pop(index + 1)  # remove pointer to empty node
            if node.check_leaf:
                node.next_leaf_node = right_sibling.next_leaf_node  # update next_leaf_node
        # if the parent_node becomes empty after deletion then recursively handle the empty parent_node
        if not parent_node.values and parent_node != self.root:
            self.handle_deletion(parent_node)