/*
 * Async-signal-safe implementation of closefrom() for Linux
 * by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain
 */

#define _GNU_SOURCE
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/syscall.h>


typedef struct linux_dirent {
	unsigned long d_ino;
	unsigned long d_off;
	uint16_t      d_reclen;
	char          d_name[1];
} linux_dirent;

static void closefrom_fallback( int lowfd ) {
	int fd, maxfd = sysconf( _SC_OPEN_MAX );
	for( fd = lowfd; fd < maxfd; ++fd ) {
		close( fd );
	}
}

void closefrom( int lowfd ) {
	int dfd = open( "/proc/self/fd", O_RDONLY | O_DIRECTORY );
	if( dfd < 0 ) {
		return closefrom_fallback( lowfd );
	}

	while( 1 ) {
		uint8_t buf[PIPE_BUF];
		int n = syscall( SYS_getdents, dfd, buf, PIPE_BUF );
		if( n <= 0 ) {
			break;
		}

		int offset = 0;
		while( offset < n ) {
			linux_dirent* entry = (linux_dirent*)( buf + offset );
			uint8_t d_type = buf[offset + entry->d_reclen - 1];

			if( d_type != DT_DIR ) {
				int fd = 0;
				char* it = entry->d_name;
				while( '0' <= *it && *it <= '9' ) {
					fd = fd * 10 + (*it - '0');
					++it;
				}
				if( it == entry->d_name || *it != '\0' ) {
					close( dfd );
					return closefrom_fallback( lowfd );
				}

				if( fd >= lowfd && fd != dfd ) {
					close( fd );
				}
			}

			offset += entry->d_reclen;
		}
	}

	close( dfd );
}
