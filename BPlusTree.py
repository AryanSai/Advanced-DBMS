import math,struct
from Node import Node

class BplusTree:
    def __init__(self, order):
        self.root = Node(order) #creating an empty root node

    def search(self, value):
        current = self.root #start from the root
        while not current.check_leaf: #cotinue search until u find a leaf node
            curr_values = current.values
            #search in that leaf node
            for i in range(len(curr_values)):
                    #when value equal to current value in the node, move right
                if value == curr_values[i]:
                    current = current.pointers[i + 1]
                    break
                elif value < curr_values[i]:
                    #when value equal to current value in the node, move left
                    current = current.pointers[i]
                    break
                #if value > curr_values[i], then we just continue
                elif i + 1 == len(current.values):
                    #when reached the end
                    current = current.pointers[i + 1]
                    break
        return current
    
    # Insert operation
    def insert(self, value, file_offset):
        #find the location where the value fits
        old_node = self.search(value) 
        
        #insert the value in the node
        old_node.insert_at_leaf(value, file_offset)
        
        #splitting the node when size exceeds the order
        if len(old_node.values) == old_node.order:
            new_node = Node(old_node.order, is_leaf=True) #create a new node
            new_node.parent = old_node.parent #set the parent
            mid = int(math.ceil(old_node.order / 2)) - 1
            #move the second half of data to the new node
            new_node.values = old_node.values[mid + 1:]
            new_node.file_offsets = old_node.file_offsets[mid + 1:]
            #let the first half of data to be with the old node
            old_node.values = old_node.values[:mid + 1]
            old_node.file_offsets = old_node.file_offsets[:mid + 1]
            #connect the old node to the new node
            old_node.nextLeafNode = new_node
            self.update_parent(old_node, new_node.values[0], new_node)

    #used for updating the parent after a split operation
    def update_parent(self, old_node, value, new_node):
        #if root is the node that got split, create a new root
        if self.root == old_node:
            #create a new node
            rootNode = Node(old_node.order, is_leaf=False)
            #give the values to the new root
            rootNode.values = [value]
            #old and new_nodes now become children of the new root
            rootNode.pointers = [old_node, new_node]
            #set the root of the tree to be the new rootNode and also change parents to the root
            self.root = rootNode
            old_node.parent = rootNode
            new_node.parent = rootNode
            return
        #when root is the node that is split, find the parent of the node that got split
        parent_Node = old_node.parent
        temp = parent_Node.pointers
        for i in range(len(temp)):
            if temp[i] == old_node:
                #put it in the correct place
                parent_Node.values = parent_Node.values[:i] + [value] + parent_Node.values[i:]
                parent_Node.pointers = parent_Node.pointers[:i + 1] + [new_node] + parent_Node.pointers[i + 1:]
                #check if the parent is full, if so then split it also
                if len(parent_Node.pointers) > parent_Node.order:
                    #create a new parent
                    new_parent = Node(parent_Node.order, is_leaf=False)
                    new_parent.parent = parent_Node.parent
                    mid = int(math.ceil(parent_Node.order / 2)) - 1
                    new_parent.values = parent_Node.values[mid + 1:]
                    new_parent.pointers = parent_Node.pointers[mid + 1:]
                    value_ = parent_Node.values[mid]
                    if mid == 0:
                         #if mid is 0, update values in the parent node
                        parent_Node.values = parent_Node.values[:mid + 1]
                    else:
                        #update values in the parent node
                        parent_Node.values = parent_Node.values[:mid]
                    #update pointers in the parent node    
                    parent_Node.pointers = parent_Node.pointers[:mid + 1]
                    #update parent pointers for the pointers in both the nodes
                    for j in parent_Node.pointers:
                        j.parent = parent_Node
                    for j in new_parent.pointers:
                        j.parent = new_parent
                    #recursively call for balancing    
                    self.update_parent(parent_Node, value_, new_parent)

     
    # Print the tree(BFS)
    def print_tree(self):
        explored = [self.root]
        levels = [0]
        while len(explored) != 0:
            current = explored.pop(0)
            level = levels.pop(0)
            if not current.check_leaf:
                for item in current.pointers:
                    # print("internal: ",current.file_offsets, item.values, current.pointers)
                    explored.append(item)
                    levels.append(level + 1)
            else:
                print(current.file_offsets, current.values)

    # Write the B+ tree index to a binary file
    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            self.write_node_to_file(file, self.root)

    # method for writing a node to the file
    def write_node_to_file(self, file, node):
        # Write node information to the file
        file.write(struct.pack('I', node.order))
        file.write(struct.pack('?', node.check_leaf))
        file.write(struct.pack('I', len(node.values)))

        for value, file_offsets in zip(node.values, node.file_offsets):
            if isinstance(value, str):
                value_bytes = value.encode('utf-8')
            else:
                value_bytes = value

            file.write(struct.pack('25s', value_bytes))
            file.write(struct.pack('I', len(file_offsets)))
            for offset in file_offsets:
                file.write(struct.pack('Q', offset))

        # If it's an internal node, recursively write child nodes
        if not node.check_leaf:
            for child_node in node.pointers:
                self.write_node_to_file(file, child_node)

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
        
        with open(file_path, 'rb') as file:
            file.seek(offset[0])
            line = file.readline().decode('utf-8').strip()
        return line