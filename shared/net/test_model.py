from .model import *
import unittest

class ValidatorTestCase(unittest.TestCase):
    def test_any(self):
        a = Any()
        a(1)
        a("Hello!")
        a([])
        a({})
        a(set())

    def test_any_of(self):
        AnyOf(Type(int))
        AnyOf(Type(str))

        AnyOf(int)
        AnyOf(str)
        AnyOf(int,str)
        AnyOf(int,int)

        self.assertIsInstance(AnyOf(int)(1), int)

        with self.assertRaises(TypeError):
            AnyOf()

    def test_type(self):
        self.assertEqual(
            Type(int)(1),
            1
        )

        with self.assertRaises(ValidationException):
            Type(int)("Not int")

    def test_list(self):
        self.assertEqual(
            List(Type(int))([]),
            []
        )

        self.assertEqual(
            List(int)([]),
            []
        )

        self.assertEqual(
            List(Type(int))([1]),
            [1]
        )

        self.assertEqual(
            List(int)([1]),
            [1]
        )

        self.assertEqual(
            List(Type(int))([1, 2, 3]),
            [1, 2, 3]
        )

        self.assertEqual(
            List(Type(str))([]),
            []
        )

        self.assertEqual(
            List(Type(str))(["hello!"]),
            ["hello!"]
        )

        self.assertEqual(
            List(Any())([1, 2, 3]),
            [1, 2, 3]
        )
        
        self.assertEqual(
            List(Any())(["hello", "world"]),
            ["hello", "world"]
        )
        
        with self.assertRaises(ValidationException):
            List(Any())({})
            List(int)({})
            List(str)({})
            List(Any())(set())

    def test_model(self):
        class A(Model):
            def model(self):
                self.a = Type(int)
                self.b = List(AnyOf(Type(int), Type(str)))
        
        A()({
            "a": 1,
            "b": ["hello!", "world!"]
        })
        
        A()({
            "a": 2,
            "b": [1, 2]
        })

        with self.assertRaises(ValidationException):
            A()({
                "a": 1
            })

            A()({
                "a": 1,
                "b": 1
            })

            A()({
                "a": "hello",
                "b": []
            })

    def test_dict(self):
        class A(Model):
            def model(self):
                self.a = Type(int)
                self.b = Type(str)
        
        d = {
            "a": 1,
            "b": "foo"
        }

        a = A()(d)

        self.assertDictEqual(
            a.as_dict(),
            d
        )

    def test_dict_nested(self):
        class A(Model):
            def model(self):
                self.a = Type(int)
                self.b = Type(int)
                self.c = Type(str)
        
        class B(Model):
            def model(self):
                self.a = Type(A)
                self.b = Type(int)
        
        A()({
            "a": 1,
            "b": 2,
            "c": "three"
        })

        d = {
            "a": {
                "a": 1,
                "b": 2,
                "c": "three"
            },
            "b": 4
        }
        b = B()(d)

        self.assertDictEqual(
            b.as_dict(),
            d
        )

    def test_nested_list(self):
        self.assertEqual(
            List(List(int))([[1], [2], [3,4]]),
            [[1], [2], [3, 4]]
        )

        self.assertEqual(
            List(List(List(int)))(
                [
                    [
                        [1],[2]
                    ],
                    [
                        [3], [4]
                    ]
                ]),
            [
                [
                    [1], [2]
                ],
                [
                    [3], [4]
                ]
            ]
        )

        with self.assertRaises(ValidationException):
            List(List(int))([1, 2, 3, 4])
            List(List(str))(["1", "2", "3", "4"])

    def test_list_with_model(self):
        class A(Model):
            def model(self):
                self.value = Type(int)
        
        List(A)([A(value=1), A(value=2)])

    def test_nested_list_with_model(self):
        class A(Model):
            def model(self):
                self.value = Type(int)
        
        List(List(A))(
            [[A(value=1)], [A(value=1)], [A(value=1)]]
        )

    def test_model_incomplete_dict(self):
        class A(Model):
            def model(self):
                self.value = Type(int)
        
        with self.assertRaises(ValidationException):
            A({})

    def test_option(self):
        self.assertEqual(
            Option(Type(int))(None),
            None
        )

        self.assertEqual(
            Option(Type(int))(1),
            1
        )

        with self.assertRaises(ValidationException):
            Option(Type(int))(1.0)
            Option(Type(str))(1.0)