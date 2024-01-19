from BPlusTree import BplusTree

#read the contents of the text file and build B+ tree index
def build_bplus_tree_index(file_path, bplustree):
    with open(file_path, 'rb') as file:
        file_offset = 0 #intial
        for line in file:
            line = str(line, 'utf-8').strip()
            value = (line[:25] + ' ' * (25 - len(line)))[:25] #truncate or pad to 25 characters
            bplustree.insert(value, file_offset)
            file_offset = file.tell()  #get the current file offset for the next iteration

def lookup(bplustree,key,path):
    result = bplustree.lookup(key,path)
    if result is not None:
        print(f"'{result}' found in the  B+ tree index!")
    else:
        print(f"Key '{key}' not found in the B+ tree index.")

def main():            
    order = 4 #number of elements in each node
    bplustree = BplusTree(order)
    build_bplus_tree_index('sai.txt', bplustree)
    bplustree.print_tree()
    bplustree.write_to_file('bplustree_index.dat')  
    
    key='gala'  
    lookup(bplustree,key,'sai.txt')
    
main()