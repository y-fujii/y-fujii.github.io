// Brown noise generator
// by y.fujii <y-fujii at mimosa-pudica.net>, public domain

#include <exception>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <limits>
#include <cmath>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/soundcard.h>

using namespace std;


int initOSS( const char* dev, int fmt, int freq, int nch ) {
	int fd = open( dev, O_WRONLY );
	if( fd < 0 ) throw exception();
	try {
		if( ioctl( fd, SOUND_PCM_SETFMT, &fmt ) < 0 ) throw exception();
		if( ioctl( fd, SOUND_PCM_WRITE_CHANNELS, &nch ) < 0 ) throw exception();
		if( ioctl( fd, SOUND_PCM_WRITE_RATE, &freq ) < 0 ) throw exception();
	}
	catch(...) {
		close( fd );
		throw;
	}

	return fd;
}

double randGauss() {
	double lhs = sqrt( -2.0 * log( (rand() + 1.0) * (1.0 / (RAND_MAX + 1.0)) ) );
	double rhs = sin( rand() * (2.0 * M_PI / (RAND_MAX + 1.0)) );
	return lhs * rhs;
}

template<class T, class U> U clip( const U& x ) {
	const U low = (U)numeric_limits<T>().min();
	const U upp = (U)numeric_limits<T>().max();
	return min( max( x, low ), upp );
}

int main( int argc, char** argv ) {
	string ossDev( "/dev/sound" );
	int freq = 48000;
	double sigm = 32768.0 / 128.0;

	int ch;
	while( (ch = getopt( argc, argv, "d:f:s:h" )) >= 0) {
		switch( ch ) {
			case 'd':
				ossDev = optarg;
				break;

			case 'f':
				if( (istringstream( optarg ) >> freq).fail() ) throw exception();
				break;

			case 's':
				double sd;
				if( (istringstream( optarg ) >> sd).fail() ) throw exception();
				sigm = sd * 32768.0;
				break;

			case 'h':
				cout << "Usage: brown [-d OSS device] [-f sampling freq.] [-s deviation] [-h]\n";
				return 0;

			default:
				return 0;
		}
	}

	int fd = initOSS( ossDev.c_str(), AFMT_S16_LE, freq, 2 );

	double L = 0, R = 0;
	while( true ) {
		int16_t buf[freq * 2];
		for( int i = 0; i < freq; ++i ) {
			buf[i * 2 + 0] = (int16_t)L;
			buf[i * 2 + 1] = (int16_t)R;

			L = clip<int16_t>( L + sigm * randGauss() );
			R = clip<int16_t>( R + sigm * randGauss() );
		}
		if( write( fd, &buf, sizeof( buf ) ) < 0 ) throw exception();
	}

	return 0;
}

