# Copyright (c) 2012 Alain Fischer (alain [dot] fischer [at] bluewin [dot] ch)
# Licensed under the terms of the MIT License
# see: http://www.opensource.org/licenses/mit-license.php

# implementation based on first OMeta/JS:
# http://tinlizzie.org/ometa/ometa-js-old/

__author__ = 'alain'

class ReadStream():
    def __init__(self, anArrayOrString):
        self.src = anArrayOrString
        self.pos = 0

    def atEnd(self):
        return self.pos >= len(self.src)

    def next(self):
        result = self.src[self.pos]
        self.pos += 1
        return result

def makeOMInputStream(hd, tl, stream):
    r = OMInputStreamEnd(stream) if stream is not None and stream.atEnd() else OMInputStream(hd, tl, stream)
    r.memo = {}
    return r

class OMInputStream():
    def __init__(self, hd, tl, stream):
        self.hd = hd
        self.tl = tl
        self.stream = stream

    def head(self):
        if self.hd is None:
            self.hd = self.stream.next()
        return self.hd

    def tail(self):
        if self.tl is None:
            self.tl = makeOMInputStream(None, None, self.stream)
        return self.tl

class OMInputStreamEnd():
    def __init__(self, stream):
        self.stream = stream

    def head(self):
        raise Fail()

class Fail(Exception):
    pass

class LeftRecursion():
    def __init__(self):
        self.isLeftRecursion = True
        self.detected = False

class OMeta():
    def matchAllWith(self, listObj, rule):
        return self.genericMatch(makeOMInputStream(None, None, ReadStream(listObj)), rule)

    def genericMatch(self, input, rule):
        self.input = input
        return self._apply(rule)

    def _apply(self, rule):
        memoRec = self.input.memo.get(rule)
        if memoRec is None:
            oldInput = self.input
            lr = LeftRecursion()
            self.input.memo[rule] = lr
            ans = getattr(self, rule)()
            oldInput.memo[rule] = memoRec = {'ans': ans, 'nextInput': self.input}
            if lr.detected:
                sentinel = self.input
                while True:
                    try:
                        self.input = oldInput
                        ans = getattr(self, rule)()
                        if self.input == sentinel:
                            raise Fail()
                        oldInput.memo[rule] = memoRec = {'ans': ans, 'nextInput': self.input}
                    except Fail:
                        break
        elif isinstance(memoRec, LeftRecursion):
            memoRec.detected = True
            raise Fail()
        self.input = memoRec['nextInput']
        return memoRec['ans']

    def _applyWithArgs(self, rule, *args):
        for arg in args:
            self.input = makeOMInputStream(arg, self.input, None)
        return getattr(self, rule)()

    def _or(self, *args):
        oldInput = self.input
        for arg in args:
            try:
                self.input = oldInput
                return arg()
            except Fail:
                pass
        raise Fail()

    def _pred(self, c):
        if c:
            return True
        raise Fail()

    def anything(self):
        r = self.input.head()
        self.input = self.input.tail()
        return r

    def exactly(self):
        wanted = self._apply("anything")
        if self._apply("anything") == wanted:
            return wanted
        raise Fail()

class OMetaExample(OMeta):
    def digit(self):
        c = self._apply('anything')
        self._pred(c.isdigit())
        return int(c)

    def number(self):
        def _or1():
            n = self._apply('number')
            d = self._apply('digit')
            return n * 10 + d

        def _or2():
            return self._apply('digit')

        return self._or(lambda: _or1(), lambda: _or2())

    def priExpr(self):
        def _or1():
            return self._apply('number')

        def _or2():
            self._applyWithArgs('exactly', '(')
            e = self._apply('expr')
            self._applyWithArgs('exactly', ')')
            return e

        return self._or(lambda: _or1(), lambda: _or2())

    def mulExpr(self):
        def _or1():
            x = self._apply('mulExpr')
            self._applyWithArgs('exactly', '*')
            y = self._apply('priExpr')
            return x * y

        def _or2():
            x = self._apply('mulExpr')
            self._applyWithArgs('exactly', '/')
            y = self._apply('priExpr')
            return x / y

        def _or3():
            return self._apply('priExpr')

        return self._or(lambda: _or1(), lambda: _or2(), lambda: _or3())

    def addExpr(self):
        def _or1():
            x = self._apply('addExpr')
            self._applyWithArgs('exactly', '+')
            y = self._apply('mulExpr')
            return x + y

        def _or2():
            x = self._apply('addExpr')
            self._applyWithArgs('exactly', '-')
            y = self._apply('mulExpr')
            return x - y

        def _or3():
            return self._apply('mulExpr')

        return self._or(lambda: _or1(), lambda: _or2(), lambda: _or3())

    def expr(self):
        return self._apply('addExpr')
