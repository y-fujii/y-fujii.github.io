# Direct C/C++ code importer for Python
# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import sys
import os
import imp


if os.name == "posix":
	def get_depends(src):
		text = os.popen("c++ -MM " + src, "r").read()
		text = text.replace("\\\n", " ")
		text = text.split(":")[1]
		return text.split()
else:
	def get_depends(src):
		return []
	

def load_cpp(cpp_path):
	(base, _) = os.path.splitext(cpp_path)
	bin_path = compiler.shared_object_filename(base)
	dir_path = os.path.dirname(base)
	name = os.path.basename(base)

	deps = get_depends(cpp_path)
	objs = compiler.compile([cpp_path], depends=deps)
	compiler.link_shared_object(objs, bin_path)
	
	return imp.load_module(name, *imp.find_module(name, [dir_path]))


def import_new(name, *rest):
	mod_path = name.replace(".", os.path.sep)
	for sys_path in ["."] + sys.path:
		path = os.path.join(sys_path, mod_path)
		for ext in compiler.src_extensions:
			if os.path.exists(path + ext):
				return load_cpp(path + ext)

	return import_old(name, *rest)


def __init_compiler():
	from distutils import (ccompiler, sysconfig)

	incs = [
		sysconfig.get_python_inc(),
		os.path.join(sys.prefix, "include"),
	]
	libs = [
		sysconfig.get_python_lib(),
		os.path.join(sys.prefix, "lib"),
	]

	cc = ccompiler.new_compiler()
	sysconfig.customize_compiler(cc)

	for inc in incs:
		cc.add_include_dir(inc)

	for lib in libs:
		cc.add_library_dir(lib)
		cc.add_runtime_library_dir(lib)

	cc.add_library("boost_python-mt")

	return cc


compiler = __init_compiler()
import_old = __builtins__["__import__"]
__builtins__["__import__"] = import_new
