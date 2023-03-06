from src.encs.abstract_encoding import ACEncoding
from src.utils.constants import C_ABSOLUTE_ENCODING, C_RELATIVE_ENCODING, C_ROOT_LABEL, C_CONFLICT_SEPARATOR, C_NONE_LABEL
from src.models.const_label import C_Label
from src.models.linearized_tree import LinearizedTree
from src.models.const_tree import C_Tree

import re

class C_NaiveDynamicEncoding(ACEncoding):
    def __init__(self, separator, unary_joiner):
        self.separator = separator
        self.unary_joiner = unary_joiner

    def __str__(self):
        return "Constituent Naive Dynamic Encoding"

    def encode(self, constituent_tree):
        lc_tree = LinearizedTree.empty_tree()
        leaf_paths = constituent_tree.path_to_leaves(collapse_unary=True, unary_joiner=self.unary_joiner)

        last_n_common=0
        for i in range(0, len(leaf_paths)-1):
            path_a=leaf_paths[i]
            path_b=leaf_paths[i+1]
            
            last_common=""
            n_commons=0
            for a,b in zip(path_a, path_b):

                if (a!=b):
                    # Remove the digits and aditional feats in the last common node
                    last_common = re.sub(r'[0-9]+', '', last_common)
                    last_common = last_common.split("##")[0]

                    # Get word and POS tag
                    word = path_a[-1]
                    postag = path_a[-2]
                    
                    # Build the Leaf Unary Chain
                    unary_chain = None
                    leaf_unary_chain = postag.split(self.unary_joiner)
                    if len(leaf_unary_chain)>1:
                        unary_list = []
                        for element in leaf_unary_chain[:-1]:
                            unary_list.append(element.split("##")[0])

                        unary_chain = self.unary_joiner.join(unary_list)
                        postag = leaf_unary_chain[len(leaf_unary_chain)-1]
                    
                    # Clean the POS Tag and extract additional features
                    postag_split = postag.split("##")
                    feats = [None]

                    if len(postag_split) > 1:
                        postag = re.sub(r'[0-9]+', '', postag_split[0])
                        feats = postag_split[1].split("|")
                    else:
                        postag = re.sub(r'[0-9]+', '', postag)

                    # Compute the encoded value
                    abs_val=n_commons
                    rel_val=(n_commons-last_n_common)

                    if (abs_val<=3 and rel_val<=-2):
                        c_label = (C_Label(abs_val, last_common, unary_chain, C_ABSOLUTE_ENCODING, self.separator, self.unary_joiner))
                    else:
                        c_label = (C_Label(rel_val, last_common, unary_chain, C_RELATIVE_ENCODING, self.separator, self.unary_joiner))
                    
                    lc_tree.add_row(word, postag, feats, c_label)

                    last_n_common=n_commons
                    break
                
                # Store Last Common and increase n_commons 
                # Note: When increasing n_commons use the number from split the collapsed chains
                n_commons += len(a.split(self.unary_joiner))
                last_common = a
        
        # n = max number of features of the tree
        lc_tree.n = max([len(f) for f in lc_tree.additional_feats])
        return lc_tree

    def decode(self, linearized_tree):
        # Check valid labels 
        if not linearized_tree:
            print("[*] Error while decoding: Null tree.")
            return
        
        # Create constituent tree
        tree = C_Tree(C_ROOT_LABEL, [])
        current_level = tree

        old_n_commons=0
        old_last_common=''
        old_level=None
        is_first = True
        last_label = None

        for word, postag, feats, label in linearized_tree.iterrows():
            
            # Convert the labels to absolute scale
            if last_label!=None and label.encoding_type==C_RELATIVE_ENCODING:
                label.to_absolute(last_label)
            
            # First label must have a positive n_commons value
            if is_first and label.n_commons < 0:
                label.n_commons = 0

            # Descend through the tree until reach the level indicated by last_common
            current_level = tree
            for level_index in range(label.n_commons):
                if (len(current_level.children)==0) or (level_index >= old_n_commons):
                    current_level.add_child(C_Tree(C_NONE_LABEL, []))
                
                current_level = current_level.r_child()

            # Split the Last Common field of the Label in case it has a Unary Chain Collapsed
            label.last_common = label.last_common.split(self.unary_joiner)

            if len(label.last_common)==1:
                # If current level has no label yet, put the label
                # If current level has label but different than this one, set it as a conflict
                if (current_level.label==C_NONE_LABEL):
                    current_level.label = label.last_common[0].rstrip()
                else:
                    current_level.label = current_level.label + C_CONFLICT_SEPARATOR + label.last_common[0]
            else:
                current_level = tree
                
                # Descend to the beginning of the Unary Chain and fill it
                descend_levels = label.n_commons - (len(label.last_common)) + 1
                for level_index in range(descend_levels):
                    current_level = current_level.r_child()
                
                for i in range(len(label.last_common)-1):
                    if (current_level.label==C_NONE_LABEL):
                        current_level.label=label.last_common[i]
                    else:
                        current_level.label=current_level.label+C_CONFLICT_SEPARATOR+label.last_common[i]
                    current_level = current_level.r_child()

                # If we reach a POS tag, set it as child of the current chain
                if current_level.is_preterminal():
                    temp_current_level = current_level
                    current_level.label = label.last_common[i+1]
                    current_level.children = [temp_current_level]
                else:
                    current_level.label=label.last_common[i+1]
            
            # Fill POS tag in this node or previous one
            if (label.n_commons >= old_n_commons):
                current_level.fill_pos_nodes(postag, word, label.unary_chain, self.unary_joiner)
            else:
                old_level.fill_pos_nodes(postag, word, label.unary_chain, self.unary_joiner)

            old_n_commons=label.n_commons
            old_level=current_level
            last_label=label

        tree=tree.children[0]
        return tree