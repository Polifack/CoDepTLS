from codelin.encs.abstract_encoding import ADEncoding
from codelin.models.deps_label import D_Label
from codelin.models.deps_tree import D_Tree
from codelin.utils.constants import D_NONE_LABEL, D_2P_GREED, D_2P_PROP
from codelin.models.linearized_tree import LinearizedTree

class D_Brk7BitsEncoding(ADEncoding):
    
    def __init__(self, separator:str = "_", planar_alg:str = D_2P_GREED):
        super().__init__(separator)
        self.planar_alg = planar_alg

    def __str__(self):
        return "Dependency Bracketing 7-Bits Encoding"

    def encode(self, dep_tree):
        def encoding_step(plane, labels_brk, brk_chars):
            '''
            encoding step for the brackets. 
            brk_chars = [<0 \0 >0 /0] for the first plane and
                        [<1 \1 >1 /1] for the second plane

            we will also add a * to the leftmost and rightmost nodes
            '''
            for node in plane:
                if node.id == 0:
                    continue
                
                if node.is_left_arc():
                    labels_brk[node.id] += brk_chars[0]
                    if plane.is_leftmost(node):
                        labels_brk[node.id] += '*'
                    
                    labels_brk[node.head] += brk_chars[1] if brk_chars[1] not in labels_brk[node.head] else ""
                
                else:
                    labels_brk[node.id] += brk_chars[2]
                    if plane.is_rightmost(node):
                        labels_brk[node.id] += '*'
                    
                    labels_brk[node.head] += brk_chars[3] if brk_chars[3] not in labels_brk[node.head] else ""

            return labels_brk
        
        labels_brk = [""] * (len(dep_tree) + 1)
        encoded_labels = []

        if self.planar_alg == D_2P_GREED:
            p1_nodes, p2_nodes = D_Tree.two_planar_greedy(dep_tree)
        elif self.planar_alg == D_2P_PROP:
            p1_nodes, p2_nodes = D_Tree.two_planar_propagate(dep_tree)

        labels_brk = encoding_step(p1_nodes, labels_brk, ['<0', '\\0', '>0', '/0'])
        labels_brk = encoding_step(p2_nodes, labels_brk, ['<1', '\\1', '>1', '/1'])
        
        # generate labels
        for node in dep_tree:
            li = node.relation
            xi = labels_brk[node.id]

            current = D_Label(xi, li, self.separator)
            encoded_labels.append(current)

        return LinearizedTree(dep_tree.get_words(), dep_tree.get_postags(), dep_tree.get_feats(), encoded_labels, len(encoded_labels))

    def _merge_brackets(self, brks):
        for i in range(len(brks)):
            # merge planar indicator
            if brks[i] in ['1', '0']:
                brks[i-1] = brks[i-1]+brks[i]
                brks[i] = ""
            
            # merge rmost/lmost indicator
            if brks[i] == "*":
                brks[i-2] = brks[i-2] + "*"
                brks[i] = ""
        
        brks = [brk for brk in brks if brk != ""]
        return brks

    def _decoding_step(self, lin_tree, decoded_tree, planar_idx, direction):
        stack = []

        current_node = 0 if direction == 'l2r' else len(lin_tree)-1
        s_append_brk = "/" + planar_idx if direction == 'l2r' else "\\" + planar_idx
        s_peek_brk   = ">" + planar_idx if direction == 'l2r' else "<" + planar_idx

        for word, postag, features, label in lin_tree.iterrows(dir = direction):
            brks = list(label.xi) if label.xi != D_NONE_LABEL else []
            brks = self._merge_brackets(brks)
            
            if direction == 'r2l':
                brks.sort(key = lambda x: (x == ("\\"+planar_idx), x))

            # set parameters to the node
            decoded_tree.update_word(current_node, word)
            decoded_tree.update_upos(current_node, postag)
            decoded_tree.update_relation(current_node, label.li)

            # fill the relation using brks
            for char in brks:
                if s_append_brk in char:
                    stack.append(current_node)
                
                if s_peek_brk in char:
                    head_id = stack[-1] if len(stack) > 0 else 0
                    decoded_tree.update_head(current_node, head_id)
                    if "*" in char:
                        stack.pop()
            
            current_node += 1 if direction == 'l2r' else -1
        return decoded_tree

    def _decode_l2r(self, lin_tree, decoded_tree):    
        stack = []
        current_node = 0
        for word, postag, features, label in lin_tree.iterrows(dir='l2r'):
            brks = list(label.xi) if label.xi != D_NONE_LABEL else []
            brks = self._merge_brackets(brks)
                       
            # set parameters to the node
            decoded_tree.update_word(current_node, word)
            decoded_tree.update_upos(current_node, postag)
            decoded_tree.update_relation(current_node, label.li)

            # fill the relation using brks
            for char in brks:                
                if "/0" in char:
                    stack.append(current_node)
                
                if ">0" in char:
                    head_id = stack[-1] if len(stack) > 0 else 0
                    decoded_tree.update_head(current_node, head_id)
                    if "*" in char:
                        stack.pop()
            
            current_node += 1
        return decoded_tree
    
    def _decode_r2l(self, lin_tree, decoded_tree):
        stack = []
        current_node = len(lin_tree)-1
        for word, postag, features, label in lin_tree.iterrows(dir='r2l'):
            brks = list(label.xi) if label.xi != D_NONE_LABEL else []
            brks = self._merge_brackets(brks)
            
            # sort brackets with < first and \ last
            brks.sort(key = lambda x: (x == "\\", x))
            
            # set parameters to the node
            decoded_tree.update_word(current_node, word)
            decoded_tree.update_upos(current_node, postag)
            decoded_tree.update_relation(current_node, label.li)
            #  fill the relation using brks
            for char in brks:
                if "\\0" in char:
                    stack.append(current_node)  
                if "<0" in char:
                    head_id = stack[-1] if len(stack) > 0 else 0
                    decoded_tree.update_head(current_node, head_id)
                    if "*" in char:
                        stack.pop()
            
            current_node-=1
        return decoded_tree

    def decode(self, lin_tree):
        # Create an empty tree with n labels
        decoded_tree = D_Tree.empty_tree(len(lin_tree))
        
        # parse left to right arcs
        
        decoded_tree = self._decoding_step(lin_tree, decoded_tree, '0', 'l2r')
        decoded_tree = self._decoding_step(lin_tree, decoded_tree, '0', 'r2l')
        
        decoded_tree = self._decoding_step(lin_tree, decoded_tree, '1', 'l2r')
        decoded_tree = self._decoding_step(lin_tree, decoded_tree, '1', 'r2l')
        
        # decoded_tree = self._decode_l2r(lin_tree, decoded_tree)
        # decoded_tree = self._decode_r2l(lin_tree, decoded_tree)

        # decoded_tree.remove_dummy()
        return decoded_tree