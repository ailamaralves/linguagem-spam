import io
import contextlib
from spam import var, env, Symbol, parse, eval, global_env

run = lambda src, env=None: eval(parse(src), env)
x, y, a, b, c, f, g, h, op = map(Symbol, 'x y a b c f g h op'.split())


def parse_expr(src):
    mod = parse(src + ";")
    assert len(mod) == 2
    cmd = mod[1]
    assert cmd[0] == "simplecmd"
    return cmd[1]

def parse_cmd(src):
    mod = parse(src)
    assert len(mod) == 2
    return mod[1]

def check_print(src):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        run(src)
    return stdout.getvalue()


class TestSpamGrammar:
    def test_numbers(self):
        assert parse_expr('42') == 42
        assert parse_expr('3.14') == 3.14
        assert parse_expr('-3.14') == -3.14

    def test_atomic(self):
        assert parse_expr('#t') is True
        assert parse_expr('#f') is False
        assert parse_expr('x') == x

    def test_strings(self):
        assert parse_expr('"foobar"') == "foobar"
        assert parse_expr('"foo bar"') == "foo bar"
        assert parse_expr(r'"foo\nbar"') == "foo\nbar"
        assert parse_expr(r'"foo\tbar"') == "foo\tbar"
        assert parse_expr(r'"foo\tbar"') == "foo\tbar"
        assert parse_expr(r'"foo\"bar\""') == "foo\"bar\""

    def test_list(self):
        assert parse_expr('[1, 2]') == [1, 2]
        assert parse_expr('[1, 2, 3, 4]') == [1, 2, 3, 4]
        assert parse_expr('["Sara", "Pedro", "Ailamar", "Matheus"]') == ["Sara", "Pedro", "Ailamar", "Matheus"]
        assert parse_expr('[]') == []

    def test_nested_list(self):
        assert parse_expr('[1, [2, [3, 4]]]') == [1, [2, [3, 4]]]
        assert parse_expr('[[1, 2, 3]]') == [[1, 2, 3]]

    def test_atrib(self):
        assert parse_cmd('x = 2;') == ['atrib', 'x', 2]
        assert parse_cmd('x = 2 + 1;') == ['atrib', 'x', ["operation", 2, 1]]
        assert parse_cmd('x = 2 + y;') == ['atrib', 'x', ["operation", 2, y]]

    def test_if(self):
        assert parse_cmd('x == 2, talkei? 4 x = 42; imp') == ['ifcmd', ['comp', x, 2], ['block', ['atrib', 'x', 42]]]
        assert parse_cmd('y == 3, talkei? 4 x = 53; imp ele não! 4 x > y; imp') == ['ifcmd', ['comp', y, 3], ['block', ['atrib', 'x', 53]]]

    def test_else(self):
        assert parse_cmd('ele não! 4 x = 2; imp') == ['elsecmd', ['block', ['atrib', 'x', 2]]]

    def test_return(self):
        assert parse_cmd('#t lula livre!') == ['returncmd', True]
        assert parse_cmd('2 lula livre!') == ['returncmd', 2]
        assert parse_cmd('x lula livre!') == ['returncmd', x]

    def test_print(self):
        assert parse_cmd('(x == 2) grande dia!') == ['printcmd', ['comp', x, 2]]

    def test_def(self):
        assert parse_cmd('repare bem x (1): 4 x = 42; imp') == ['defcmd', x, 1, ['block', ['atrib','x', 42]]]

    def test_for(self):
        assert parse_cmd('companheiro , teste em x < 2 é golpe!') == ['forcmd', 'teste', ['comp', x, 2]]
        assert parse_cmd('companheiro , lista em y < x é golpe!') == ['forcmd', 'lista', ['comp', y, x]]

    def test_while(self):
        assert parse_cmd('(x > 2) gloria a deux!') == ['whilecmd', ['comp', x, 2]]
        assert parse_cmd('(y == 0) gloria a deux!') == ['whilecmd', ['comp', y, 0]]

class TestEnvCreation:
    def test_env_creation(self):
        assert env() == global_env
        assert set(env({var.x: 42})).issuperset(set(global_env))
        assert env({var.x: 42})[var.x] == 42
        assert env(x=42)[var.x] == 42


class TestRuntime:
    def test_eval_simple(self):
        assert run('42;') == ['module', ['simplecmd', 42]]

    def test_eval_if_simple(self):
        assert run('x == 2, talkei? 4 (x == 3) grande dia! imp') == ['module', ['ifcmd', ['comp', x, 2], ['block', ['printcmd', ['comp', x, 3]]]]]
        assert run('x == 2, talkei? 4 x = 52; imp') == ['module', ['ifcmd', ['comp', x, 2], ['block', ['atrib', 'x', 52]]]]

    def test_eval_else_simple(self):
        assert run('ele não! 4 x + 4; imp') == ['module', ['elsecmd', ['block', ['simplecmd', ['operation', x, 4]]]]]
        assert run('ele não! 4 (x) grande dia! imp') == ['module', ['elsecmd',['block', ['printcmd', x]]]]

    def test_eval_for(self):
        assert run('companheiro, x em y é golpe!') == ['module', ['forcmd', 'x', y]] 
        assert run('companheiro, nota em x é golpe!') == ['module', ['forcmd', 'nota', x]]

    def _test_eval_if_nested(self):
        assert run('(if (odd? 1) (+ 40 2) (+ 1 1))') == 42
        assert run('(if (even? 1) (+ 40 2) (+ 1 1))') == 2

    def _test_eval_define_simple(self):
        e = env()
        assert run("(define x 42)", e) is None
        assert e[Symbol('x')] == 42

    def _test_eval_define_nested(self):
        e = env()
        assert run("(define x (+ 40 2))", e) is None
        assert e[Symbol('x')] == 42
    
    def _test_call_environment_functions(self):
        assert run('(even? 42)') is True
        assert run('(odd? 42)') is False

    def _test_call_function_with_nested_arguments(self):
        assert run('(even? (+ 1 1))') is True
        assert run('(+ (* 2 3) 4)') == 10