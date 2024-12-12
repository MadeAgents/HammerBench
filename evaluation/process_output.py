import re, json
def convert_label_back(label_args):
    res = {}
    for k,v in label_args.items():
        if v!='' and v!='\\':res[k]=v
    return res
def parse_response(input_text, sup1, sup2):
    res = []
    # sup1, sup2 = '<tool_call>', '</tool_call>'
    # sup1, sup2 = '```json', '```'
    try:
        label = json.loads(input_text.strip())
        return [(label['name'], convert_label_back(label['parameters']))]
    except:pass
    extract = re.findall(f'{sup1}([\S\s]*?){sup2}', input_text)
    if extract==[]:
        extract = [input_text[input_text.find('{"name"'):].strip()]
    for x in extract:
        if x=='':continue
        try:label = json.loads(x.strip())
        except:# 输出 parallel情况，取最后一个
            label = json.loads([x0.strip() for x0 in x.strip().split('\n')][-1])
            # pass

        try:res.append((label['name'] ,convert_label_back(label['arguments']) ))
        except:
            try:res.append((label['name'] ,convert_label_back(label['parameters']) ))
            except:res.append((label['name'] ,{}))   # 存在只有 name 键值的，把参数赋为 {}
    return res

def parse_mistral(input_text):
    extract = '['+re.findall('\[TOOL_CALLS\]\[([\S\s]*?)\]', input_text)[0]+']'
    label = json.loads(extract.strip())
    
    return [(x['name'], convert_label_back(x['arguments'])) for x in label]

def parse_xlam(input_text):
    extract = '['+re.findall('"tool_calls":.*\[([\S\s]*?)\]', input_text)[0]+']'
    label = json.loads(extract.strip())
    
    return [(x['name'], convert_label_back(x['arguments'])) for x in label]
def parse_hammer(input_text):
    extract = re.findall('```([\S\s]*?)```', input_text)[0]
    label = json.loads(extract.strip())
    return [(x['name'], convert_label_back(x['arguments'])) for x in label]


# 括号形式的后处理
import ast
def resolve_ast_call(elem):
    # Handle nested attributes for deeply nested module paths
    func_parts = []
    func_part = elem.func
    while isinstance(func_part, ast.Attribute):
        func_parts.append(func_part.attr)
        func_part = func_part.value
    if isinstance(func_part, ast.Name):
        func_parts.append(func_part.id)
    func_name = ".".join(reversed(func_parts))
    args_dict = {}
    for arg in elem.keywords:
        output = resolve_ast_by_type(arg.value)
        args_dict[arg.arg] = output
    return {func_name: args_dict}
def resolve_ast_by_type(value):
    if isinstance(value, ast.Constant):
        if value.value is Ellipsis:
            output = "..."
        else:
            output = value.value
    elif isinstance(value, ast.UnaryOp):
        output = -value.operand.value
    elif isinstance(value, ast.List):
        output = [resolve_ast_by_type(v) for v in value.elts]
    elif isinstance(value, ast.Dict):
        output = {
            resolve_ast_by_type(k): resolve_ast_by_type(v)
            for k, v in zip(value.keys, value.values)
        }
    elif isinstance(
        value, ast.NameConstant
    ):  # Added this condition to handle boolean values
        output = value.value
    elif isinstance(
        value, ast.BinOp
    ):  # Added this condition to handle function calls as arguments
        output = eval(ast.unparse(value))
    elif isinstance(value, ast.Name):
        output = value.id
    elif isinstance(value, ast.Call):
        if len(value.keywords) == 0:
            output = ast.unparse(value)
        else:
            output = resolve_ast_call(value)
    elif isinstance(value, ast.Tuple):
        output = tuple(resolve_ast_by_type(v) for v in value.elts)
    elif isinstance(value, ast.Lambda):
        output = eval(ast.unparse(value.body[0].value))
    elif isinstance(value, ast.Ellipsis):
        output = "..."
    elif isinstance(value, ast.Subscript):
        try:
            output = ast.unparse(value.body[0].value)
        except:
            output = ast.unparse(value.value) + "[" + ast.unparse(value.slice) + "]"
    else:
        raise Exception(f"Unsupported AST type: {type(value)}")
    return output
def parse_toolace(input_text):
    parsed = ast.parse(input_text.strip("[]'"), mode='eval')
    extracted = []
    if isinstance(parsed.body, ast.Call):
        extracted.append(resolve_ast_call(parsed.body))
    else:
        for elem in parsed.body.elts:
            assert isinstance(elem, ast.Call)
            extracted.append(resolve_ast_call(elem))
    return [tuple(x.items())[0] for x in extracted]