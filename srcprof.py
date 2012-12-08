#!/usr/bin/env python
# -*- coding: CP932 -*-
"""
The source profiler program.

It lists up all files in a directory tree and sum up line counts
for making statistics analysis.
"""

import sys,os,ctypes,codecs
import math
if 3 <= sys.version_info[0]:
	is_v3 = True
	import zipfile
else:
	is_v3 = False
	import zipfile2 as zipfile


# Global settings
ignoredirs = set(['.hg', '.svn', '.git', '.bzr']) # Probably we could ignore all directories beginning with a dot.
extensions = set(['.pl', '.py', '.rb', '.c', '.cpp', '.h', '.rc', '.rci', '.dlg', '.pas', '.dpr', '.cs'])
extstats = {}
verbose = False
listing = True
readzip = True
summary = True
ranking = 10
enable_distrib = True
zipfile_encoding = 'CP932'
enable_html = False
dist_width = 60 # The width of distribution graph

if len(sys.argv) < 2:
	helpstr = "usage: [flags] " + sys.argv[0] + " path\n" +(
	"""
The source profiler program.

It lists up all files in a directory tree and sum up line counts
for making statistics analysis.

The flags can be combination of the following:

    +v      Enable verbose flag
    -v      Disable verbose flag
    +l      Enable listing of processed files.
    -l      Disable listing of processed files.
    +z      Enable reading sources inside zipfiles.
    -z      Disable reading sources inside zipfiles.
    +e ext  Add extension to search criteria
    -e ext  Remove extension from search criteria
    +i dir  Add directory to ignore list
    -i dir  Remove directory from ignore list
    +s      Enable Summary section (default)
    -s      Disable Summary section
    -r n    Enable ranking of file line count for top n files.
            Set n to 0 to disable ranking. (default 10)
    +d      Enable distribution graph (default)
    -d      Disable distribution graph
    -E enc  Set Zipfile entry file encoding to enc. (default CP932)
    +h      Enable HTML output
    -h      Disable HTML output (default)
    -w wid  Set distribution graph width in chars or pixels
            (non-html: default 60; html: default 200)

""")
	helpstr += "Default ignoredirs:\n"
	helpstr += str(ignoredirs) + "\n"
	helpstr += "Default extensions:\n"
	helpstr += str(extensions) + "\n"
	sys.stderr.write(helpstr)
	quit(0)

def vprint(arg):
	if enable_html:
		s = str(arg)
		print((s + '<br>').encode('utf-8'))
	# if it's already an unicode, do not try re-encoding
	elif ((is_v3 and type(arg) == str) or (not is_v3 and type(arg) == unicode)):
		print(arg)
	else:
		print((str(arg).encode('CP932')))

# closure to check count of arguments
def chkopt(i):
	if len(sys.argv) <= i + 1:
		print(("Premature option: " + val + "\n"))
		exit(0)
	i += 1
	return sys.argv[i], i

# The first pass finds if verbose flag is set
i = 1
while i < len(sys.argv):
	arg = sys.argv[i]
	if arg == '+v':
		verbose = True
	elif arg == '-v':
		verbose = False
	i += 1

# The second pass finds if HTML output is set
i = 1
while i < len(sys.argv):
	arg = sys.argv[i]
	if arg == '+h':
		enable_html = True
		dist_width = 300
		if verbose:
			vprint('HTML flag ON')
	elif arg == '-h':
		enable_html = False
		dist_width = 60
		if verbose:
			vprint('HTML flag OFF')
	i += 1

# The third pass interprets rest of the arguments
i = 1
while i < len(sys.argv):
	arg = sys.argv[i]

	# Do not tamper with verbose flag in the second pass
	if arg == '+v':
		pass
	elif arg == '-v':
		pass

	# Specifying listing of processed source files
	elif arg == '+l':
		listing = True
		if verbose:
			vprint('Listing flag ON')
	elif arg == '-l':
		listing = False
		if verbose:
			vprint('Listing flag OFF')

	# Specifying ZIP taget
	elif arg == '+z':
		readzip = True
		if verbose:
			vprint('Read ZIP flag ON')
	elif arg == '-z':
		readzip = False
		if verbose:
			vprint('Read ZIP flag OFF')

	elif arg == '+e':
		value, i = chkopt(i)
		extensions.add(value)
		if verbose:
			vprint('added extension ' + value + ' to target, resulting:')
			vprint(extensions)

	elif arg == '-e':
		value, i = chkopt(i)
		if value in extensions:
			extensions.remove(value)
		if verbose:
			vprint('removed extension ' + value + ' from target, resulting:')
			vprint(extensions)

	elif arg == '+i':
		value, i = chkopt(i)
		ignoredirs.add(value)
		if verbose:
			vprint('added ignoring directory name ' + value + ', resulting:')
			vprint(ignoredirs)

	elif arg == '-i':
		value, i = chkopt(i)
		if value in ignoredirs:
			ignoredirs.remove(value)
		if verbose:
			vprint('removed ignoring directory name ' + value + ', resulting:')
			vprint(ignoredirs)

	elif arg == '+s':
		summary = True
		if verbose:
			vprint('Summary flag ON')

	elif arg == '-s':
		summary = False
		if verbose:
			vprint('Summary flag OFF')

	elif arg == '-r':
		value, i = chkopt(i)
		ranking = int(value)
		if verbose:
			vprint('Set ranking to ' + str(ranking))

	elif arg == '+d':
		enable_distrib = True
		if verbose:
			vprint('Distribution graph flag ON')

	elif arg == '-d':
		enable_distrib = False
		if verbose:
			vprint('Distribution graph flag OFF')

	elif arg == '-w':
		value, i = chkopt(i)
		dist_width = int(value)
		if verbose:
			vprint('Set distribution graph width to ' + str(dist_width))

	elif arg == '-E':
		value, i = chkopt(i)
		zipfile_encoding = value
		if verbose:
			vprint('zipfile_encoding set to ' + zipfile_encoding)

	# HTML argument is already checked
	elif arg == '+h':
		pass
	elif arg == '-h':
		pass

	else:
		if 3 <= sys.version_info[0]:
			path = arg
			if verbose:
				vprint('target path: ' + path)
		else:
			path = arg.decode('CP932')
			if verbose:
				vprint('target path: ' + path.encode('CP932'))

	i += 1


if enable_html:
	print("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>srcprof.py output</title>
</head>
<body>
""")

dirlist = []
i = 0
dircount = 0

class fileentry:
	name = ''
	lines = 0
	size = 0
	def __lt__(self,o):
		return self.name<o.name

filelist = []

class srcstats:
        files = 0
        lines = 0
        size = 0
        def tostring(self):
                return ('files = ' + str(self.files) +
                        ', lines = ' + str(self.lines) +
                        ', size = ' + str(self.size))

        def tohtml(self):
        	return ('<td>' + str(self.files) + '</td>' +
        		'<td>' + str(self.lines) + '</td>' +
        		'<td>' + str(self.size) + '</td>')

        @staticmethod
        def htmlheader():
        	return ('<th>file</th>' +
        		'<th>lines</th>' +
        		'<th>size</th>')

class filer:
	def open(self, root, f):
		return null
	def getsize(self, root, f):
		return 0

class deffiler(filer):
	def open(self, root, f):
		if 3 <= sys.version_info[0]:
			return open(os.path.join(root, f), encoding='latin-1')
		else:
			return open(os.path.join(root, f))
	def getsize(self, root, f):
		return os.path.getsize(os.path.join(root, f))

class zipfiler(filer):
	zf = None
	def __init__(self, zf):
		self.zf = zf
	def open(self, root, f):
		return self.zf.open(f)
	def getsize(self, root, f):
		return self.zf.getinfo(f).file_size


def process_file_list(root, files, filer):
	for f in files:
		ext = os.path.splitext(f)[1].lower()

		matched = False
		for srcext in extensions:
                        if srcext == ext:
                        	matched = True
		if not matched: continue

		# os.path.join fails with corrupted strings
#		print(os.path.join(root, f))
		if root[-1] == '/' or root[-1] == '\\':
			filepath = root + f
		else:
			filepath = root + os.sep + f
		fp = filer.open(root, f)
		linecount = 0
		for line in fp:
			linecount += 1

		filesize = filer.getsize(root, f)

		if listing:
			if enable_html:
				print(('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format(len(filelist), linecount, filesize, filepath.encode('utf-8'))))
			else:
				print(('{0}\t{1:5}\t{2}'.format(len(filelist) + 1, linecount, filepath.encode('CP932'))))

		fe = fileentry()
		fe.name = filepath
		fe.lines = linecount
		fe.size = filesize
		filelist.append((linecount, fe))
		fp.close()

		if not ext in extstats:
			extstats[ext] = srcstats()
		extstats[ext].lines += linecount
		extstats[ext].files += 1
		extstats[ext].size += filer.getsize(root, f)
	return

if listing:
	if enable_html:
		print(b"<h1>File list in \"" + path.encode('UTF-8') + b"\"</h1>")
		print('<table border="1" cellspacing="0" cellpadding="1">')
		print("<tr><th>No.</th><th>lines</th><th>size</th><th>name</th></tr>")
	else:
		print(("Profiling files in \"" + path + "\"...\n"))
		print("No.\tlines\tname\n")


for root, dirs, files in os.walk(path):
	dirlist.append((len(files), root))
	dircount += len(files)

	for dir in ignoredirs:
		if dir in dirs:
			vprint("skipping " + os.path.join(root, dir))
			dirs.remove(dir)

	for f in files:
		ext = os.path.splitext(f)[1].lower()
		filepath = os.path.join(root, f)
		if readzip and ext.lower() == '.zip' and zipfile.is_zipfile(filepath):
			try:
				zf = zipfile.ZipFile(filepath)
				process_file_list(filepath, zf.namelist(), zipfiler(zf))
			except:
				print(("exception in file ", filepath))
				raise

	process_file_list(root, files, deffiler())

def zipenter(path, filter = ''):
	if zipfile.is_zipfile(path):
		if verbose:
			vprint('filter="{0}"'.format(filter))
		zf = zipfile.ZipFile(path, fileencoding = zipfile_encoding)
		nl = []
		for f in zf.infolist():
			if verbose:
				vprint('flag_bits = ' + str(f.flag_bits) + ', filename = ' + f.filename)
			if f.filename.startswith(filter):
				matched = False
				for id in ignoredirs:
					if 0 <= f.filename.find(id):
						matched = True
						break
				if matched:
					continue
				nl.append(f.filename)
				if verbose:
					vprint(f.filename)
		return process_file_list(path, nl, zipfiler(zf))
	elif verbose:
		vprint(path + ' is not a zipfile')
	return 0

i += zipenter(path)
path = path.replace('\\', '/')
splitpath = path.split('/')
uppath = ''
while 0 < path.rfind('/'):
#	print '1 path', path
	slashpos = path.rfind('/')
	if slashpos == len(path)-1:
		path = path[0:slashpos]
	else:
		uppath = path[slashpos+1:] + '/' + uppath
		path = path[0:slashpos]
#		print '2 path="{0}", uppath="{1}", {2}, {3}'.format(path, uppath, slashpos, len(path))
		zipenter(path, uppath.replace('\\', '/'))

if listing and enable_html:
	print("</table><hr>")



if summary:
	if enable_html:
		print("<h1>Summary</h1>")
		print('<table border="1" cellspacing="0" cellpadding="1">')
		print(("<tr><th>extension</th>" + srcstats.htmlheader() + "</tr>"))
	else:
		print("""
--------------------------
         Summary
--------------------------
""")

	extsum = srcstats()
	for ext,l in list(extstats.items()):
		if enable_html:
			print(("<tr><td>" + ext + '</td>' + l.tohtml() + "</tr>"))
		else:
			print((ext + ': ' + l.tostring()))
		extsum.files += l.files
		extsum.lines += l.lines
		extsum.size += l.size

	if enable_html:
		print(('<tr><td>total</td>' + extsum.tohtml() + '</tr>'))
	else:
		print(('total: ' + extsum.tostring()))

	if enable_html:
		print("</table><hr>")



if 0 < ranking:
	if enable_html:
		print(("<h1>Top {0} files</h1>".format(ranking)))
		print('<table border="1" cellspacing="0" cellpadding="1">')
		print("<tr><th>No.</th><th>lines</th><th>size</th><th>name</th></tr>")
	else:
		print(("""
--------------------------
      Top {0} files
--------------------------
""".format(ranking)))

	filelist.sort(reverse = 1)
	i = 0
	for key,fe in filelist:
		i += 1
		if key == 0 or ranking <= i:
			break
		if enable_html:
			print(("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(
				i, str(key), fe.size, fe.name.encode('utf-8'))))
		else:
			print((str(key) + ": " + fe.name))

	if enable_html:
		print("</table><hr>")

"""
print("total directories: " + str(i) + ", files: " + str(dircount))
print("sorting order by file count")

dirlist.sort(reverse = 1)
i = 0

for key,s in dirlist:
	i += 1
	if key == 0 or 80 <= i:
		break
	print(str(key) + ": " + s)
"""

if enable_distrib:
	cell = 1
	base = math.sqrt(2)
	distrib = list(range(31))
	for i in distrib:
		distrib[i] = 0
	for key,s in filelist:
	        if key == 0: continue
	        find = math.log(key, base)
	        ind = int(max(0,math.ceil(find)))
	        if ind < len(distrib):
	        	distrib[ind] += 1

	maxdirs = 1
	for v in distrib[1:]:
		if maxdirs < v:
			maxdirs = v
	maxdirs = math.log(maxdirs)+1

	if enable_html:
		print("<h1>Distribution</h1>")
		print('<table border="1" cellspacing="0" cellpadding="1">')
	else:
		print ("""
--------------------------
      Distribution
--------------------------
""")

	for i in range(2,len(distrib)):
		s = ""
		if enable_html:
			print(('''<tr><td align="right">{0:5}-{1:5} {2:3}</td>
<td><div style="background-color:#{4:02x}007f;width:{3}px;">&nbsp;</div></td></tr>'''.format(
				int(pow(base, ((i - 1) * cell))),
				int(pow(base, ((i) * cell))) - 1,
				str(distrib[i]),
				(int((math.log(distrib[i])+1) * dist_width / maxdirs)) if distrib[i] != 0 else 0,
				int(i * 255 / len(distrib)))))
		else:
			if 0 < maxdirs and i != 0 and distrib[i] != 0:
				for j in range(int((math.log(distrib[i])+1) * dist_width / maxdirs)):
					s += "*"

			print(("{0:5}-{1:5} {2:3}".format(
		                int(pow(base, ((i - 1) * cell))),
		                int(pow(base, ((i) * cell))) - 1,
		                str(distrib[i])) + ":" + s))

	if enable_html:
		print("</table>")

if enable_html:
	print("""
</body>
</html>
""")

