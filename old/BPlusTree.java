package old;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.LinkedList;
import java.util.Queue;

class BPlusTree {

    private static final int MAX_KEYS = 3; // Order of the B+ tree
    private static final int MAX_CHILDREN = MAX_KEYS + 1;

    private Node root;

    // Node class for B+ Tree
    private static class Node {
        boolean isLeaf;
        int numKeys;
        String[] keys;
        long[] offsets; // File offsets for leaf nodes
        Node[] children;
        Node next; // Pointer to next leaf node

        Node(boolean isLeaf) {
            this.isLeaf = isLeaf;
            keys = new String[MAX_KEYS];
            offsets = new long[MAX_KEYS];
            children = new Node[MAX_CHILDREN];
        }
    }

    // Builds the in-memory B+ tree index from a text file
    public void buildIndex(String filename) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            long offset = 0;
            String line;
            while ((line = reader.readLine()) != null) {
                insert(formatKey(line), offset);
                offset += line.length() + 1; // Add 1 for newline character
            }
        }
    }

    // Formats a key to 25 characters (padding or truncating)
    private String formatKey(String key) {
        return String.format("%-25s", key).substring(0, 25);
    }

    // Inserts a key-offset pair into the B+ tree
    private void insert(String key, long offset) {
        if (root == null) {
            root = new Node(true);
            root.keys[0] = key;
            root.offsets[0] = offset;
            root.numKeys = 1;
        } else {
            Node leaf = findLeafNode(key);
            // Handle leaf node overflow
            if (leaf.numKeys == MAX_KEYS) {
                // splitNode(leaf);
                leaf = findLeafNode(key); // Re-find leaf after potential split
            }
            insertIntoLeaf(leaf, key, offset);
        }
    }

    // Inserts a key-offset pair into a leaf node
    private void insertIntoLeaf(Node leaf, String key, long offset) {
        int index = 0;

        // Find the correct position to insert the key
        while (index < leaf.numKeys && key.compareTo(leaf.keys[index]) > 0) {
            index++;
        }

        // Shift keys and offsets to make space for the new key
        System.arraycopy(leaf.keys, index, leaf.keys, index + 1, leaf.numKeys - index);
        System.arraycopy(leaf.offsets, index, leaf.offsets, index + 1, leaf.numKeys - index);

        // Insert the new key and offset
        leaf.keys[index] = key;
        leaf.offsets[index] = offset;
        leaf.numKeys++;
    }

    private Node findLeafNode(String key) {
        Node current = root;
        while (!current.isLeaf) {
            int i;
            for (i = 0; i < current.numKeys; i++) {
                if (key.compareTo(current.keys[i]) < 0) {
                    break;
                }
            }
            current = current.children[i];
        }
        return current;
    }

    // private void splitNode(Node node) {
    //     Node parent = findParent(node);
    //     int middleIndex = node.numKeys / 2;
    //     String middleKey = node.keys[middleIndex];
    //     long middleOffset = node.offsets[middleIndex];

    //     Node newSibling = new Node(node.isLeaf);
    //     newSibling.numKeys = node.numKeys - middleIndex - 1;
    //     System.arraycopy(node.keys, middleIndex + 1, newSibling.keys, 0, newSibling.numKeys);
    //     System.arraycopy(node.offsets, middleIndex + 1, newSibling.offsets, 0, newSibling.numKeys);

    //     node.numKeys = middleIndex;
    //     newSibling.next = node.next;
    //     node.next = newSibling;

    //     if (parent == null) {
    //         // Create a new root
    //         parent = new Node(false);
    //         root = parent;
    //         parent.keys[0] = middleKey;
    //         parent.offsets[0] = middleOffset;
    //         parent.children[0] = node;
    //         parent.children[1] = newSibling;
    //         parent.numKeys = 1;
    //     } else {
    //         // Insert the middle key into the parent
    //         int i;
    //         for (i = 0; i < parent.numKeys; i++) {
    //             if (middleKey.compareTo(parent.keys[i]) < 0) {
    //                 break;
    //             }
    //         }
    //         // Shift keys and children to make space for the new key and child
    //         System.arraycopy(parent.keys, i, parent.keys, i + 1, parent.numKeys - i);
    //         System.arraycopy(parent.offsets, i, parent.offsets, i + 1, parent.numKeys - i);
    //         System.arraycopy(parent.children, i, parent.children, i + 1, parent.numKeys - i + 1);

    //         parent.keys[i] = middleKey;
    //         parent.offsets[i] = middleOffset;
    //         parent.children[i + 1] = newSibling;
    //         parent.numKeys++;
    //     }
    // }

    private Node findParent(Node node) {
        Node current = root;
        Node parent = null;
        while (current != null && !current.isLeaf) {
            int i;
            for (i = 0; i < current.numKeys; i++) {
                if (node.keys[0].compareTo(current.keys[i]) < 0) {
                    break;
                }
            }
            parent = current;
            current = current.children[i];
        }
        return parent;
    }

    // Display the B+ tree level by level
    public void displayTree() {
        if (root == null) {
            System.out.println("Empty tree");
            return;
        }

        Queue<Node> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                Node current = queue.poll();
                System.out.print("[ ");
                for (int j = 0; j < current.numKeys; j++) {
                    System.out.print(current.keys[j] + " ");
                }
                System.out.print("] ");
                if (!current.isLeaf) {
                    for (int j = 0; j <= current.numKeys; j++) {
                        if (current.children[j] != null) {
                            queue.offer(current.children[j]);
                        }
                    }
                }
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        BPlusTree bPlusTree = new BPlusTree();
        try {
            bPlusTree.buildIndex("sai.txt");
            bPlusTree.displayTree();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
