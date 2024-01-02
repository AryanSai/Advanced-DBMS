import math,struct

# Node creation
class Node:
    def __init__(self, order, is_leaf=True):
        self.order = order
        self.values = [] #for leaf nodes
        self.keys = []   #references for internal nodes
        self.nextLeafNode = None
        self.parent = None
        self.check_leaf = is_leaf
        self.file_offsets = [] #like pointers 

    # Insert at the leaf
    def insert_at_leaf(self, leaf, value, file_offset):
        if self.values:
            temp1 = self.values
            for i in range(len(temp1)):
                if value == temp1[i]:   #if already exists, just append the offset
                    self.file_offsets[i].append(file_offset)
                    break
                elif value < temp1[i]: #when value less than the curr_leaf value, insert in right position
                    self.values = self.values[:i] + [value] + self.values[i:]
                    self.file_offsets = self.file_offsets[:i] + [[file_offset]] + self.file_offsets[i:]
                    break
                elif i + 1 == len(temp1): #when greater, append to the lists
                    self.values.append(value)
                    self.file_offsets.append([file_offset])
                    break
        else: #when the leaf is empty
            self.values = [value]
            self.file_offsets = [[file_offset]]

# B plus tree
class BplusTree:
    def __init__(self, order):
        self.root = Node(order)

    # Insert operation
    def insert(self, value, file_offset):
        old_node = self.search(value)
        old_node.insert_at_leaf(old_node, value, file_offset)

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

    # Search operation for different operations
    def search(self, value):
        current = self.root #start from the root
        while not current.check_leaf: #cotinue search until u find a leaf node
            temp = current.values
            #search in that leaf node
            for i in range(len(temp)):
                    #when value equal to current value in the node, move right
                if value == temp[i]:
                    current = current.keys[i + 1]
                    break
                elif value < temp[i]:
                    #when value equal to current value in the node, move left
                    current = current.keys[i]
                    break
                elif i + 1 == len(current.values):
                    #when value is greater than all values in the node, move to rightmost
                    current = current.keys[i + 1]
                    break
        return current

    #used for updating the parent after a split operation
    def update_parent(self, old_node, value, new_node):
        #if root is the node that got split, create a new root
        if self.root == old_node:
            #create a new node
            rootNode = Node(old_node.order, is_leaf=False)
            #give the values to the new root
            rootNode.values = [value]
            #old and new_nodes now become children of the new root
            rootNode.keys = [old_node, new_node]
            #set the root of the tree to be the new rootNode and also change parents to the root
            self.root = rootNode
            old_node.parent = rootNode
            new_node.parent = rootNode
            return
        #when root is the node that is split, find the parent of the node that got split
        parent_Node = old_node.parent
        temp = parent_Node.keys
        for i in range(len(temp)):
            if temp[i] == old_node:
                #put it in the correct place
                parent_Node.values = parent_Node.values[:i] + [value] + parent_Node.values[i:]
                parent_Node.keys = parent_Node.keys[:i + 1] + [new_node] + parent_Node.keys[i + 1:]
                #check if the parent is full, if so then split it also
                if len(parent_Node.keys) > parent_Node.order:
                    #create a new parent
                    new_parent = Node(parent_Node.order, is_leaf=False)
                    new_parent.parent = parent_Node.parent
                    mid = int(math.ceil(parent_Node.order / 2)) - 1
                    new_parent.values = parent_Node.values[mid + 1:]
                    new_parent.keys = parent_Node.keys[mid + 1:]
                    value_ = parent_Node.values[mid]
                    if mid == 0:
                         #if mid is 0, update values in the parent node
                        parent_Node.values = parent_Node.values[:mid + 1]
                    else:
                        #update values in the parent node
                        parent_Node.values = parent_Node.values[:mid]
                    #update keys in the parent node    
                    parent_Node.keys = parent_Node.keys[:mid + 1]
                    #update parent pointers for the keys in both the nodes
                    for j in parent_Node.keys:
                        j.parent = parent_Node
                    for j in new_parent.keys:
                        j.parent = new_parent
                    #recursively call for balancing    
                    self.update_parent(parent_Node, value_, new_parent)

    # Print the tree
    def print_tree(self):
        lst = [self.root]
        level = [0]

        while len(lst) != 0:
            x = lst.pop(0)
            lev = level.pop(0)
            if not x.check_leaf:
                for i, item in enumerate(x.keys):
                    # print(item.values)
                    lst.append(item)
                    level.append(lev + 1)
            else:
                for i, item in enumerate(x.keys):
                    # print(item.values)
                    pass
                print("File Offsets:", x.file_offsets)

    # Write the B+ tree index to a binary file
    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            self.write_node_to_file(file, self.root)

    # Helper method for writing a node to the file
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
            for child_node in node.keys:
                self.write_node_to_file(file, child_node)

    def lookup(self, key, data_file_path):
        # Find the leaf node containing the key
        leaf_node = self.search(key)
    
        # Find the offset corresponding to the key
        for i, value in enumerate(leaf_node.values):
            if value == key:
                offset = leaf_node.file_offsets[i][0]
                break
        else:
            # Key not found in the leaf node
            return None
    
        try:
            # Read the line from the data file using the offset
            with open(data_file_path, 'rb') as data_file:
                data_file.seek(offset)
                line = data_file.readline().decode('utf-8').strip()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            # Handle file-related errors
            print(f"Error reading data file: {e}")
            return None
    
        return line


#read the contents of the text file and build B+ tree index
def build_bplus_tree_index(file_path, bplustree):
    with open(file_path, 'rb') as file:
        file_offset = 0
        for line in file:
            line = line.decode('utf-8').strip()
            value = (line[:25] + ' ' * (25 - len(line)))[:25] #truncate or pad to 25 characters
            bplustree.insert(value, file_offset)
            file_offset = file.tell()  #get the current file offset

def main():            
    order = 4 #number of elements in each node
    bplustree = BplusTree(order)
    build_bplus_tree_index('sai.txt', bplustree)
    bplustree.print_tree()
    bplustree.write_to_file('bplustree_index.dat')
    
    # Example: Lookup the contents of the data file for a specific key
    key_to_lookup = 'sai'
    result = bplustree.lookup(key_to_lookup, 'sai.txt')

    if result is not None:
        print(f"Contents of the data file for key '{key_to_lookup}': {result}")
    else:
        print(f"Key '{key_to_lookup}' not found in the B+ tree index.")
main()