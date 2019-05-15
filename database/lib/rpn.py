from inspect import signature

def RPN(exp, op):
    ''' 逆ポーランド記法を計算する関数
    params:
        exp list: 逆ポーランド記法プログラムの配列（el. [1, 2, '+'] => 1 + 2）
        op dict: 演算子,変数の定義（el. {'+': (lambda x, y: x + y), 'ten': 10}）
    '''
    stack = []
    for e in exp:
        f = None if isinstance(e, list) else op.get(e)
        if f is None:
            # 演算子でも変数でもない場合はstack
            stack.append(e)
        elif callable(f):
            # 演算子なら演算実行
            argc = len(signature(f).parameters) # 関数の引数の数を取得
            res = f(*stack[-argc:]) # stackの後ろから引数を取得し、関数実行
            stack = stack[:-argc] # 引数分をstackから削除
        if res is not None:
            stack.append(res) # 関数の戻り値をstack
        else:
            # 変数の値をstack
            stack.append(f)
    return stack
