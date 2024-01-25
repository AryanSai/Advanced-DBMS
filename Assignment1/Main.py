from BPlusTree import BPlusTree
import pickle

#read the contents of the text file and build B+ tree index
def build_bplus_tree_index(file_path, bplustree):
    with open(file_path, 'rb') as file:
        file_offset = 0 #intial
        for line in file:
            line = str(line, 'utf-8').strip()
            value = (line[:25] + ' ' * (25 - len(line)))[:25] #truncate or pad to 25 characters
            bplustree.insert(value, file_offset)
            file_offset = file.tell()  #get the current file offset for the next iteration

#lookup the tree for a key
def lookup(bplustree,key,path):
    result = bplustree.lookup(key,path)
    if result is not None:
        print(f"\n'{result}' found in the  B+ tree index!")
    else:
        print(f"\nKey '{key}' not found in the B+ tree index.")

# serialize the B+ tree
def create_binfile(bplustree):
        serialized_tree = pickle.dumps(bplustree)
        # save the serialized data to a binary file
        with open("bplus_tree.bin", "wb") as binary_file:
            binary_file.write(serialized_tree)

# deserialize the B+ tree
def load_binfile():
        with open("bplus_tree.bin", "rb") as binary_file:
            serialized_tree = binary_file.read()
        # deserialize the B+ tree using pickle
        bplus_tree = pickle.loads(serialized_tree)  
        return bplus_tree

def main():            
    order = 4 #number of elements in each node
    path='/home/aryan/Desktop/MTech/DBMS(P)/Assignment1/input2.txt'
    
    bplustree = BPlusTree(order)
    
    build_bplus_tree_index(path, bplustree)
    print('\nB+ Tree created......')
    
    print('\nBinary file created......')
    create_binfile(bplustree)
    
    print('\nLoaded the index tree from the binary file......')
    bplus_tree = load_binfile()
    
    print('\nLooking up the B+ tree......')    
    lookup(bplus_tree,'xylo',path)
    lookup(bplus_tree,'ggg',path)
    
    print('\nPrinting the B+ tree......')
    bplus_tree.print_tree()
    
    print('\nDeleting a key from the B+ tree......')    
    bplus_tree.delete('Aryan Sai')
    
    print('\nPrinting the B+ tree after deletion......')
    bplus_tree.print_tree()
    
main()