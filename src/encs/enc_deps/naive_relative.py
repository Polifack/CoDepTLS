from src.encs.abstract_encoding import ADEncoding
from src.models.deps_label import D_Label
from src.models.deps_tree import D_Tree
from src.utils.constants import D_NONE_LABEL

class D_NaiveRelativeEncoding(ADEncoding):
    def __init__(self, separator, hang_from_root):
        super().__init__(separator)
        self.hfr = hang_from_root

    def encode(self, dep_tree):
        encoded_labels = []
        dep_tree.remove_dummy()
        for node in dep_tree:
            li = node.relation 
            xi = node.delta_head()

            if node.relation == 'root' and self.hfr:
                xi = D_NONE_LABEL
            
            current = D_Label(xi, li, self.separator)
            encoded_labels.append(current)

        return encoded_labels

    def decode(self, labels, postags, words):
        dep_tree = D_Tree.empty_tree(len(labels)+1)

        for i in range(len(labels)):
            label  = labels[i]
            postag = postags[i]
            word   = words[i]
            
            if label.xi == D_NONE_LABEL:
                # set as root
                dep_tree.update_head(i+1, 0)
            else:
                dep_tree.update_head(i+1, int(label.xi)+(i+1))
                
            
            dep_tree.update_word(i+1, word)
            dep_tree.update_upos(i+1, postag)
            dep_tree.update_relation(i+1, label.li)

        dep_tree.remove_dummy()
        return dep_tree