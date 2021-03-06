import re
import json
import txt_tool

path_json = open("/Users/guru/MyResearch/sg/src/dir_path.json", 'r')
paths = json.load(path_json)
path_json.close()

model_name = paths['model_name']
m_path = paths['m_path']
data_path = paths['data_path']
function_words_list = paths['function_words_list']
formula_format = paths['formula_format']

print('model is ', model_name)
print(m_path)
print(data_path)
print(function_words_list)
###############################################################
#   original corpus data
###############################################################
inp_corpus = open(data_path)
all_input_formulas = []
all_target_texts = []
all_output_expections =[]
#base, surf and func is used only masking model
all_base_texts =[]
all_surf_texts =[]
func_list = []
func_index = []

###############################################################
#   input and output token dictionary
###############################################################
dict_formula_tokens = set()
dict_target_tokens = set()
dict_lem = dict()
formula_token_index = dict()
target_token_index = dict()
reverse_target_token_index = dict()

###############################################################
#   initial demention of word vector
###############################################################
NUM_ENCODER_TOKENS = 0
NUM_DECODER_TOKENS = 0
MAX_ENCODER_SEQ_LENGTH = 0
MAX_DECODER_SEQ_LENGTH = 0

for i, line in enumerate(inp_corpus):
    line = line.split('_SPLIT_') # formula/orign sentence / 動詞とか処理したもの
    inp_formula = line[1]
    inp_formula = inp_formula.rstrip().lstrip()
    target_text = line[0]
    target_text = target_text.rstrip().lstrip().lower()

    lst_formula = txt_tool.formula_to_list(inp_formula)
    if(formula_format == 'only_pred'):
        lst_formula = txt_tool.get_predicate_in_formula_list(lst_formula)
    all_input_formulas.append(lst_formula)

    all_output_expections.append(target_text)

    lst_text = txt_tool.text_to_list(target_text)
    all_target_texts.append(lst_text)

    for token in lst_formula:
        if token not in dict_formula_tokens:
            dict_formula_tokens.add(token)


    for token in lst_text:
        if token not in dict_target_tokens:
            dict_target_tokens.add(token)

    ###############################################################
    #   masking model
    ###############################################################

    if(model_name=='masking'):
        from nltk import stem
        stemmer = stem.PorterStemmer()
        lemmatizer = stem.WordNetLemmatizer()

        for word in target_text.split():
            lem = stemmer.stem(word)
            if not(lem in dict_lem.keys()):
                dict_lem[lem] = set()
            if not(word in dict_lem[lem]):
                dict_lem[lem].add(word)

    # -------------------- notice: end of inp_corpus --------------------
###############################################################
# special case : including vocabraries in test data
###############################################################
test_texts = open('test.complex.unique.candc.formulas','r')
for line in test_texts:
    test_text, _ = line.split('_SPLIT_')
    test_text_list = txt_tool.text_to_list(test_text)
    for token in test_text_list:
        if token not in dict_target_tokens:
            dict_target_tokens.add(token)
test_text.close()
###############################################################

dict_formula_tokens = sorted(list(dict_formula_tokens))
dict_target_tokens = sorted(list(dict_target_tokens))


NUM_ENCODER_TOKENS = len(dict_formula_tokens) + 1
NUM_DECODER_TOKENS = len(dict_target_tokens) + 1
MAX_ENCODER_SEQ_LENGTH = max([len(txt) for txt in all_input_formulas])
MAX_DECODER_SEQ_LENGTH = max([len(txt) for txt in all_target_texts])

formula_token_index = dict(
    [(token, i+1) for i, token in enumerate(dict_formula_tokens)])
target_token_index = dict(
    [(token, i+1) for i, token in enumerate(dict_target_tokens)])
reverse_target_token_index = dict(
    (i, token) for token, i in target_token_index.items()) #0:tab,1:\n

###############################################################
#   masking model
###############################################################
if(model_name=='masking'):
    f = open(function_words_list)
    line = f.readline()
    while line:
        func_list.append(line.rstrip())
        line = f.readline()
    f.close()

    func_index.append(target_token_index['EOS'])

    for w in func_list:
        if w in target_token_index:
            func_index.append(target_token_index[w])

###############################################################
#   checking dictionary
###############################################################
print('Number of samples:', len(all_input_formulas))
print("NUM_ENCODER_TOKENS:", NUM_ENCODER_TOKENS)
print("NUM_DECODER_TOKENS:" ,NUM_DECODER_TOKENS)
print("MAX_ENCODER_SEQ_LENGTH: ",MAX_ENCODER_SEQ_LENGTH)
print("MAX_DECODER_SEQ_LENGTH: ",MAX_DECODER_SEQ_LENGTH)

#f = open(m_path+'token_formulas','w')
#f.write(str(dict_formula_tokens))
#f.close()

#f = open(m_path+'token_sentence','w')
#f.write(str(dict_target_tokens))
#f.close()
