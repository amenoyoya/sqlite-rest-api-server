# encoding: utf-8
'''
Reverse Polish Notation (RPN) Processor Library

Copyright (C) 2019 yoya(@amenoyoya). All rights reserved.
GitHub: https://github.com/amenoyoya/pyrpn
License: MIT License
'''

# 関数の引数の数を取得するためにsignatureをimport
from inspect import signature
import re

class Value:
    ''' 値クラス '''
    VALUE = 0 # 値
    CHUNK = 1 # 遅延評価式

    def __init__(self, value, _type=VALUE):
        self.value = value
        self.type = _type


class Variable(Value):
    ''' 変数クラス '''
    class NameError(Exception):
        def __str__(self):
            return 'Invalid character specified for variable name.'
    
    # 変数名には[アルファベット, 数字, _, .]のみ使用可能
    pattern = re.compile(r'^[a-zA-Z0-9_\.]+$')
    
    def __init__(self, variable_name):
        if Variable.pattern.match(variable_name) is None:
            raise Variable.NameError()
        super(Variable, self).__init__(variable_name, Value.CHUNK)
    

class RPN:
    ''' 逆ポーランド記法計算クラス '''

    # 四則演算子
    ## 演算子を変えたい場合は、このクラスを継承する
    operators = {
        '+': lambda x, y: Value(x.value + y.value),
        '-': lambda x, y: Value(x.value - y.value),
        '*': lambda x, y: Value(x.value * y.value),
        '/': lambda x, y: Value(x.value / y.value),
    }
    
    @staticmethod
    def processor(callback):
        ''' 逆ポーランド記法処理系定義デコレータ
        @RPN.processor
        def eval_rpn(element):
            return element # スタック対象を返す
        '''
        def wrapper(exp, *args, **kwargs):
            ''' 逆ポーランド記法を計算する関数
            params:
                exp(list): 逆ポーランド記法プログラムの配列
                    el: [Value(1), Value(2), (lambda x, y: x.value + y.value)] => 1 + 2
            '''
            
            # stackから引数をとって関数をcallする関数
            def call(func, stack):
                argc = len(signature(func).parameters) # 関数の引数の数を取得
                res = func(*stack[-argc:]) # stackの後ろから引数を取得し、関数実行
                del stack[-argc:] # 引数分をstackから削除
                if res is not None:
                    stack += [res] # 関数の戻り値をstack
            
            stack = []
            for e in exp:
                if callable(e):
                    # 関数なら関数実行
                    call(e, stack)
                elif isinstance(e, Value):
                    # Valueはそのままstack
                    stack += [e]
                else:
                    # stack前処理の結果をstack
                    res = callback(e, *args, **kwargs)
                    if res is not None:
                        if callable(res):
                            # stack前処理が関数を返したら関数実行
                            call(res, stack)
                        else:
                            stack += [res]
            return stack
        return wrapper

    @staticmethod
    def explain(exp):
        ''' ビルド済み逆ポーランド記法をprint可能な形式に変換
        params:
            exp(list): ビルド済み逆ポーランド記法プログラムの配列
                el: RPN.build({'+': [1, 2]})
        return:
            exp(list): print可能な逆ポーランド記法配列
        '''
        return [
            e.__name__ if callable(e) else
                e.value if isinstance(e, Value) else e for e in exp
        ]

    @classmethod
    def eval(self, exp, variables={}):
        ''' 定義した演算子に基づいて逆ポーランド記法の計算式を計算
        params:
            exp(list): 逆ポーランド記法プログラムの配列
                el: [1, 2, '+'] => 1 + 2
            variables(dict): 組み込み変数
                el: {'TEN': 10, 'ZERO': 0}
        return:
            result(list): Value配列
        '''
        @RPN.processor
        def calc(e):
            # 演算子
            f = self.operators.get(e)
            if f is not None:
                return f
            # 組み込み変数
            v = variables.get(e)
            if v is not None:
                return v if isinstance(v, Value) else Value(v)
            # 値
            return e if isinstance(e, Value) else Value(e)
        
        return calc(exp)

    @classmethod
    def build(self, s_exp):
        ''' 演算子に基づいて ポーランド記法 => 逆ポーランド記法 変換
        params:
            s_exp(dict): ポーランド記法 {
                '演算子': [引数, ...],
                '演算子': {'変数': 値}
            }
        return:
            result(list): Value配列
        '''
        rpn = []
        def convert(exp, rpn):
            for key, value in exp.items():
                op = self.operators.get(key)
                
                # 演算子でない = 変数
                if op is None:
                    rpn += [Variable(key)]
                
                if type(value) is dict:
                    convert(value, rpn)
                elif type(value) is list:
                    for v in value:
                        if type(v) is dict:
                            convert(v, rpn)
                        else:
                            rpn += [v if isinstance(v, Value) else Value(v)]
                else:
                    rpn += [value if isinstance(value, Value) else Value(value)]
                
                # 演算子は後ろに追加
                if op is not None:
                    op.__name__ = key
                    rpn += [op]
            return rpn
        return convert(s_exp, rpn)
