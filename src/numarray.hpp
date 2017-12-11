// numarray support for boost::python
// by y.fujii <y-fujii at mimosa-pudica.net>, public domain

/*
	template<class T> class cnumarray
	{
		public:
			...
			int dim() const; // 次元数
			int shape(int n) const; // n 次元目のサイズ
			int stride(int n) const; // n 次元目のストライド
			T* data() const; // 配列データへのポインタ
			T& operator[](int) const;
			T& operator[](int);
	};

	// 1 ~ 4 次元配列の作成
	template<class T> cnumarray<T> make_cnumarray(int);
	template<class T> cnumarray<T> make_cnumarray(int, int);
	template<class T> cnumarray<T> make_cnumarray(int, int, int);
	template<class T> cnumarray<T> make_cnumarray(int, int, int, int);

	// 以下は Python から呼ばれる関数の引数に使用する。
	// 必要に応じて一時オブジェクトを作成したり、書き戻したり。

	// 読み込みのみ必要な場合。書き込んだ場合の結果は不定。
	template<class T> class cnumarray_in: public cnumarray<T> { ... }
	// 書き込みのみ必要な場合。読み込んだ場合の結果は不定。
	template<class T> class cnumarray_out: public cnumarray<T> { ... }
	// 読み書きが必要な場合。
	template<class T> class cnumarray_ref: public cnumarray<T> { ... }
*/


#if !defined(___PYTHON_CNUMARRAY___)
#define ___PYTHON_CNUMARRAY___

#include <Python.h>
#include <numarray/libnumarray.h>
#include <boost/python.hpp>


template<class T> struct numarray_type;
template<> struct numarray_type<void> { static const NumarrayType id = tAny; };
template<> struct numarray_type<double> { static const NumarrayType id = tFloat64; };
template<> struct numarray_type<float> { static const NumarrayType id = tFloat32; };
template<> struct numarray_type<u_int64_t> { static const NumarrayType id = tUInt64; };
template<> struct numarray_type<u_int32_t> { static const NumarrayType id = tUInt32; };
template<> struct numarray_type<u_int16_t> { static const NumarrayType id = tUInt16; };
template<> struct numarray_type<u_int8_t> { static const NumarrayType id = tUInt8; };
template<> struct numarray_type<int64_t> { static const NumarrayType id = tInt64; };
template<> struct numarray_type<int32_t> { static const NumarrayType id = tInt32; };
template<> struct numarray_type<int16_t> { static const NumarrayType id = tInt16; };
template<> struct numarray_type<int8_t> { static const NumarrayType id = tInt8; };
template<> struct numarray_type<bool> { static const NumarrayType id = tBool; };


template<class T> class cnumarray: public boost::python::object
{
	public:
		explicit cnumarray():
			boost::python::object()
		{
		}

		explicit cnumarray(boost::python::detail::borrowed_reference p):
			boost::python::object(p)
		{
		}

		explicit cnumarray(boost::python::detail::new_reference p):
			boost::python::object(p)
		{
		}

		explicit cnumarray(boost::python::detail::new_non_null_reference p):
			boost::python::object(p)
		{
		}

		T* data() const
		{
			PyArrayObject* p = (PyArrayObject*)ptr();
			return (T*)p->data;
		}

		int dim() const
		{
			PyArrayObject* p = (PyArrayObject*)ptr();
			return p->nd;
		}

		int shape(int i) const
		{
			PyArrayObject* p = (PyArrayObject*)ptr();
			return p->dimensions[i];
		}

		int stride(int i) const
		{
			PyArrayObject* p = (PyArrayObject*)ptr();
			return p->strides[i];
		}

		T& operator[](int i) const
		{
			return *(data() + i);
		}

		T& operator[](int i)
		{
			return *(data() + i);
		}
};


template<class T> class cnumarray_ref: public cnumarray<T>
{
	private:
		cnumarray_ref();

	public:
		explicit cnumarray_ref(boost::python::detail::borrowed_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_IoArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
		}

		explicit cnumarray_ref(boost::python::detail::new_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_IoArray(
						boost::python::expect_non_null((PyObject*)p),
						numarray_type<T>::id,
						NUM_C_ARRAY
					)
				)
			)
		{
			boost::python::xdecref((PyObject*)p);
		}

		explicit cnumarray_ref(boost::python::detail::new_non_null_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_IoArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
			boost::python::decref((PyObject*)p);
		}
};


template<class T> class cnumarray_out: public cnumarray<T>
{
	private:
		cnumarray_out();

	public:
		explicit cnumarray_out(boost::python::detail::borrowed_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_OutputArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
		}

		explicit cnumarray_out(boost::python::detail::new_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_OutputArray(
						boost::python::expect_non_null((PyObject*)p),
						numarray_type<T>::id,
						NUM_C_ARRAY
					)
				)
			)
		{
			boost::python::xdecref((PyObject*)p);
		}

		explicit cnumarray_out(boost::python::detail::new_non_null_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_OutputArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
			boost::python::decref((PyObject*)p);
		}
};


template<class T> class cnumarray_in: public cnumarray<T>
{
	private:
		cnumarray_in();

	public:
		explicit cnumarray_in(boost::python::detail::borrowed_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_InputArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
		}

		explicit cnumarray_in(boost::python::detail::new_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_IoInputArray(
						boost::python::expect_non_null((PyObject*)p),
						numarray_type<T>::id,
						NUM_C_ARRAY
					)
				)
			)
		{
			boost::python::xdecref((PyObject*)p);
		}

		explicit cnumarray_in(boost::python::detail::new_non_null_reference p):
			cnumarray<T>(
				boost::python::detail::new_reference(
					NA_IoInputArray((PyObject*)p, numarray_type<T>::id, NUM_C_ARRAY)
				)
			)
		{
			boost::python::decref((PyObject*)p);
		}
};


namespace boost { namespace python { namespace converter
{
	struct numarray_manager_traits
	{
		static const bool is_specialized = true;

		static bool check(PyObject* p)
		{
			return NA_NumArrayCheck(p);
		}

		static python::detail::new_non_null_reference adopt(PyObject* x)
		{
			return python::detail::new_non_null_reference(x);
		}
	};

	template<class T>
	struct object_manager_traits< cnumarray<T> >: numarray_manager_traits
	{
		static bool check(PyObject* p)
		{
			return numarray_manager_traits::check(p)
			    && (((PyArrayObject*)p)->flags & IS_CARRAY == 0);
		}
	};

	template<class T>
	struct object_manager_traits< cnumarray_ref<T> >: numarray_manager_traits
	{
	};

	template<class T>
	struct object_manager_traits< cnumarray_out<T> >: numarray_manager_traits
	{
	};

	template<class T>
	struct object_manager_traits< cnumarray_in<T> >: numarray_manager_traits
	{
	};

} } }


template<class T> inline cnumarray<T> make_cnumarray(int x)
{
	return cnumarray<T>(
		boost::python::detail::new_reference(
			NA_NewArray(NULL, numarray_type<T>::id, 1, x)
		)
	);
}

template<class T> inline cnumarray<T> make_cnumarray(int x, int y)
{
	return cnumarray<T>(
		boost::python::detail::new_reference(
			NA_NewArray(NULL, numarray_type<T>::id, 2, x, y)
		)
	);
}

template<class T> inline cnumarray<T> make_cnumarray(int x, int y, int z)
{
	return cnumarray<T>(
		boost::python::detail::new_reference(
			NA_NewArray(NULL, numarray_type<T>::id, 3, x, y, z)
		)
	);
}

template<class T> inline cnumarray<T> make_cnumarray(int x, int y, int z, int w)
{
	return cnumarray<T>(
		boost::python::detail::new_reference(
			NA_NewArray(NULL, numarray_type<T>::id, 4, x, y, z, w)
		)
	);
}


#endif
