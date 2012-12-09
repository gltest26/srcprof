
Overview
========

srcprof is a very simple source tree profiling (statistics analyzing tool) run on a command line.


Installation
----------------

This program consists of just two Python sources, just copy them on any directory of your liking.


Usage
----------------

The program is simple Python script, which can run on any platform with Python environment available.

Just type `srcprof.py` or `python srcprof.py` to get command line help.


Output data
----------------

It outputs file count, line count and total size of each source file type distinguished by extension (or suffix).

It also prints files with largest line counts, which can help finding most complex files in the source tree.

It can print source file distribution graph (with simple ASCII art), which implies how well the project is divided into modules.

For example, running this program on git source distribution yields following output.

	--------------------------
	         Summary
	--------------------------

	.h: files = 133, lines = 17030, size = 554683
	.pl: files = 10, lines = 1444, size = 43388
	.c: files = 330, lines = 162512, size = 4179957
	.py: files = 16, lines = 5746, size = 199291
	total: files = 489, lines = 186732, size = 4977319

	--------------------------
	      Top 10 files
	--------------------------

	5750: h:\extprojs\git\compat\nedmalloc\malloc.c.h
	4931: h:\extprojs\git\diff.c
	4454: h:\extprojs\git\builtin\apply.c
	4369: h:\extprojs\git\compat\regex\regexec.c
	3884: h:\extprojs\git\compat\regex\regcomp.c
	3461: h:\extprojs\git\fast-import.c
	3242: h:\extprojs\git\git-p4.py
	2837: h:\extprojs\git\sha1_file.c
	2643: h:\extprojs\git\builtin\blame.c

	--------------------------
	      Distribution
	--------------------------

	    1-    1 0  :
	    2-    1 0  :
	    2-    3 0  :
	    4-    4 0  :
	    5-    7 8  :**************************************
	    8-   10 13 :********************************************
	   11-   15 13 :********************************************
	   16-   21 24 :****************************************************
	   22-   31 33 :********************************************************
	   32-   44 28 :******************************************************
	   45-   63 34 :*********************************************************
	   64-   89 43 :************************************************************
	   90-  127 37 :**********************************************************
	  128-  180 38 :**********************************************************
	  181-  255 37 :**********************************************************
	  256-  361 43 :************************************************************
	  362-  511 33 :********************************************************
	  512-  723 28 :******************************************************
	  724- 1023 23 :****************************************************
	 1024- 1447 20 :**************************************************
	 1448- 2047 15 :**********************************************
	 2048- 2895 6  :***********************************
	 2896- 4095 3  :**************************
	 4096- 5791 4  :******************************
	 5792- 8191 0  :
	 8192-11584 0  :
	11585-16383 0  :
	16384-23169 0  :
	23170-32767 0  :



Options
--------------

The program has some option switches. The list of available options is viewed by running the program without arguments.

	usage: srcprof.py [flags] path

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
	    -f enc  Set file path's character encoding. (default ascii)
	            Setting this should only be necessary in Python 2.*.
	    -c enc  Set file content's character encoding. Necessary to
	            count up lines correctly. (default latin-1)

	Default ignoredirs:
	set(['.bzr', '.hg', '.git', '.svn'])
	Default extensions:
	set(['.h', '.pl', '.cs', '.rc', '.rb', '.c', '.rci', '.dlg', '.py', '.cpp', '.dp
	r', '.pas'])


Origin
------------

During certain project development, I just wondered which source file is the most complex one in the whole project (thus probably be worth refactoring). I also wanted to know the trend of the whole project.
Instead of searching for countless statistical analysis tools, I just wrote one I needed.
