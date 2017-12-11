// by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain
#pragma once

// column major
template<class T, int D>
struct array_nd {
	template<class... Args>
	array_nd( Args... is ) {
		size_t s = _size( is... );
		_data = new T[s];
	}

	template<class... Args>
	T& operator()( Args... is ) {
		return _data[_index( is... )];
	}

	template<class... Args>
	T const& operator()( Args... is ) const {
		return _data[_index( is... )];
	}

	size_t shape( int i ) const {
		return _shape[i];
	}

	private:
		template<class... Args>
		size_t _size( size_t i, Args... is ) {
			_shape[D - 1 - sizeof...(Args)] = i;
			return i * _size( is... );
		}

		size_t _size() {
			return 1;
		}

		template<class... Args>
		size_t _index( size_t i, Args... is ) const {
			return i + _shape[D - 1 - sizeof...(Args)] * _index( is... );
		}

		size_t _index() const {
			return 0;
		}

		T* _data;
		size_t _shape[D];
};
