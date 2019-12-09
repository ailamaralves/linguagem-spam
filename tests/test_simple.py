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
        assert parse_cmd('x == 2, talkei? 4 x = 42; imp') == ['ifcmd', [...], ['block', ...]]


class TestEnvCreation:
    def _test_env_creation(self):
        assert env() == global_env
        assert set(env({var.x: 42})).issuperset(set(global_env))
        assert env({var.x: 42})[var.x] == 42
        assert env(x=42)[var.x] == 42


class TestRuntime:
    def _test_eval_simple(self):
        assert run('42') == 42

    def _test_eval_if_simple(self):
        assert check_print('x == 2, talkei? 4 ()"hello") grande dia! imp')
        assert run('(if #f 42 0)') == 0

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