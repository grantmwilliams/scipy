from __future__ import division, print_function, absolute_import

from math import sqrt, exp, sin, cos

from numpy.testing import (assert_warns, assert_, 
                           assert_allclose,
                           assert_equal)
from numpy import finfo, exp as np_exp, sin as np_sin, asarray

from scipy.optimize import zeros as cc
from scipy.optimize import zeros

# Import testing parameters
from scipy.optimize._tstutils import functions, fstrings


class TestBasic(object):
    def run_check(self, method, name):
        a = .5
        b = sqrt(3)
        xtol = 4*finfo(float).eps
        rtol = 4*finfo(float).eps
        for function, fname in zip(functions, fstrings):
            zero, r = method(function, a, b, xtol=xtol, rtol=rtol,
                             full_output=True)
            assert_(r.converged)
            assert_allclose(zero, 1.0, atol=xtol, rtol=rtol,
                err_msg='method %s, function %s' % (name, fname))

    def test_bisect(self):
        self.run_check(cc.bisect, 'bisect')

    def test_ridder(self):
        self.run_check(cc.ridder, 'ridder')

    def test_brentq(self):
        self.run_check(cc.brentq, 'brentq')

    def test_brenth(self):
        self.run_check(cc.brenth, 'brenth')

    def test_newton(self):
        f1 = lambda x: x**2 - 2*x - 1
        f1_1 = lambda x: 2*x - 2
        f1_2 = lambda x: 2.0 + 0*x

        f2 = lambda x: exp(x) - cos(x)
        f2_1 = lambda x: exp(x) + sin(x)
        f2_2 = lambda x: exp(x) + cos(x)

        for f, f_1, f_2 in [(f1, f1_1, f1_2), (f2, f2_1, f2_2)]:
            x = zeros.newton(f, 3, tol=1e-6)
            assert_allclose(f(x), 0, atol=1e-6)
            x = zeros.newton(f, 3, fprime=f_1, tol=1e-6)
            assert_allclose(f(x), 0, atol=1e-6)
            x = zeros.newton(f, 3, fprime=f_1, fprime2=f_2, tol=1e-6)
            assert_allclose(f(x), 0, atol=1e-6)

    def test_newton_array(self):
        """test newton with array"""

        def f_solarcell(i, v, il, io, rs, rsh, vt):
            vd = v + i * rs
            return il - io * (np_exp(vd / vt) - 1.0) - vd / rsh - i

        def f_prime(i, v, il, io, rs, rsh, vt):
            return -io * np_exp((v + i * rs) / vt) * rs / vt - rs / rsh - 1

        il = (np_sin(range(10)) + 1.0) * 7.0
        v = asarray([
            5.32725221e+00,   5.48673747e+00,   5.49539973e+00,
            5.36387202e+00,   4.80237316e+00,   1.43764452e+00,
            5.23063958e+00,   5.46094772e+00,   5.50512718e+00,
            5.42046290e+00
        ])
        args = (v, il, 1e-09, 0.004, 10, 0.27456)
        x0 = 7.0
        x = zeros.newton(f_solarcell, x0, f_prime, args)
        y = (6.17264965e+00,   1.17702805e+01,   1.22219954e+01,
             7.11017681e+00,   1.18151293e+00,   1.43707955e-01,
             4.31928228e+00,   1.05419107e+01,   1.27552490e+01,
             8.91225749e+00)
        assert_allclose(x, y)
        return x

    def test_deriv_zero_warning(self):
        func = lambda x: x**2
        dfunc = lambda x: 2*x
        assert_warns(RuntimeWarning, cc.newton, func, 0.0, dfunc)


def test_gh_5555():
    root = 0.1

    def f(x):
        return x - root

    methods = [cc.bisect, cc.ridder]
    xtol = 4*finfo(float).eps
    rtol = 4*finfo(float).eps
    for method in methods:
        res = method(f, -1e8, 1e7, xtol=xtol, rtol=rtol)
        assert_allclose(root, res, atol=xtol, rtol=rtol,
                        err_msg='method %s' % method.__name__)


def test_gh_5557():
    # Show that without the changes in 5557 brentq and brenth might
    # only achieve a tolerance of 2*(xtol + rtol*|res|).

    # f linearly interpolates (0, -0.1), (0.5, -0.1), and (1,
    # 0.4). The important parts are that |f(0)| < |f(1)| (so that
    # brent takes 0 as the initial guess), |f(0)| < atol (so that
    # brent accepts 0 as the root), and that the exact root of f lies
    # more than atol away from 0 (so that brent doesn't achieve the
    # desired tolerance).
    def f(x):
        if x < 0.5:
            return -0.1
        else:
            return x - 0.6

    atol = 0.51
    rtol = 4*finfo(float).eps
    methods = [cc.brentq, cc.brenth]
    for method in methods:
        res = method(f, 0, 1, xtol=atol, rtol=rtol)
        assert_allclose(0.6, res, atol=atol, rtol=rtol)


class TestRootResults:
    def test_repr(self):
        r = zeros.RootResults(root=1.0,
                              iterations=44,
                              function_calls=46,
                              flag=0)
        expected_repr = ("      converged: True\n           flag: 'converged'"
                         "\n function_calls: 46\n     iterations: 44\n"
                         "           root: 1.0")
        assert_equal(repr(r), expected_repr)

